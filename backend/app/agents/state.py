"""
LangGraph agent state definition.
"""
from typing import TypedDict, Annotated, Any
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for the TechKart customer support agent."""
    messages: Annotated[list, add_messages]
    customer_id: str
    thread_id: str
    current_intent: str | None
    retrieved_documents: list[dict]
    tool_results: list[dict]
    pending_action: dict | None
    human_decision: dict | None
    summary: str | None
    risk_level: str  # "safe" or "risky"
    response: str | None