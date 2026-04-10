# separating the tools, so that we can easily test and add new ones
import yfinance as yf
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchRun
from config import logger

class SearchInput(BaseModel):
    query: str = Field(..., description="The search query to look up on the internet.")

class InternetSearchTool(BaseTool):
    name: str = "search_internet"
    description: str = "Searching in internet in order to find newest market information."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        try:
            search = DuckDuckGoSearchRun()
            return search.run(query)
        except Exception as e:
            return f"Search error: {str(e)}"

class FinanceInput(BaseModel):
    ticker: str = Field(..., description="The stock or commodity ticker symbol (e.g., 'HG=F' for Copper).")

class CopperPriceTool(BaseTool):
    name: str = "get_market_data"
    description: str = "Fetches current stock price and stats for the given commodity"
    args_schema: type[BaseModel] = FinanceInput

    def _run(self, ticker: str) -> str:
        logger.info(f"Stock data fetch for {ticker}")
        try:
            data = yf.Ticker(ticker)
            price = data.fast_info['last_price']
            change = data.fast_info['year_to_date_change'] * 100
            logger.info(f"Price fetched: {price} USD for {ticker}")
            return f"Current price {ticker}: {price:.2f} USD. Change since start of the year: {change:.2f}%"
        except Exception as e:
            logger.error(f"yfinance error for {ticker}: {str(e)}")
            return f"Fetching data unsuccessful for {ticker}: {str(e)}"
