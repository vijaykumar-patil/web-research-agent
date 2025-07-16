from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.agents import Tool, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Changed model name
    temperature=0.7,
    convert_system_message_to_human=True
)

# Search tool
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
    verbose=True
)

question = input("Ask your research question: ")
response = agent.run(question)
print("\n📌 Answer:\n", response)