import os
import requests
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool # tool decorator
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 1. Local model config
my_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)

@tool("search_internet")
def search_internet(query: str):
    """Searching internet in order to find newest information about the given topic."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

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
    tools=[search_internet],
    llm=my_llm,
    verbose=True,
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