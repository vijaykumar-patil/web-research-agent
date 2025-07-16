import streamlit as st
from agent_core import create_agent

st.set_page_config(page_title="Web Research Agent", layout="centered")
st.title("🌐 Web Research Agent")
st.write("Ask a question and get researched answers using web + Gemini AI.")

question = st.text_input("🔍 Enter your research question")
agent = create_agent(verbose=False)

if st.button("Get Answer") and question:
    with st.spinner("Thinking..."):
        try:
            response = agent.run(question)
            st.success("✅ Answer:")
            st.write(response)
        except Exception as e:
            st.error(f"❌ Error: {e}")
