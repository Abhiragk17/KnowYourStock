"""Node that handles chat interactions with financial context."""

from typing import List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from config import GEMINI_LLM as llm, logger
from models import ChatState

_SYSTEM_PROMPT = (
    "You are a helpful financial assistant with expertise in stock market analysis, "
    "company information, and financial news. Provide accurate, informative, and concise responses.\n\n"
    "If the user asks about a specific stock, use the provided context about that stock to give detailed answers. "
    "Be professional and helpful in your responses."
)


def _format_recent_messages(recent_messages: List[BaseMessage]) -> str:
    formatted = "<Chat History>\n"
    for msg in recent_messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        formatted += f"{role}: {msg.content}\n"
    formatted += "</Chat History>\n"
    return formatted


def chat_node(state: ChatState) -> ChatState:
    try:
        system_prompt = _SYSTEM_PROMPT

        # Add stock context if available
        if state.context:
            ticker = state.context.get("TickerSymbol", "")
            if ticker:
                system_prompt += f"\n\nStock: {ticker}"

        recent_messages = state.messages[-5:] if len(state.messages) > 5 else state.messages

        llm_messages: List[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=_format_recent_messages(recent_messages)),
        ]

        response = llm.invoke(llm_messages)
        response_text = response.content if hasattr(response, "content") else str(response)

        state.response = response_text
        state.messages.append(AIMessage(content=response_text))

        # Keep only last 2 conversation pairs (4 messages)
        if len(state.messages) > 4:
            state.messages = state.messages[-4:]

        logger.info("Chat_node: response length=%d", len(response_text))
        return state
    except Exception as e:
        logger.error("Error in chat_node: %s", e, exc_info=True)
        return state
