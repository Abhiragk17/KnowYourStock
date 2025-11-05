from config import TAVILY_CLIENT
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import State,NewsArticle

def get_stock_news(state: State) -> State:
    try:
        """Fetch latest news articles for a given stock using Tavily."""
        query = f"Latest news about {state.User_stock_name} or its sector."
        response = TAVILY_CLIENT.search(
            query=query,
            topic="news",
            max_results=3,
            time_range="week"
        )
        results = response['results']
        news_articles = []
        for result in results:
            news_articles.append(NewsArticle(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", "")
            ))
        print(f'From News_node: ')
        print(f"Fetched {len(news_articles)} news articles.")
        return {"news_articles": news_articles}
    except Exception as e:
        print(f"Error fetching stock news: {e}")
        return {"news_articles": []}
