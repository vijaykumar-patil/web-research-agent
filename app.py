import streamlit as st
from streamlit_auth0 import login_button
from agent_core import create_agent, run_with_logging
from history import log_qa, get_all_history, init_db

# Page settings
st.set_page_config(page_title="Web Research Agent", layout="centered")
init_db()

# Auth0 login
user_info = login_button(
    client_id=st.secrets["AUTH0_CLIENT_ID"],
    domain=st.secrets["AUTH0_DOMAIN"],
    key="auth0_login"
)

if user_info:
    st.session_state["user"] = user_info
    user_id = user_info["sub"]

    st.title("🌐 Web Research Agent")
    st.markdown(f"👋 Welcome, **{user_info.get('name', 'User')}**")

    if st.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

    # Research input
    question = st.text_input("🔍 Enter your research question")
    agent = create_agent(verbose=False)

    if st.button("Get Answer") and question:
        with st.spinner("Thinking..."):
            try:
                result = run_with_logging(agent, question, user_id=user_id)
                answer = result.get("answer", "No answer provided.")
                sources = result.get("sources", [])
                confidence = result.get("confidence", 0.0)

                # Display result
                st.success("✅ Answer:")
                st.write(answer)

                st.markdown("#### 🔗 Sources")
                if sources:
                    for src in sources:
                        st.markdown(f"- [{src}]({src})")
                else:
                    st.info("No sources were detected.")

                st.markdown(f"#### 📊 Confidence Level: **{confidence * 100:.1f}%**")

                # Store in DB
                log_qa(question, answer, user_id=user_id)

            except Exception as e:
                st.error(f"❌ Error: {e}")

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
