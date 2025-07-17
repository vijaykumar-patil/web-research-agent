import streamlit as st
from streamlit_auth0 import login_button
from agent_core import create_agent
from history import log_qa, get_all_history, init_db
import os

# Read from environment variables or Streamlit secrets
client_id = st.secrets["AUTH0_CLIENT_ID"]
client_secret = st.secrets["AUTH0_CLIENT_SECRET"]  # not used by login_button but needed for token exchange (keep)
domain = st.secrets["AUTH0_DOMAIN"]
redirect_uri = st.secrets["AUTH0_CALLBACK_URL"]

# 🔐 Auth0 Login
user_info = login_button(client_id=client_id, domain=domain)

if user_info is None:
    st.warning("Please login to continue.")
    st.stop()

# ✅ Authenticated user
st.success(f"Logged in as {user_info['name']}")

# ---- Your existing app logic below ----

st.set_page_config(page_title="Web Research Agent", layout="centered")
st.title("🌐 Web Research Agent")
st.write("Ask a question and get researched answers using web + Gemini AI.")

init_db()
question = st.text_input("🔍 Enter your research question", autocomplete="off")
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
