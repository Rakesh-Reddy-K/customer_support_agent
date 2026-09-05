"""
LangGraph workflow - main agent graph with HITL support.
"""
import json
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import AgentState
from app.graph.nodes import (
    input_guardrails_node, agent_node, rag_node, tool_execution_node,
)
from app.graph.routing import route_after_agent, route_after_tools, route_risk_evaluation
from app.database.database import db_manager
from app.utils.logging import logger

checkpointer = MemorySaver()


async def risk_evaluation_node(state: AgentState) -> dict:
    """Evaluate risk of the proposed action."""
    pending = state.get("pending_action")
    if not pending:
        return {"risk_level": "safe"}
    if pending.get("action") == "refund_proposed":
        return {"risk_level": "risky"}
    return {"risk_level": "safe"}


async def human_approval_node(state: AgentState) -> dict:
    """Pause for human approval and create approval record."""
    pending = state.get("pending_action", {})
    thread_id = state.get("thread_id", "unknown")
    customer_id = state.get("customer_id", "CUS1001")
    if not pending:
        return {"pending_action": None}
    try:
        async with db_manager.session() as session:
            from app.services.approval_service import create_approval
            from app.database import ApprovalActionType
            await create_approval(session, {
                "thread_id": thread_id, "customer_id": customer_id,
                "order_id": pending.get("order_id"), "action_type": ApprovalActionType.REFUND,
                "requested_amount": pending.get("amount"),
                "requested_reason": pending.get("reason"),
                "ai_reasoning_summary": pending.get("ai_reasoning_summary", ""),
            })
        logger.info(f"Approval created for thread {thread_id}")
    except Exception as e:
        logger.error(f"Error creating approval: {e}")
    amt = pending.get("amount", 0)
    oid = pending.get("order_id", "unknown")
    msg = (f"⏳ Your refund request for order {oid} (₹{amt:,.0f}) "
           f"has been submitted and is awaiting review by our support team.")
    return {"messages": [AIMessage(content=msg)], "pending_action": pending}


async def execute_action_node(state: AgentState) -> dict:
    """Execute the approved action."""
    pending = state.get("pending_action")
    human_decision = state.get("human_decision")
    thread_id = state.get("thread_id", "unknown")
    if not pending:
        return {"messages": []}
    action = pending.get("action", "")
    if action == "refund_proposed":
        decision = human_decision.get("decision") if human_decision else None
        if decision == "approve":
            from app.services.refund_service import process_refund
            from app.services.approval_service import mark_executed
            amount = pending.get("amount", 0)
            order_id = pending.get("order_id", "")
            try:
                async with db_manager.session() as session:
                    result = await process_refund(session, order_id, amount, pending.get("reason", ""), "SUPPORT_AGENT")
                    if result.get("success"):
                        await mark_executed(session, thread_id, json.dumps(result))
                        msg = (f"✅ Your refund of ₹{amount:,.0f} for order {order_id} "
                               f"has been processed. Refund will be credited in 5-7 business days.")
                    else:
                        msg = f"❌ Unable to process refund: {result.get('error', 'Unknown error')}"
            except Exception as e:
                msg = "❌ Error processing refund."
            return {"messages": [AIMessage(content=msg)]}
        elif decision == "reject":
            reason = human_decision.get("notes", "Request not approved.")
            return {"messages": [AIMessage(content=f"Your refund request was not approved. Reason: {reason}")]}
        elif decision == "edit":
            from app.services.refund_service import process_refund
            from app.services.approval_service import mark_executed
            amount = human_decision.get("edited_amount", pending.get("amount"))
            order_id = pending.get("order_id", "")
            try:
                async with db_manager.session() as session:
                    result = await process_refund(session, order_id, amount, human_decision.get("edited_reason", ""), "SUPPORT_AGENT")
                    if result.get("success"):
                        await mark_executed(session, thread_id, json.dumps(result))
                        msg = f"✅ Your refund of ₹{amount:,.0f} for order {order_id} has been processed (edited amount)."
                    else:
                        msg = f"❌ Unable to process refund: {result.get('error')}"
            except Exception:
                msg = "❌ Error processing refund."
            return {"messages": [AIMessage(content=msg)]}
    return {"messages": [AIMessage(content="Action completed.")]}


async def output_guardrails_node(state: AgentState) -> dict:
    """Output guardrails - validate the AI response."""
    from app.guardrails.output_guardrails import validate_output
    messages = state.get("messages", [])
    if not messages:
        return {"risk_level": "safe"}
    last_msg = messages[-1]
    if hasattr(last_msg, "content"):
        is_safe, reason = await validate_output(last_msg.content)
        if not is_safe:
            return {"messages": messages[:-1] + [
                AIMessage(content="I apologize, but I cannot provide that information. How else can I help you?")
            ]}
    return {"risk_level": "safe"}


def build_graph():
    """Build the LangGraph workflow."""
    graph = StateGraph(AgentState)
    graph.add_node("input_guardrails", input_guardrails_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_execution_node)
    graph.add_node("rag", rag_node)
    graph.add_node("risk_evaluation", risk_evaluation_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("execute_action", execute_action_node)
    graph.add_node("output_guardrails", output_guardrails_node)

    graph.set_entry_point("input_guardrails")
    graph.add_edge("input_guardrails", "agent")
    graph.add_conditional_edges("agent", route_after_agent,
                                {"tools": "tools", "rag": "rag", "output_guardrails": "output_guardrails"})
    graph.add_conditional_edges("tools", route_after_tools,
                                {"agent": "agent", "risk_evaluation": "risk_evaluation"})
    graph.add_conditional_edges("risk_evaluation", route_risk_evaluation,
                                {"human_approval": "human_approval", "execute_action": "execute_action"})
    graph.add_edge("human_approval", END)
    graph.add_edge("execute_action", END)
    graph.add_edge("rag", "output_guardrails")
    graph.add_edge("output_guardrails", END)
    return graph.compile(checkpointer=checkpointer)


compiled_graph = None


def get_compiled_graph():
    global compiled_graph
    if compiled_graph is None:
        compiled_graph = build_graph()
    return compiled_graph