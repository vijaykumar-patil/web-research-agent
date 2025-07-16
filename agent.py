from agent_core import create_agent

def main():
    agent = create_agent(verbose=True)
    question = input("Ask your research question: ")
    try:
        response = agent.run(question)
        print("\n📌 Answer:\n", response)
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
