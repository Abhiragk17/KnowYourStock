import bs4
from langchain_community.document_loaders import WebBaseLoader
from config import TAVILY_CLIENT
import re

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import State

def extract_screener_data(state: State) -> State:
    try:
        """Fetch and return the HTML content of a Screener.in page."""
        response = TAVILY_CLIENT.extract(
            urls=[state.ScreenerURL],
            include_images=False,
            format="markdown",
            extract_depth="basic"
        )
        response = response['results'][0]['raw_content']
        response = clean_screener_content(response)
        state.screener_data = response
        print(f'From ScreenerExtract_node: ')
        print(f"Screener Data: {response[:500]}...")
        return {"screener_data": response}
    except Exception as e:
        print(f"Error extracting Screener data: {e}")
        state.screener_data = ""
        return {"screener_data": ""}

def clean_screener_content(raw_content: str) -> str:
    """
    Cleans Screener.in extracted markdown by removing:
    - Screener logos, icons, navigation items
    - Footer texts and copyright notes
    """
    # Remove image and logo links
    content = re.sub(r'!\[.*?\]\(https:\/\/cdn-static\.screener\.in.*?\)', '', raw_content)

    # Remove duplicate 'Screener Logo' mentions or headers
    content = re.sub(r'#*\s*Screener Logo\s*', '', content, flags=re.IGNORECASE)

    # Remove trailing 'Stock analysis...' footer and terms/privacy lines
    content = re.sub(
        r'Stock analysis.*?Privacy.*?(Mittal Analytics.*?C-MOTS.*?Privacy.*?)?$',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove extra newlines and spaces
    #content = re.sub(r'\n{2,}', '\n\n', content).strip()

    # Remove [Chart](#chart)
    content = re.sub(r'\(#top\)\s*', "", content).strip()
    content = re.sub(r"\[Chart\]\(#chart\)\s*", "", content)
    content = re.sub(r"\[Analysis\]\(#analysis\)\s*", "", content)
    content = re.sub(r"\[Peers\]\(#peers\)\s*", "", content)
    content = re.sub(r"\[Quarters\]\(#quarters\)\s*", "", content)
    content = re.sub(r"\[Profit & Loss\]\(#profit-loss\)\s*", "", content)
    content = re.sub(r"\[Balance Sheet\]\(#balance-sheet\)\s*", "", content)
    content = re.sub(r"\[Cash Flow\]\(#cash-flow\)\s*", "", content)
    content = re.sub(r"\[Ratios\]\(#ratios\)\s*", "", content)
    content = re.sub(r"\[Investors\]\(#shareholding\)\s*", "", content)
    content = re.sub(r"\[Documents\]\(#documents\)\s*", "", content)


    return content