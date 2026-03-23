from langchain_core.prompts import ChatPromptTemplate
#from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from config import GEMINI_LLM as llm
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from Models import State,StocksInfo

parser = PydanticOutputParser(pydantic_object=StocksInfo)
format_instructions = parser.get_format_instructions()

def get_stock_info(state: State) -> State:
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system","You are a financial research assistant with deep expertise in Indian equities.\n\n"
            "Given the stock ticker symbol Extract and summarize the following details:\n\n"
            "- Business Model along with Product & Revenue Mix\n"
            "- Geographical Revenue Mix\n"
            "- Sectoral Tailwinds & Headwinds\n"
            "- Capex & Expansion Plans\n"
            "- Management Commentary & Forward Guidance\n\n"
            "Return the result strictly in this structured format:\n\n{format_instructions}"),
            ("user","Ticker symbol - {ticker_symbol}.")
        ],
    ).partial(format_instructions=format_instructions)
        #prompt_template.input_variables.append("ticker_symbol")
        chain = prompt_template | llm | parser
        response = chain.invoke({"ticker_symbol": state.TickerSymbol})
        print(f'response from StocksInfoNode : {response}')
        print(f'type of response from StocksInfoNode : {type(response)}')
        return {"stocks_info": response}
    except Exception as e:
        print(f"Error in getting Stock Info: {e}")
        return {"stocks_info": None}