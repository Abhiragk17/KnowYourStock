"""Main stock-analysis workflow.

START -> ScreenerURLNode -> [StockInfoNode, ScreenerExtractNode, StockNewsNode] -> END
"""

from langgraph.graph import StateGraph, START, END

from models import State
from workflows.get_nodes import get_nodes

_nodes = get_nodes()

_graph = StateGraph(state_schema=State)
_graph.add_node("ScreenerURLNode", _nodes["ScreenerURLNode"])
_graph.add_node("StockInfoNode", _nodes["StockInfoNode"])
_graph.add_node("ScreenerExtractNode", _nodes["ScreenerExtractNode"])
_graph.add_node("StockNewsNode", _nodes["StockNewsNode"])

_graph.add_edge(START, "ScreenerURLNode")
_graph.add_edge("ScreenerURLNode", "StockInfoNode")
_graph.add_edge("ScreenerURLNode", "ScreenerExtractNode")
_graph.add_edge("ScreenerURLNode", "StockNewsNode")
_graph.add_edge("StockInfoNode", END)
_graph.add_edge("ScreenerExtractNode", END)
_graph.add_edge("StockNewsNode", END)

workflow = _graph.compile()
