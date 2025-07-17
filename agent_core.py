import os
import csv
import re
from datetime import datetime
from dotenv import load_dotenv

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

# Load .env variables
load_dotenv()

# ✅ Extract URLs
def extract_sources(text):
    url_pattern = r'https?://[^\s\]\)"]+'
    return re.findall(url_pattern, text)

# ✅ Local CSV logger
def log_to_csv(question, answer, log_file="qa_history.csv"):
    file_exists = os.path.exists(log_file)
    with open(log_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "question", "answer"])
        writer.writerow([datetime.now().isoformat(), question, answer])

# ✅ Fast fallback using RunnableSequence
def create_llm_chain():
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        convert_system_message_to_human=True
    )
    prompt = PromptTemplate.from_template(
        "Answer the question as concisely as possible:\n\n{question}"
    )
    return prompt | llm  # RunnableSequence

# ✅ Full agent with web tools
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
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=verbose
    )

# ✅ Unified run with logging
def run_with_logging(model, question: str, user_id: str = None, is_fast: bool = False) -> dict:
    if is_fast:
        result = model.invoke({"question": question})
    else:
        result = model.run(question)

    raw_answer = result if isinstance(result, str) else str(result)
    sources = extract_sources(raw_answer)
    confidence = 0.95 if is_fast else 0.90

    log_to_csv(question, raw_answer)

    return {
        "answer": raw_answer,
        "sources": sources,
        "confidence": confidence
    }
