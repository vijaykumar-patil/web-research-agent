import streamlit as st
from streamlit_auth0 import login_button
from agent_core import create_agent, create_llm_chain, run_with_logging
from history import log_qa, get_all_history, init_db

# Set page configuration
st.set_page_config(page_title="Web Research Agent", layout="centered")
init_db()

# 🔐 User Authentication
user_info = login_button(
    client_id=st.secrets["AUTH0_CLIENT_ID"],
    domain=st.secrets["AUTH0_DOMAIN"],
    key="auth0_login"
)

# 🔁 Cache both agents
@st.cache_resource
def get_agent():
    return create_agent(verbose=False)

@st.cache_resource
def get_fast_model():
    return create_llm_chain()

if user_info:
    user_id = user_info["sub"]
    user_name = user_info.get("name", "User")

    st.title("🌐 Web Research Agent")
    st.markdown(f"👋 Welcome, **{user_name}**")

    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    # Mode selector
    use_fast = st.toggle("⚡ Use Fast Mode (quicker, less research)", value=True)
    model = get_fast_model() if use_fast else get_agent()

    # 💬 Question input
    with st.form("qa_form"):
        question = st.text_input("🔍 Enter your research question", placeholder="e.g., What are the latest EV trends in India?")
        submitted = st.form_submit_button("Get Answer")

    if submitted and question.strip():
        with st.spinner("Thinking..."):
            try:
                result = run_with_logging(model, question, user_id=user_id, is_fast=use_fast)
                answer = result.get("answer", "No answer provided.")
                sources = result.get("sources", [])
                confidence = result.get("confidence", 0.0)

                # ✅ Display answer
                st.success("✅ Answer:")
                st.write(answer)

                # 🔗 Show sources
                st.markdown("#### 🔗 Sources")
                if sources:
                    for src in sources:
                        st.markdown(f"- [{src}]({src})")
                else:
                    st.info("No sources were detected.")

                # 📊 Confidence level
                st.markdown(f"#### 📊 Confidence Level: **{confidence * 100:.1f}%**")

                # 🗃️ Save to DB
                log_qa(question, answer, user_id=user_id)

            except Exception as e:
                st.error(f"❌ Error: {e}")

    # 📜 Show user-specific Q&A history
    st.markdown("---")
    st.subheader("📜 Your Past Q&A History")

    history = get_all_history(user_id)
    if history:
        for timestamp, q, a in history:
            with st.expander(f"🔎 {q} ({timestamp})"):
                st.write(a)
    else:
        st.info("No history found.")

else:
    st.title("🔐 Please Sign In")
    st.info("Use the login button above to get started.")
