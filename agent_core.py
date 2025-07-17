import os
import re
from dotenv import load_dotenv
from datetime import datetime

from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from google.api_core.exceptions import DeadlineExceeded

from history import log_qa  # ✅ Use SQLite logger

# Load environment variables
load_dotenv()

# Optional: Reduce Gemini timeout
import google.generativeai as genai
genai.configure(timeout=15)  # seconds

# ✅ Extract URLs
def extract_sources(text):
    url_pattern = r'https?://[^\s\]\)"]+'
    return re.findall(url_pattern, text)

# ✅ Fast model using RunnableSequence
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

# ✅ Full web-search agent
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

# ✅ Unified execution function with SQLite logging
def run_with_logging(model, question: str, user_id: str = None, is_fast: bool = False) -> dict:
    try:
        if is_fast:
            result = model.invoke({"question": question})
        else:
            result = model.run(question)

        raw_answer = result if isinstance(result, str) else str(result)
        sources = extract_sources(raw_answer)
        confidence = 0.95 if is_fast else 0.90

        # ✅ Log into SQLite
        if user_id:
            log_qa(question, raw_answer, user_id)

        return {
            "answer": raw_answer,
            "sources": sources,
            "confidence": confidence
        }

    except DeadlineExceeded:
        return {
            "answer": "⚠️ Gemini timed out while processing the request.",
            "sources": [],
            "confidence": 0.0
        }

    except Exception as e:
        return {
            "answer": f"❌ Unexpected error: {str(e)}",
            "sources": [],
            "confidence": 0.0
        }
