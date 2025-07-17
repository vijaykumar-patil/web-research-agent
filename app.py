# app.py
import streamlit as st
from streamlit_auth0 import login_button   # pip install streamlit-auth0
from agent_core import create_agent
from history import init_db, log_qa, get_user_history, get_all_history

# --- Auth0 login ---
user_info = login_button()

st.set_page_config(page_title="Web Research Agent", layout="centered")

if not user_info:
    st.warning("Please log in (Google/GitHub via Auth0) to use the Web Research Agent.")
    st.stop()

# Logged in:
user_name = user_info.get("name") or user_info.get("nickname") or "User"
user_id = user_info.get("email") or user_info.get("sub")  # email preferred

st.sidebar.success(f"Logged in as {user_name}")
# streamlit-auth0 provides a logout URL in user_info if configured; you can show a button:
logout_url = user_info.get("end_session_endpoint")
if logout_url:
    st.sidebar.markdown(f"[Logout]({logout_url})", unsafe_allow_html=True)

# --- App UI ---
st.title("🌐 Web Research Agent")
st.write("Ask a question and get researched answers using web + Gemini AI.")

# Ensure DB ready
init_db()

question = st.text_input("🔍 Enter your research question", autocomplete="off")
agent = create_agent(verbose=False)

if st.button("Get Answer") and question:
    with st.spinner("Thinking..."):
        try:
            response = agent.run(question)
            st.success("✅ Answer:")
            st.write(response)
            # Log with user_id
            log_qa(question, response, user_id=user_id)
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.markdown("---")
st.subheader("📜 Your Q&A History")

history_rows = get_user_history(user_id)
if not history_rows:
    st.info("No history yet. Ask something above!")
else:
    for timestamp, _user, q, a in history_rows:
        with st.expander(f"🔎 {q} ({timestamp})"):
            st.write(a)

# Optional global history (admin only)
if st.sidebar.checkbox("Show ALL history (admin)"):
    all_rows = get_all_history(limit=100)
    for timestamp, _user, q, a in all_rows:
        with st.expander(f"👥 {_user} · {q} ({timestamp})"):
            st.write(a)
