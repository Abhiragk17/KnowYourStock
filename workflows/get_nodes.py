"""Registry of all LangGraph node functions."""

from nodes import (
    get_stock_news,
    extract_screener_data,
    get_screener_url_and_ticker_symbol,
    get_stock_info,
)


def get_nodes() -> dict:
    """Returns a dictionary mapping node names to their callable functions."""
    return {
        "StockNewsNode": get_stock_news,
        "ScreenerExtractNode": extract_screener_data,
        "ScreenerURLNode": get_screener_url_and_ticker_symbol,
        "StockInfoNode": get_stock_info,
    }
