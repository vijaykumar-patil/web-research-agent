# agent_core.py

import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent

# Load environment variables
load_dotenv()

# ✅ Create the LangChain agent
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

# ✅ Log Q&A to CSV (optional, for local debugging)
def log_to_csv(question, answer, log_file="qa_history.csv"):
    file_exists = os.path.exists(log_file)
    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer"])
        writer.writerow([datetime.now().isoformat(), question, answer])

# ✅ Extract URLs from text (basic pattern)
def extract_sources(text):
    url_pattern = r'https?://[^\s\]\)"]+'
    return re.findall(url_pattern, text)

# ✅ Run and log, with metadata
def run_with_logging(agent, question: str, user_id: str = None) -> dict:
    raw_answer = agent.run(question)

    sources = extract_sources(raw_answer)
    confidence = 0.9  # Default confidence if not returned from LLM

    log_to_csv(question, raw_answer)  # Optional

    return {
        "answer": raw_answer,
        "sources": sources,
        "confidence": confidence
    }
