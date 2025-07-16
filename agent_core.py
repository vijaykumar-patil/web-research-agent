import os
from dotenv import load_dotenv
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent

# Load API keys
load_dotenv()

def create_agent(verbose: bool = False):
    # Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        convert_system_message_to_human=True
    )

    # Web search tool
    search = DuckDuckGoSearchAPIWrapper()

    tools = [
        Tool(
            name="Web Search",
            func=search.run,
            description="Search the web for up-to-date info"
        )
    ]

    # LangChain Agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent="zero-shot-react-description",
        verbose=verbose
    )

    return agent
