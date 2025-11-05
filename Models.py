from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages

class NewsArticle(BaseModel):
    title: str = Field(..., description="Title of the news article")
    url: str = Field(..., description="URL of the news article")
    content: str = Field(..., description="Content of the news article")

class StocksInfo(BaseModel):
    ticker_symbol: str = Field(..., description="The official ticker symbol of the stock")
    business_model: str = Field(..., description="Description of the company's business model, products, and revenue mix")
    geographical_revenue_mix: str = Field(..., description="Breakdown of revenue by geography or region")
    sectoral_tailwinds_headwinds: str = Field(..., description="Sectoral opportunities and risks affecting the business")
    capex_expansion_plans: str = Field(..., description="Details about capital expenditure and expansion plans")
    management_commentary_forward_guidance: str = Field(..., description="Recent management commentary and forward-looking statements")

class State(BaseModel):
    User_stock_name: Optional[str] = Field(default="", description="The name of the stock provided by the user")
    ScreenerURL: Optional[str] = Field(default="", description="The Screener URL of the stock")
    # Some nodes expect TickerSymbol while others used Stock_Ticker — support both
    TickerSymbol: Optional[str] = Field(default="", description="The stock ticker symbol (canonical)")
    Stock_Ticker: Optional[str] = Field(default="", description="Legacy alias for ticker symbol")
    news_articles: Optional[List[NewsArticle]] = Field(default_factory=list, description="List of news articles related to the stock")
    stocks_info: Optional[StocksInfo] = Field(default=None, description="Information related to the stock")
    screener_data: Optional[str] = Field(default="", description="Extracted and cleaned data from the Screener.in page")

class ChatState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]
    message: str = Field(default="", description="Current user message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context from stock search")
    response: str = Field(default="", description="AI response")