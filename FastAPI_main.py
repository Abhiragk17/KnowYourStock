from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
import importlib
import traceback
import sys
import json
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Langgraph.workflow import workflow
from Langgraph.chat_workflow import chat_workflow
from Models import ChatState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

app = FastAPI(title="Finance Tweet Assistant API")


class LanggraphRequest(BaseModel):
    stock_name: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    messages: Optional[List[Dict[str, str]]] = None  # Previous conversation history (role/content dicts)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def HelloWorld():
    return {"message": "Hello! Welcome"}

@app.post("/langgraph")
async def run_langgraph(req: LanggraphRequest):
    """Run the simple workflow:

    START -> ScreenerURL_node -> [News_node, ScreenerExtract_node, StockInfo_node] -> END

    Behavior:
    - If `stock_name` provided, resolves screener URL + ticker via tools.ScreenerURL_tool
    - Calls News, ScreenerExtract, and StockInfo tool functions and returns aggregated result.
    """
    try:
        state_input = {}
        if req.stock_name:
            state_input["User_stock_name"] = req.stock_name

        result_state = await workflow.ainvoke(state_input)
        return {"status": "ok", "result": result_state}
    except Exception as e:
        tb = traceback.format_exc()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": tb})

@app.post("/chat")
async def chatting(req: ChatRequest):
    """Chat endpoint using LangGraph chat workflow with streaming support.
    
    Uses memory to retain last 2 conversation pairs and includes optional stock context.
    """
    try:
        # Prepare the chat state with existing messages if provided
        state_input = {
            "current_message": req.message,
            "context": req.context,
            "messages": req.messages if req.messages else []  # Use provided messages (role/content dicts) or empty list
        }
        
        # Run the chat workflow
        result_state = chat_workflow.invoke(state_input)
        
        # Extract response and updated messages
        response_text = result_state.get("response", "No response generated")
        updated_messages = result_state.get("messages", [])
        
        return {
            "status": "ok", 
            "response": response_text,
            "messages": updated_messages  # Return updated message history
        }
    except Exception as e:
        tb = traceback.format_exc()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": tb})


@app.post("/chat/stream")
async def chatting_stream(req: ChatRequest):
    """Streaming chat endpoint using LangGraph chat workflow.
    
    Returns Server-Sent Events (SSE) stream for real-time response streaming.
    Uses LangChain streaming capabilities for token-by-token streaming.
    """
    from langchain_core.callbacks import AsyncCallbackHandler
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from config import GEMINI_LLM
    
    class StreamHandler(AsyncCallbackHandler):
        def __init__(self):
            self.tokens = []
            self.queue = asyncio.Queue()
        
        async def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.tokens.append(token)
            await self.queue.put(token)
        
        async def aiter(self):
            while True:
                try:
                    token = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                    yield token
                except asyncio.TimeoutError:
                    break
    
    async def generate_stream():
        try:
            # Prepare chat state
            messages_history = req.messages if req.messages else []
            recent_messages = messages_history[-4:] if len(messages_history) > 4 else messages_history
            
            # Build system prompt with context (similar to chat_node)
            system_prompt = """You are a helpful financial assistant with expertise in stock market analysis, 
    company information, and financial news. Provide accurate, informative, and concise responses.

    If the user asks about a specific stock, use the provided context about that stock to give detailed answers.
    Be professional and helpful in your responses."""
            
            if req.context:
                stock_name = req.context.get("User_stock_name", "")
                ticker = req.context.get("Stock_Ticker", "")
                if stock_name:
                    system_prompt += f"\n\nUser is asking about: {stock_name}"
                    if ticker:
                        system_prompt += f" (Ticker: {ticker})"
            
            # Build message list
            messages = [SystemMessage(content=system_prompt)]
            for msg in recent_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            messages.append(HumanMessage(content=req.message))
            
            # Stream LLM response
            stream_handler = StreamHandler()
            response_parts = []
            
            # Stream the response
            async for chunk in GEMINI_LLM.astream(
                messages,
                callbacks=[stream_handler]
            ):
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    response_parts.append(content)
                    yield f"data: {json.dumps({'status': 'chunk', 'content': content})}\n\n"
            
            # Combine response parts
            full_response = "".join(response_parts)
            
            # Update messages (keep only last 2 pairs)
            updated_messages = messages_history + [
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": full_response}
            ]
            if len(updated_messages) > 4:
                updated_messages = updated_messages[-4:]
            
            # Yield completion
            yield f"data: {json.dumps({'status': 'done', 'messages': updated_messages})}\n\n"
                
        except Exception as e:
            error_msg = {"status": "error", "error": str(e)}
            yield f"data: {json.dumps(error_msg)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    # Run via: python FastAPI_main.py (for quick local tests)
    import uvicorn

    uvicorn.run("FastAPI_main:app", host="0.0.0.0", port=8000, reload=False)
