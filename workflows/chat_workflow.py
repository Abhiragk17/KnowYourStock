"""Chat workflow: START -> ChatNode -> END."""

from langgraph.graph import StateGraph, START, END

from models import ChatState
from nodes import chat_node

_graph = StateGraph(state_schema=ChatState)
_graph.add_node("ChatNode", chat_node)
_graph.add_edge(START, "ChatNode")
_graph.add_edge("ChatNode", END)

chat_workflow = _graph.compile()
