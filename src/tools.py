# separating the tools, so that we can easily test and add new ones
import yfinance as yf
from crewai.tools import BaseTool
from crewai_tools import DirectorySearchTool
from pydantic import BaseModel, Field, PrivateAttr
from langchain_community.tools import DuckDuckGoSearchRun
from config import logger, my_llm
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
import os

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

# Local searcher scheme
class LocalSearchInput(BaseModel):
    query: str = Field(..., description="The question to ask based on local knowledge base.")

# tool class
class LocalKnowledgeTool(BaseTool):
    name: str = "search_local_notes"
    description: str = "Searches internal makrdown notes about commodities and copper market"
    args_schema: type[BaseModel] = LocalSearchInput

    # PrivateAttr used in order to make Pydantic not to try to valudate the db
    _db: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Initializing Local Vector Database... this may take a moment")

        # embeddings config (creates text fingerprints)
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )

        # load .md files from knowledge/ folder
        try:
            loader = DirectoryLoader("knowledge/", glob="**/*.md", loader_cls=TextLoader)
            docs = loader.load()

            # text splitting
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            texts = text_splitter.split_documents(docs)

            # Create temporary vector DB in memory (or in folder)
            # Bypassing OpenAI
            self._db = Chroma.from_documents(
                documents=texts,
                embedding=embeddings,
                collection_name="local_knowledge"
            )
            logger.info("Vector Database ready and indexed.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self._db = None
        
        def _run(self, query: str) -> str:
            if not self._db:
                return "Knwoledge base is inaccesible (initialization error)"

            logger.info(f"Searching local notes for: {query}")
            # Searching in a ready db

            # searching for best fitting fragments
            results = self._db.similarity_search(query, k=3)

            return "\n---\n".join([res.page_content for res in results])
    
# Instance initialization
knowledge_tool = LocalKnowledgeTool()

