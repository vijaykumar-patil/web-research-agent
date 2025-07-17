# agent.py
from agent_core import create_agent
from history import init_db, log_qa

def main():
    init_db()
    agent = create_agent(verbose=True)
    question = input("Ask your research question: ")
    try:
        response = agent.run(question)
        print("\n📌 Answer:\n", response)
        log_qa(question, response, user_id="local-cli")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
