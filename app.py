# app.py
import streamlit as st
from streamlit_auth0 import login_button
from agent_core import create_agent
from history import log_qa, get_all_history, init_db

# ---------- Setup ----------
st.set_page_config(page_title="Web Research Agent", layout="centered")
init_db()

# ---------- Auth0 Login ----------
user_info = login_button(
    client_id=st.secrets["AUTH0_CLIENT_ID"],
    domain=st.secrets["AUTH0_DOMAIN"],
    redirect_uri=st.secrets["AUTH0_CALLBACK_URL"]
)

# Store user info in session state
if user_info:
    st.session_state["user"] = user_info

# ---------- Authenticated UI ----------
if "user" in st.session_state:
    user = st.session_state["user"]
    user_id = user["sub"]

    st.title("🌐 Web Research Agent")
    st.markdown(f"👋 Welcome, **{user.get('name', 'User')}**")

    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    st.write("Ask a question and get researched answers using web + Gemini AI.")

    question = st.text_input("🔍 Enter your research question", autocomplete="off")
    agent = create_agent(verbose=False)

    if st.button("Get Answer") and question:
        with st.spinner("Thinking..."):
            try:
                response = agent.run(question)
                st.success("✅ Answer:")
                st.write(response)
                log_qa(question, response, user_id=user_id)
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ---------- History ----------
    st.markdown("---")
    st.subheader("📜 Your Past Q&A History")
    history = get_all_history(user_id=user_id)

    if history:
        for timestamp, q, a in history:
            with st.expander(f"🔎 {q} ({timestamp})"):
                st.write(a)
    else:
        st.info("No history found.")

# ---------- Not Logged In ----------
else:
    st.title("🔐 Please Sign In")
    st.info("You must log in to use the Web Research Agent.")
