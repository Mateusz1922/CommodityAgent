import os
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama
from langchain_community.tools import DuckDuckGoSearchRun

# 1. Local model config
llama4 = Ollama(model="llama4:8b")
search_tool = DuckDuckGoSearchRun()

# 2. Agents definitions
researcher = Agent(
    role="Commodity Market Specialist",
    goal="Find all newest information about copper prices and market trends for April 2026",
    backstory="You're an analyst with 10 years of experience in Goldman Sachs. You can differentiate between news noise and real market signals",
    tools=[search_tool],
    llm=llama4,
    verbose=True
)

writer = Agent(
    role='Business Journalist',
    goal='Prepare brief report for an investor on Slack',
    backstory='You can translate complex data on benefit langauge. Your reports are detailed and without hallucinations.',
    llm=llama4,
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
    verbose=True
)

# START
print("### Agent jobs START ###")
result = commodity_crew.kickoff()
print("\n\n######################")
print("## FINAL REPORT:")
print(result)