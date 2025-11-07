from langchain_core.prompts import ChatPromptTemplate
from config import GEMINI_LLM as llm
#from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import State

def get_screener_url_and_ticker_symbol(state: State) -> State:
    try:
        response_schemas = [
            ResponseSchema(name="ticker_symbol", description="The official ticker symbol for the given stock"),
        ]

        parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = parser.get_format_instructions()

        prompt_template = ChatPromptTemplate(
    [
        ("system", "You are a financial research assistant with deep expertise in Indian equities. Given the user input, your task is to identify the official ticker symbol of the stock as per NSE (National Stock Exchange of India). Use precise and accurate information to determine the correct ticker symbol."),
        ("user","""stock name: {stock_name}
        If the user input is ambiguous or refers to multiple stocks, choose the most prominent or widely recognized stock based on market capitalization and trading volume.   \n
        Provide only the ticker symbol without any additional text.   \n
        Return the result strictly in this structured format:
        {format_instructions}"""),
    ]
        )
        prompt_template = prompt_template.partial(format_instructions=format_instructions)
        chain = prompt_template | llm | parser
        response = chain.invoke(input={"stock_name": state.User_stock_name})
        ticker_symbol = response['ticker_symbol']
        screener_url = f"https://www.screener.in/company/{ticker_symbol}/consolidated/"
        state.ScreenerURL = screener_url
        state.TickerSymbol = ticker_symbol
        print(f'From ScreenerURL_node: ')
        print(f"Screener URL: {screener_url} and Ticker Symbol: {ticker_symbol}")
        return {"ScreenerURL": screener_url, "TickerSymbol": ticker_symbol}
    except Exception as e:
        print(f"Error in getting Screener URL and Ticker Symbol: {e}")
        return {"ScreenerURL": "", "TickerSymbol": ""}