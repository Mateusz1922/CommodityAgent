# import os
# import requests
# import logging
# from datetime import datetime
# from dotenv import load_dotenv
# from crewai import Agent, Task, Crew, LLM, Process
# from crewai.tools import BaseTool 
# from langchain_community.llms import Ollama
# from langchain_community.tools import DuckDuckGoSearchRun
# from pydantic import BaseModel, Field
# import yfinance as yf

# load_dotenv()
# SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# # Logging config
# log_filename = f"agent_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("agent_work.log", encoding='utf-8'),
#         logging.StreamHandler() # write in console parallel to CrewAI
#     ]
# )

# logger = logging.getLogger("CommodityAgent")
# logger.info("Agent System Initialization...")

# # 1. Local model config
# my_llm = LLM(
#     model="ollama/llama3.2",
#     base_url="http://localhost:11434"
# )

# class SearchInput(BaseModel):
#     query: str = Field(..., description="The search query to look up on the internet.")

# class InternetSearchTool(BaseTool):
#     name: str = "search_internet"
#     description: str = "Searching in internet in order to find newest market information."
#     args_schema: type[BaseModel] = SearchInput

#     def _run(self, query: str) -> str:
#         try:
#             search = DuckDuckGoSearchRun()
#             return search.run(query)
#         except Exception as e:
#             return f"Search error: {str(e)}"

# # Input Schema for finances
# class FinanceInput(BaseModel):
#     ticker: str = Field(..., description="The stock or commodity ticker symbol (e.g., 'HG=F' for Copper).")

# # yfinance class tool
# class CopperPriceTool(BaseTool):
#     name: str = "get_market_data"
#     description: str = "Fetches current stock price and stats for the given commodity"
#     args_schema: type[BaseModel] = FinanceInput

#     def _run(self, ticker: str) -> str:
#         logger.info(f"Stock data fetch for {ticker}")
#         try:
#             data = yf.Ticker(ticker)
#             # Fetch closure or current price
#             price = data.fast_info['last_price']
#             logger.info(f"Price fetched: {price} USD for {ticker}")
#             change = data.fast_info['year_to_date_change'] * 100
#             return f"Current price {ticker}: {price:.2f} USD. Change since start of the year: {change:.2f}%"
#         except Exception as e:
#             logger.error(f"yfinance error for {ticker}: {str(e)}")
#             return f"Fetching data unsuccessful for {ticker}: {str(e)}"


# # 3. Inicjalizacja narzędzia
# search_tool_instance = InternetSearchTool()
# finance_tool = CopperPriceTool()


# def send_to_slack(message):
#     logger.info("Preparing report delivery to Slack...")
#     if SLACK_URL:
#         try:
#             payload = {"text": message}
#             response = requests.post(SLACK_URL, json=payload)
#             if response.status_code == 200:
#                 logger.info("Report sent to Slack!")
#             else:
#                 logger.warning(f"Slack responded with code: {response.status_code}. Info: {response.text}")
#         except Exception as e:
#             logger.error(f"Critical error while sending to Slack: {e}")

# # 2. Agents definitions
# researcher = Agent(
#     role="Commodity Market Specialist",
#     goal="Find all newest information about copper prices and market trends for April 2026",
#     backstory="You're an analyst with 10 years of experience in Goldman Sachs. You can differentiate between news noise and real market signals",
#     tools=[search_tool_instance, finance_tool],
#     llm=my_llm,
#     verbose=True,
#     max_iter=5,
#     allow_delegation=False
# )

# writer = Agent(
#     role='Business Journalist',
#     goal='Prepare brief report for an investor on Slack',
#     backstory='You can translate complex data on benefit langauge. Your reports are detailed and without hallucinations.',
#     llm=my_llm,
#     verbose=True
# )

# # 3. Task definition
# task_research = Task(
#     description="Identify 3 crucial factors that impact on the current copper price. Focus on the data from last week",
#     agent=researcher,
#     expected_output="List of 3 points with short explanation and source."
# )

# task_report = Task(
#     description='Based on the research write a report (max 150 words). Finish with a specific recommendation: BUY, SELL or WAIT',
#     agent=writer,
#     expected_output='Report done in Markdown format.'
# )

# # 4. Orchestration (Crew)
# commodity_crew = Crew(
#     agents=[researcher, writer],
#     tasks=[task_research, task_report],
#     process=Process.sequential, # First search then write
#     verbose=True,
#     manager_llm=my_llm
# )

# # START
# print("### Agent jobs START ###")
# result = commodity_crew.kickoff()
# print("\n\n######################")
# print("## FINAL REPORT:")
# print(result)

# # Send to slack
# send_to_slack(str(result))


####################################################

import requests
from crewai import Crew, Process
from config import logger, SLACK_URL, my_llm
from agents import researcher, writer, task_research, task_report

def send_to_slack(message):
    logger.info("Preparing report delivery to Slack...")
    if SLACK_URL:
        try:
            payload = {"text": message}
            response = requests.post(SLACK_URL, json=payload)
            if response.status_code == 200:
                logger.info("Report sent to Slack!")
            else:
                logger.warning(f"Slack responded with code: {response.status_code}. Info: {response.text}")
        except Exception as e:
            logger.error(f"Critical error while sending to Slack: {e}")

def run_commodity_system():
    # 4. Orchestration (Crew)
    commodity_crew = Crew(
        agents=[researcher, writer],
        tasks=[task_research, task_report],
        process=Process.sequential, # First search then write
        verbose=True,
        manager_llm=my_llm
    )
    
    logger.info("### Agent jobs START ###")
    result = commodity_crew.kickoff()
    
    # Finalny raport
    report_text = str(result)
    print("\n\n######################")
    print("## FINAL REPORT:")
    print(report_text)

    send_to_slack(report_text)

if __name__ == "__main__":
    run_commodity_system()