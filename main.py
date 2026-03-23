"""FastAPI application for KnowYourStock."""

import asyncio
import json
import traceback
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import GEMINI_LLM, logger
from models import (
    LanggraphRequest,
    ChatRequest,
    StockCompareRequest,
)
from workflows import workflow, chat_workflow

app = FastAPI(
    title="KnowYourStock API",
    description="Financial analysis API powered by LangGraph and Gemini",
    version="2.0.0",
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Simple in-memory cache for stock analysis results
# ---------------------------------------------------------------------------
_stock_cache: Dict[str, Any] = {}
_CACHE_MAX = 50


def _cache_key(name: str) -> str:
    return name.strip().lower()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to KnowYourStock API v2"}


@app.post("/langgraph")
async def run_langgraph(req: LanggraphRequest):
    """Run the stock-analysis workflow (with caching)."""
    try:
        state_input: dict = {}
        if req.stock_name:
            state_input["User_stock_name"] = req.stock_name

            # Check cache
            key = _cache_key(req.stock_name)
            if key in _stock_cache:
                logger.info("Cache hit for '%s'", req.stock_name)
                return {"status": "ok", "result": _stock_cache[key], "cached": True}

        result_state = await workflow.ainvoke(state_input)

        # Store in cache
        if req.stock_name:
            if len(_stock_cache) >= _CACHE_MAX:
                _stock_cache.pop(next(iter(_stock_cache)))
            _stock_cache[_cache_key(req.stock_name)] = result_state

        return {"status": "ok", "result": result_state}
    except Exception as e:
        logger.error("langgraph error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/compare")
async def compare_stocks(req: StockCompareRequest):
    """Compare multiple stocks side-by-side by running the workflow for each."""
    try:
        tasks = []
        for name in req.stock_names:
            key = _cache_key(name)
            if key in _stock_cache:
                tasks.append(asyncio.coroutine(lambda c=_stock_cache[key]: c)())
            else:
                tasks.append(workflow.ainvoke({"User_stock_name": name}))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        comparison = []
        for name, result in zip(req.stock_names, results):
            if isinstance(result, Exception):
                comparison.append({"stock_name": name, "error": str(result)})
            else:
                # Cache successful results
                key = _cache_key(name)
                if key not in _stock_cache:
                    if len(_stock_cache) >= _CACHE_MAX:
                        _stock_cache.pop(next(iter(_stock_cache)))
                    _stock_cache[key] = result
                comparison.append({"stock_name": name, "data": result})

        return {"status": "ok", "comparison": comparison}
    except Exception as e:
        logger.error("compare error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/chat")
async def chatting(req: ChatRequest):
    """Chat endpoint using LangGraph chat workflow."""
    try:
        state_input = {
            "current_message": req.message,
            "context": req.context,
            "messages": req.messages if req.messages else [],
        }
        result_state = chat_workflow.invoke(state_input)
        return {
            "status": "ok",
            "response": result_state.get("response", "No response generated"),
            "messages": result_state.get("messages", []),
        }
    except Exception as e:
        logger.error("chat error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/chat/stream")
async def chatting_stream(req: ChatRequest):
    """Streaming chat endpoint returning Server-Sent Events."""

    async def generate_stream():
        try:
            messages_history = req.messages or []
            recent_messages = messages_history[-4:] if len(messages_history) > 4 else messages_history

            system_prompt = (
                "You are a helpful financial assistant with expertise in stock market analysis, "
                "company information, and financial news. Provide accurate, informative, and concise responses.\n\n"
                "If the user asks about a specific stock, use the provided context to give detailed answers."
            )

            if req.context:
                stock_name = req.context.get("User_stock_name", "")
                ticker = req.context.get("Stock_Ticker", "")
                if stock_name:
                    system_prompt += f"\n\nUser is asking about: {stock_name}"
                    if ticker:
                        system_prompt += f" (Ticker: {ticker})"

            messages = [SystemMessage(content=system_prompt)]
            for msg in recent_messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            messages.append(HumanMessage(content=req.message))

            response_parts = []
            async for chunk in GEMINI_LLM.astream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    response_parts.append(chunk.content)
                    yield f"data: {json.dumps({'status': 'chunk', 'content': chunk.content})}\n\n"

            full_response = "".join(response_parts)
            updated_messages = messages_history + [
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": full_response},
            ]
            if len(updated_messages) > 4:
                updated_messages = updated_messages[-4:]

            yield f"data: {json.dumps({'status': 'done', 'messages': updated_messages})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.delete("/cache")
def clear_cache():
    """Clear the in-memory stock analysis cache."""
    _stock_cache.clear()
    return {"status": "ok", "message": "Cache cleared"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
