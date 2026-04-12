from crewai import Agent, Task
from config import my_llm
from tools import InternetSearchTool, CopperPriceTool, knowledge_tool

# 3. Tool initialization
search_tool_instance = InternetSearchTool()
finance_tool = CopperPriceTool()

# 2. Agents definitions
researcher = Agent(
    role="Commodity Market Specialist",
    goal="Find all newest information about copper prices and market trends for April 2026",
    backstory="You're an analyst with 10 years of experience in Goldman Sachs. You can differentiate between news noise and real market signals",
    tools=[search_tool_instance, finance_tool, knowledge_tool],
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

