import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from crewai import LLM

# load data from .env file
load_dotenv()
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Logging config
log_filename = f"agent_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_work.log", encoding='utf-8'),
        logging.StreamHandler() # write in console parallel to CrewAI
    ]
)

logger = logging.getLogger("CommodityAgent")

# 1. Local model config
my_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)