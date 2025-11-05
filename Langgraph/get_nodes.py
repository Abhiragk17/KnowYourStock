import sys
from pathlib import Path

# Add parent directory to sys.path
parent_dir = Path(__file__).resolve().parent.parent
print(f'parent directory: {parent_dir}')
sys.path.append(str(parent_dir))

from nodes.News_node import get_stock_news
from nodes.ScreenerExtract_node import extract_screener_data
from nodes.ScreenerURL_node import get_screener_url_and_ticker_symbol
from nodes.StockInfo_node import get_stock_info


def getnodes() -> dict:
    """Returns a dictionary mapping node names to their callable functions."""
    return {
        "StockNewsNode": get_stock_news,
        "ScreenerExtractNode": extract_screener_data,
        "ScreenerURLNode": get_screener_url_and_ticker_symbol,
        "StockInfoNode": get_stock_info
    }

print(f'nodes: {getnodes()}')


def _discover_tool_files() -> list[Path]:
	root = Path(__file__).resolve().parent.parent
	tools_dir = root / "tools"
	if not tools_dir.exists():
		return []
	return [p for p in tools_dir.iterdir() if p.suffix == ".py" and not p.name.startswith("_")]
