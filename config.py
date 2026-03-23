"""Configuration and shared resources for the backend."""

import os
import logging
from functools import lru_cache
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("knowyourstock")

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    """Return a cached LLM instance."""
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)


@lru_cache(maxsize=1)
def get_tavily_client() -> TavilyClient:
    """Return a cached Tavily client."""
    return TavilyClient(api_key=TAVILY_API_KEY)


# Convenience aliases (backwards-compatible)
GEMINI_LLM = get_llm()
TAVILY_CLIENT = get_tavily_client()
