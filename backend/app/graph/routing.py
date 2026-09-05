"""
LangGraph routing logic - determines next node based on state.
"""
import json
from app.agents.state import AgentState
from app.utils.logging import logger


def should_use_rag(state: AgentState) -> str:
    """Determine if we should use RAG based on the last tool results."""
    tool_results = state.get("tool_results", [])
    if not tool_results:
        # No tools were called - likely a general question, use RAG
        return "rag"
    return "continue"


def route_after_agent(state: AgentState) -> str:
    """Route after the agent node - determine next action."""
    messages = state.get("messages", [])
    if not messages:
        return "end"

    last_msg = messages[-1]
    
    # If agent called tools, go to tool execution
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"

    # If agent just responded with text, go to output guardrails then end
    return "output_guardrails"


def route_after_tools(state: AgentState) -> str:
    """Route after tool execution.

    Reads state that was set by ``tool_execution_node`` (refund proposals
    set ``pending_action`` and ``risk_level`` there).
    """
    risk_level = state.get("risk_level", "safe")
    pending_action = state.get("pending_action")

    # If a refund proposal was detected (set by tool_execution_node),
    # route through risk evaluation → human approval
    if pending_action and risk_level == "risky":
        return "risk_evaluation"

    # Check if the refund was rejected by business rules
    tool_results = state.get("tool_results", [])
    for tr in tool_results:
        result_str = tr.get("result", "{}")
        try:
            result = json.loads(result_str) if isinstance(result_str, str) else result_str
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(result, dict) and result.get("action") == "refund_rejected":
            return "agent"  # Let agent explain rejection

    # Default: go back to agent for response generation
    return "agent"


def route_risk_evaluation(state: AgentState) -> str:
    """Route based on risk level."""
    risk = state.get("risk_level", "safe")
    if risk == "risky":
        return "human_approval"
    return "execute_action"