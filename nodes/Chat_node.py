from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage,BaseMessage
from config import GEMINI_LLM as llm
import sys
from pathlib import Path
from typing import List, Dict
import traceback

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import ChatState

def format_recent_messages(recent_messages: List[BaseMessage]) -> str:
    formatted = "<Chat History>\n"
    for msg in recent_messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
        formatted += f"{role}: {msg.content}\n"
    formatted += "</Chat History>\n"
    return formatted

def chat_node(state: ChatState) -> ChatState:
    try:
        # Build system prompt with optional context
        system_prompt = """You are a helpful financial assistant with expertise in stock market analysis, 
company information, and financial news. Provide accurate, informative, and concise responses.

If the user asks about a specific stock, use the provided context about that stock to give detailed answers.
Be professional and helpful in your responses."""

        # Add stock context if available
        context_info = ""
        if state.context:
            TickerSymbol = state.context.get("TickerSymbol", "")
            if TickerSymbol:
                context_info += f"\n\nStock : {TickerSymbol}"

        if context_info:
            system_prompt += context_info

        # state.messages is Annotated[List[BaseMessage], add_messages]
        # It should already contain the last 5 messages (including current user question as last)
        recent_messages = state.messages[-5:] if len(state.messages) > 5 else state.messages

        # Build message list for LLM
        llm_messages: List[BaseMessage] = [SystemMessage(content=system_prompt), HumanMessage(content=format_recent_messages(recent_messages))]
        print(f"LLM messages: {llm_messages}")
        # Get response from LLM
        response = llm.invoke(llm_messages)

        # Extract response content
        response_text = response.content if hasattr(response, "content") else str(response)

        # Update state
        state.response = response_text

        # Append assistant response to conversation and keep only last 2 pairs (4 messages)
        state.messages.append(AIMessage(content=response_text))
        if len(state.messages) > 4:
            state.messages = state.messages[-4:]

        print(f'Chat response: {response_text[:100]}...')
        return state
    except Exception as e:
        print(f"Error in chat_node: {e}")
        traceback.print_exc()
        return state