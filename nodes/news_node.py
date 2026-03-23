"""Node that fetches latest news articles for a stock using Tavily."""

from config import TAVILY_CLIENT, logger
from models import State, NewsArticle


def get_stock_news(state: State) -> dict:
    try:
        query = f"Latest news about {state.User_stock_name} or its sector."
        response = TAVILY_CLIENT.search(
            query=query,
            topic="news",
            max_results=3,
            time_range="week",
        )
        results = response["results"]
        news_articles = [
            NewsArticle(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
            )
            for r in results
        ]
        logger.info("News_node: fetched %d articles for '%s'", len(news_articles), state.User_stock_name)
        return {"news_articles": news_articles}
    except Exception as e:
        logger.error("Error fetching stock news: %s", e, exc_info=True)
        return {"news_articles": []}
