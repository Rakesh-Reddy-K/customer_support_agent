"""
LangGraph nodes - the building blocks of the agent workflow.
"""
import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT, RAG_SYSTEM_PROMPT
from app.config.settings import settings
from app.tools.order_tools import lookup_order, lookup_order_with_auth, list_customer_orders, track_shipment, check_refund_eligibility
from app.tools.customer_tools import get_customer_info
from app.tools.refund_tools import request_refund_proposal, execute_approved_refund
from app.tools.shipping_tools import get_shipping_status
from app.tools.support_tools import create_support_ticket, get_customer_tickets
from app.rag.retriever import get_retriever
from app.utils.logging import logger


def get_llm():
    """Get the LLM instance based on the configured provider.

    Provider is selected via the LLM_PROVIDER env var:
      ollama  -> ChatOllama  (requires OLLAMA_BASE_URL, OLLAMA_MODEL)
      openai  -> ChatOpenAI  (requires OPENAI_API_KEY, MODEL_NAME)
    """
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.model_temperature,
        )

    # Default to OpenAI-compatible API
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.model_name,
        temperature=settings.model_temperature,
        api_key=settings.openai_api_key,
    )


# All tools available to the agent
ALL_TOOLS = [
    lookup_order, lookup_order_with_auth, list_customer_orders,
    track_shipment, check_refund_eligibility, get_customer_info,
    get_shipping_status, request_refund_proposal, execute_approved_refund,
    create_support_ticket, get_customer_tickets,
]


def get_agent_with_tools():
    """Get LLM bound to tools."""
    llm = get_llm()
    return llm.bind_tools(ALL_TOOLS)


async def input_guardrails_node(state: AgentState) -> dict:
    """Input guardrails - check for prompt injection and PII."""
    from app.guardrails.input_guardrails import check_input
    messages = state["messages"]
    if not messages:
        return {"messages": messages}

    last_msg = messages[-1]
    if hasattr(last_msg, "content") and last_msg.content:
        is_safe, sanitized, reason = await check_input(last_msg.content)
        if not is_safe:
            return {
                "messages": messages + [
                    AIMessage(content="I'm sorry, but I can't process that request. Please ask a question about your orders, shipments, or TechKart services.")
                ]
            }
        if sanitized != last_msg.content:
            messages = list(messages)
            messages[-1] = HumanMessage(content=sanitized)
    return {"messages": messages}


async def agent_node(state: AgentState) -> dict:
    """Main agent node - calls the LLM with tools."""
    customer_id = state.get("customer_id", "CUS1001")
    system_prompt = SYSTEM_PROMPT.format(customer_id=customer_id)

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    agent = get_agent_with_tools()
    try:
        response = await agent.ainvoke(messages)
        logger.info("Agent response generated", extra={"customer_id": customer_id})
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {
            "messages": [AIMessage(
                content="I apologize, but I'm experiencing a technical issue. Please try again or contact our support team."
            )]
        }


async def rag_node(state: AgentState) -> dict:
    """RAG node - retrieves relevant policy documents and generates response."""
    if not state["messages"]:
        return {"messages": []}

    last_msg = state["messages"][-1]
    query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)

        context = "\n\n".join([d.page_content for d in docs])

        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=RAG_SYSTEM_PROMPT.format(context=context, question=query))
        ])

        doc_sources = [{"title": d.metadata.get("title", ""), "source": d.metadata.get("source", "")} for d in docs]
        return {
            "messages": [response],
            "retrieved_documents": doc_sources,
        }
    except Exception as e:
        logger.error(f"RAG error: {e}")
        return {
            "messages": [AIMessage(content="I apologize, but I couldn't find relevant policy information. Let me connect you with a support agent.")],
        }


async def tool_execution_node(state: AgentState) -> dict:
    """Execute tools called by the agent."""
    from langchain_core.messages import ToolMessage
    messages = state["messages"]
    if not messages:
        return {"messages": []}

    last_msg = messages[-1]
    if not hasattr(last_msg, "tool_calls") or not last_msg.tool_calls:
        return {"tool_results": []}

    tool_map = {t.name: t for t in ALL_TOOLS}
    tool_results = []
    new_messages = []

    for tc in last_msg.tool_calls:
        tool_name = tc["name"]
        tool_args = tc["args"]
        if tool_name in tool_map:
            try:
                result = await tool_map[tool_name].ainvoke(tool_args)
                tool_results.append({"tool": tool_name, "args": tool_args, "result": result})
                new_messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                new_messages.append(ToolMessage(content=error_msg, tool_call_id=tc["id"]))
                tool_results.append({"tool": tool_name, "error": str(e)})

    # Detect refund proposals in tool results and set state accordingly
    # (LangGraph routing functions receive read-only state snapshots,
    #  so mutations must happen in nodes, not routers)
    update: dict = {"messages": new_messages, "tool_results": tool_results}

    for tr in tool_results:
        result_str = tr.get("result", "{}")
        try:
            result = json.loads(result_str) if isinstance(result_str, str) else result_str
        except (json.JSONDecodeError, TypeError):
            continue

        if isinstance(result, dict):
            if result.get("action") == "refund_proposed":
                update["pending_action"] = result
                update["risk_level"] = "risky"
                break
            if result.get("action") == "refund_rejected":
                # Business rules rejected the refund; agent will explain
                break

    return update