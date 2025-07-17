# app.py
import streamlit as st
from agent_core import create_agent
from history import log_qa, get_all_history, init_db

st.set_page_config(page_title="Web Research Agent", layout="centered")
st.title("🌐 Web Research Agent")
st.write("Ask a question and get researched answers using web + Gemini AI.")

init_db()
question = st.text_input(
    "🔍 Enter your research question",
    autocomplete="off"  # or "off" if you want to disable it
)
agent = create_agent(verbose=False)

if st.button("Get Answer") and question:
    with st.spinner("Thinking..."):
        try:
            response = agent.run(question)
            st.success("✅ Answer:")
            st.write(response)
            log_qa(question, response)
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.markdown("---")
st.subheader("📜 Past Q&A History")

for timestamp, q, a in get_all_history():
    with st.expander(f"🔎 {q} ({timestamp})"):
        st.write(a)
