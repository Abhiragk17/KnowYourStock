from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Langgraph.get_nodes import getnodes
from Models import NewsArticle,StocksInfo,State


nodes = getnodes()
for node_name, node in nodes.items():
    print(f'Loaded node: {node_name} -> {node}')
    print(f'type of node: {type(node)}')



workflow = StateGraph(state_schema=State)
# Add nodes using safe, non-reserved names that match get_nodes() output
workflow.add_node("ScreenerURLNode", nodes["ScreenerURLNode"])
workflow.add_node("StockInfoNode", nodes["StockInfoNode"])
workflow.add_node("ScreenerExtractNode", nodes["ScreenerExtractNode"])
workflow.add_node("StockNewsNode", nodes["StockNewsNode"])

# Define the flow: START -> ScreenerURLNode -> [StockInfoNode, ScreenerExtractNode, StockNewsNode] -> END
workflow.add_edge(START, "ScreenerURLNode")
workflow.add_edge("ScreenerURLNode", "StockInfoNode")
workflow.add_edge("ScreenerURLNode", "ScreenerExtractNode")
workflow.add_edge("ScreenerURLNode", "StockNewsNode")

workflow.add_edge("StockInfoNode", END)
workflow.add_edge("ScreenerExtractNode", END)
workflow.add_edge("StockNewsNode", END)

print(f'Workflow nodes: {workflow.nodes}')
print(f'Workflow edges: {workflow.edges}')

workflow = workflow.compile()
# Optionally draw the workflow graph (disabled by default)
# workflow.get_graph().draw_png("langgraph_workflow.png")