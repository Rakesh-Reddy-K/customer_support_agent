"""
Chat API endpoint - main interaction point for the AI agent.
"""
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.graph.workflow import get_compiled_graph
from app.utils.logging import logger


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customer_id: str = "CUS1001"
    thread_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    customer_id: str
    pending_approval: dict | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the AI customer support agent."""
    thread_id = request.thread_id or f"thread-{uuid.uuid4().hex[:8]}"
    
    try:
        graph = get_compiled_graph()
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "customer_id": request.customer_id,
            "thread_id": thread_id,
            "current_intent": None,
            "retrieved_documents": [],
            "tool_results": [],
            "pending_action": None,
            "human_decision": None,
            "summary": None,
            "risk_level": "safe",
            "response": None,
        }

        config = {"configurable": {"thread_id": thread_id}}
        result = await graph.ainvoke(initial_state, config)

        # Extract last AI message
        messages = result.get("messages", [])
        ai_response = "I apologize, but I couldn't generate a response. Please try again."
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                ai_response = msg.content
                break

        pending = result.get("pending_action")
        return ChatResponse(
            response=ai_response,
            thread_id=thread_id,
            customer_id=request.customer_id,
            pending_approval=pending,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")