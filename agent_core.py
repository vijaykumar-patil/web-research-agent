# agent_core.py
import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent

# Load API keys from .env
load_dotenv()

def create_agent(verbose: bool = False):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        convert_system_message_to_human=True
    )

    search = DuckDuckGoSearchAPIWrapper()

    tools = [
        Tool(
            name="Web Search",
            func=search.run,
            description="Search the web for up-to-date info"
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=verbose
    )

    return agent

def log_to_csv(question, answer, log_file="qa_history.csv"):
    file_exists = os.path.exists(log_file)
    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer"])
        writer.writerow([datetime.now().isoformat(), question, answer])

def extract_sources(text):
    return re.findall(r'(https?://\S+)', text)

def estimate_confidence(answer):
    if "I don't know" in answer or "uncertain" in answer:
        return 0.3
    return min(0.95, 0.6 + len(answer) / 500)

def run_with_logging(agent, question: str) -> dict:
    raw_answer = agent.run(question)
    sources = extract_sources(raw_answer)
    confidence = estimate_confidence(raw_answer)
    log_to_csv(question, raw_answer)
    return {
        "answer": raw_answer,
        "sources": sources,
        "confidence": confidence
    }
