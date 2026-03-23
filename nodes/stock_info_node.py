"""Node that uses an LLM to generate structured stock information."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from config import GEMINI_LLM as llm, logger
from models import State, StocksInfo

_parser = PydanticOutputParser(pydantic_object=StocksInfo)
_format_instructions = _parser.get_format_instructions()


def get_stock_info(state: State) -> dict:
    try:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a financial research assistant with deep expertise in Indian equities.\n\n"
                    "Given the stock ticker symbol, extract and summarize:\n"
                    "- Business Model along with Product & Revenue Mix\n"
                    "- Geographical Revenue Mix\n"
                    "- Sectoral Tailwinds & Headwinds\n"
                    "- Capex & Expansion Plans\n"
                    "- Management Commentary & Forward Guidance\n\n"
                    "Return the result strictly in this structured format:\n\n{format_instructions}",
                ),
                ("user", "Ticker symbol - {ticker_symbol}."),
            ],
        ).partial(format_instructions=_format_instructions)

        chain = prompt_template | llm | _parser
        response = chain.invoke({"ticker_symbol": state.TickerSymbol})
        logger.info("StockInfo_node: generated info for %s", state.TickerSymbol)
        return {"stocks_info": response}
    except Exception as e:
        logger.error("Error in StockInfo_node: %s", e, exc_info=True)
        return {"stocks_info": None}
