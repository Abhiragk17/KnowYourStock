from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import ChatState
from nodes.Chat_node import chat_node

# Create the chat workflow
chat_workflow_graph = StateGraph(state_schema=ChatState)

# Add the chat node
chat_workflow_graph.add_node("ChatNode", chat_node)

# Define the workflow: START -> ChatNode -> END
chat_workflow_graph.add_edge(START, "ChatNode")
chat_workflow_graph.add_edge("ChatNode", END)

# Compile the workflow
chat_workflow = chat_workflow_graph.compile()

print(f'Chat workflow nodes: {chat_workflow_graph.nodes}')
print(f'Chat workflow edges: {chat_workflow_graph.edges}')

# Optionally draw the workflow graph
try:
    chat_workflow.get_graph().draw_png("langgraph_chat_workflow.png")
except Exception as e:
    print(f"Could not draw workflow graph: {e}")

