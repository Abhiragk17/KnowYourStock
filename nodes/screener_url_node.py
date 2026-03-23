"""Node that resolves a stock name to its Screener.in URL and NSE ticker symbol."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from config import GEMINI_LLM as llm, logger
from models import State


class _TickerSchema(BaseModel):
    ticker_symbol: str = Field(..., description="The official ticker symbol for the given stock")


def get_screener_url_and_ticker_symbol(state: State) -> dict:
    try:
        parser = PydanticOutputParser(pydantic_object=_TickerSchema)
        format_instructions = parser.get_format_instructions()

        prompt_template = ChatPromptTemplate(
            [
                (
                    "system",
                    "You are a financial research assistant with deep expertise in Indian equities. "
                    "Given the user input, identify the official ticker symbol of the stock as per NSE "
                    "(National Stock Exchange of India).",
                ),
                (
                    "user",
                    "stock name: {stock_name}\n"
                    "If the input is ambiguous, choose the most prominent stock by market cap.\n"
                    "Return the result strictly in this structured format:\n{format_instructions}",
                ),
            ]
        )
        prompt_template = prompt_template.partial(format_instructions=format_instructions)
        chain = prompt_template | llm | parser
        response = chain.invoke(input={"stock_name": state.User_stock_name})

        ticker_symbol = response.ticker_symbol
        screener_url = f"https://www.screener.in/company/{ticker_symbol}/consolidated/"

        logger.info("ScreenerURL_node: URL=%s  Ticker=%s", screener_url, ticker_symbol)
        return {"ScreenerURL": screener_url, "TickerSymbol": ticker_symbol}
    except Exception as e:
        logger.error("Error in ScreenerURL_node: %s", e, exc_info=True)
        return {"ScreenerURL": "", "TickerSymbol": ""}
