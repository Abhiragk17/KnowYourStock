"""Node that extracts and cleans financial data from Screener.in."""

import re

from config import TAVILY_CLIENT, logger
from models import State


def extract_screener_data(state: State) -> dict:
    try:
        response = TAVILY_CLIENT.extract(
            urls=[state.ScreenerURL],
            include_images=False,
            format="markdown",
            extract_depth="basic",
        )
        raw = response["results"][0]["raw_content"]
        cleaned = _clean_screener_content(raw)
        logger.info("ScreenerExtract_node: extracted %d chars", len(cleaned))
        return {"screener_data": cleaned}
    except Exception as e:
        logger.error("Error extracting Screener data: %s", e, exc_info=True)
        return {"screener_data": ""}


# Patterns to strip from Screener.in markdown
_NAV_LINK_PATTERNS = [
    r"\[Chart\]\(#chart\)\s*",
    r"\[Analysis\]\(#analysis\)\s*",
    r"\[Peers\]\(#peers\)\s*",
    r"\[Quarters\]\(#quarters\)\s*",
    r"\[Profit & Loss\]\(#profit-loss\)\s*",
    r"\[Balance Sheet\]\(#balance-sheet\)\s*",
    r"\[Cash Flow\]\(#cash-flow\)\s*",
    r"\[Ratios\]\(#ratios\)\s*",
    r"\[Investors\]\(#shareholding\)\s*",
    r"\[Documents\]\(#documents\)\s*",
]


def _clean_screener_content(raw_content: str) -> str:
    """Remove Screener.in chrome (logos, nav links, footers) from extracted markdown."""
    content = re.sub(r"!\[.*?\]\(https://cdn-static\.screener\.in.*?\)", "", raw_content)
    content = re.sub(r"#*\s*Screener Logo\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(
        r"Stock analysis.*?Privacy.*?(Mittal Analytics.*?C-MOTS.*?Privacy.*?)?$",
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    content = re.sub(r"\(#top\)\s*", "", content).strip()
    for pattern in _NAV_LINK_PATTERNS:
        content = re.sub(pattern, "", content)
    return content
