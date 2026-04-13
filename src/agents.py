from crewai import Agent, Task
from config import my_llm
from tools import InternetSearchTool, CopperPriceTool, LocalKnowledgeTool

# 3. Tool initialization
search_tool_instance = InternetSearchTool()
finance_tool = CopperPriceTool()
knowledge_tool = LocalKnowledgeTool()

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

critic = Agent(
    role="Senior Risk & Quality Compliance Analyst",
    goal="Verify the report for factual accuracy, consistency with research data, and professional tone.",
    backstory="""You are a veteran analyst known for your skepticism. 
    Your job is to ensure that the Writer didn't hallucinate facts and that 
    the recommendation (BUY/SELL/WAIT) is logically supported by the provided research.
    If you find errors, you demand corrections.""",
    llm=my_llm,
    verbose=True,
    allow_delegation=False # We don't let him ask other agents for a justification
)

# 3. Task definition
task_research = Task(
    description="Identify 3 crucial factors that impact on the current copper price. Focus on the data from last week",
    agent=researcher,
    expected_output="List of 3 points with short explanation and source."
)

task_report = Task(
    description="""Based on the research, write a professional copper market report.
    1. Summarize 3 key factors.
    2. Crucial: You MUST end the report with a clear section: 
       ### RECOMMENDATION: [BUY, SELL, or WAIT]
       Provide a 1-sentence justification for this choice.""",
    agent=writer,
    expected_output='A Markdown report with a mandatory "RECOMMENDATION" section at the end.'
)

task_review = Task(
    description="""Review and finalize the copper report. 
    Your main priority is to ensure the factual data is correct AND that there is a 
    CLEAR and VISIBLE investor recommendation at the very end.
    
    If the recommendation is missing, you must add it based on the research findings.
    The final output must end with:
    ### FINAL RECOMMENDATION: [ACTION]""",
    agent=critic,
    context=[task_research, task_report],
    expected_output="Final polished Markdown report ending with a bold FINAL RECOMMENDATION section."
)

