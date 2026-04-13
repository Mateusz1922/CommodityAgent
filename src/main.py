import requests
from crewai import Crew, Process
from config import logger, SLACK_URL, my_llm
from agents import researcher, writer, critic, task_research, task_report, task_review

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
        agents=[researcher, writer, critic],
        tasks=[task_research, task_report, task_review],
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