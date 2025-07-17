# agent.py
from agent_core import create_agent, run_with_logging
from history import log_qa, init_db

def main():
    init_db()
    agent = create_agent(verbose=True)

    question = input("Ask your research question: ").strip()
    if not question:
        print("⚠️ No question provided.")
        return

    try:
        result = run_with_logging(agent, question)
        answer = result["answer"]
        sources = result["sources"]
        confidence = result["confidence"]

        print("\n📌 Answer:\n", answer)

        print("\n🔗 Sources:")
        if sources:
            for src in sources:
                print(f"- {src}")
        else:
            print("No sources found.")

        print(f"\n📊 Confidence Level: {confidence * 100:.1f}%")

        # Store only answer in history (optionally extend to store sources/confidence)
        log_qa(question, answer)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
