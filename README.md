# CommodityAgent

Commodity Market Intelligence System
Project Overview
I developed this system to automate the time-consuming process of monitoring commodity markets. Instead of manually scanning news and financial reports, this project uses a multi-agent AI workflow to research, analyze, and report on market trends—specifically focused on copper prices for this implementation.

The goal was to create a tool that provides actionable insights directly to a business communication channel (Slack), reducing the noise and focusing on key market drivers.

How It Works
The system is built on the CrewAI framework and utilizes a team of specialized autonomous agents:

Market Research Agent: Scours the web using DuckDuckGo to find the latest news, supply chain disruptions, and geopolitical factors affecting prices.

Investment Advisor Agent: Processes the raw research, filters out the noise, and generates a concise report with a clear recommendation (BUY/SELL/HOLD).

Key Technical Features
Local Execution: Powered by Llama 3.2 running locally via Ollama. This ensures 100% data privacy and eliminates the costs associated with proprietary LLM APIs.

Resilient Tool Calling: Implemented using custom Python classes and Pydantic validation. The system is designed to handle and recover from validation errors, which is crucial when running smaller, local models.

Direct Integration: Features a dedicated pipeline to push final reports to Slack via incoming webhooks, making the insights immediately available to the team.

Scalable Architecture: The modular design allows for easy addition of new data sources (like yfinance) or expanding the scope to other commodities like gold, oil, or lithium.

Why This Matters
In a fast-moving market, the delay between a news event and a strategic decision can be costly. This project demonstrates how autonomous agents can act as a force multiplier for analysts, handling the "grunt work" of data collection and initial synthesis so humans can focus on high-level strategy.

Tech Stack
Language: Python 3.11+

AI Framework: CrewAI

Local LLM: Ollama (Llama 3.2)

Validation: Pydantic

Data Sources: DuckDuckGo Search API

Notifications: Slack API

### Visual System Workflow

graph TD
    A[System start] --> B{Agent Researcher}
    B -->|Looks for information| C[DuckDuckGo]
    B -->|Fetches prices| D[yfinance]
    C --> E[Agent Analyst]
    D --> E
    E -->|Trend analysis| F[Agent Writer]
    F -->|Report generation| G[Slack Webhook]
    G --> H[End]