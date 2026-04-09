import os
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import BaseTool # tool decorator
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field

load_dotenv()
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 1. Local model config
my_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

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

# 3. Inicjalizacja narzędzia
search_tool_instance = InternetSearchTool()


def send_to_slack(message):
    if SLACK_URL:
        payload = {"text": message}
        requests.post(SLACK_URL, json=payload)
        print("--- Report sent to Slack! ---")
    else:
        print("--- No Slack URL. Report only in terminal ---")

# 2. Agents definitions
researcher = Agent(
    role="Commodity Market Specialist",
    goal="Find all newest information about copper prices and market trends for April 2026",
    backstory="You're an analyst with 10 years of experience in Goldman Sachs. You can differentiate between news noise and real market signals",
    tools=[search_tool_instance],
    llm=my_llm,
    verbose=True,
    max_iter=5,
    allow_delegation=False
)

writer = Agent(
    role='Business Journalist',
    goal='Prepare brief report for an investor on Slack',
    backstory='You can translate complex data on benefit langauge. Your reports are detailed and without hallucinations.',
    llm=my_llm,
    verbose=True
)

# 3. Task definition
task_research = Task(
    description="Identify 3 crucial factors that impact on the current copper price. Focus on the data from last week",
    agent=researcher,
    expected_output="List of 3 points with short explanation and source."
)

task_report = Task(
    description='Based on the research write a report (max 150 words). Finish with a specific recommendation: BUY, SELL or WAIT',
    agent=writer,
    expected_output='Report done in Markdown format.'
)

# 4. Orchestration (Crew)
commodity_crew = Crew(
    agents=[researcher, writer],
    tasks=[task_research, task_report],
    process=Process.sequential, # First search then write
    verbose=True,
    manager_llm=my_llm
)

# START
print("### Agent jobs START ###")
result = commodity_crew.kickoff()
print("\n\n######################")
print("## FINAL REPORT:")
print(result)

# Send to slack
send_to_slack(str(result))