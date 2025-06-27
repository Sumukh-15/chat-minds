# === ChatMinds — Local AI ChatBot with Login, Logout, and Memory ===

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# ----------------- Load Credentials from config.yaml -----------------
with open("config.yaml") as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# ----------------- Login Interface -----------------
name, authentication_status, username = authenticator.login('Login', location='sidebar')



if authentication_status:
    # ---------------- Sidebar ----------------
    st.sidebar.title("👤 User Panel")
    st.sidebar.success(f"Logged in as: {name}")
    authenticator.logout("🔒 Logout", "sidebar")
    st.sidebar.markdown("---")
    st.sidebar.info("This AI chat runs fully offline using the `mistral` model from Ollama.")

        # Add clear chat button in sidebar
    with st.sidebar:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history.clear()
            st.experimental_rerun()

    # ---------------- Model Loading (Cached) ----------------
    @st.cache_resource
    def load_model():
        return OllamaLLM(model="mistral")

    llm = load_model()

    # ---------------- Prompt Template ----------------
    prompt = PromptTemplate(
        input_variables=["chat_history", "question"],
        template=(
            "You are a helpful assistant. Continue the conversation.\n\n"
            "Previous Conversation:\n{chat_history}\n"
            "User: {question}\nAI:"
        )
    )

    # ---------------- Chat Memory ----------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ChatMessageHistory()

    # ---------------- Response Generator ----------------
    def run_chain(question):
        chat_history_text = '\n'.join(
            [f"{msg.type.capitalize()}: {msg.content}" for msg in st.session_state.chat_history.messages]
        )
        response = llm.invoke(prompt.format(chat_history=chat_history_text, question=question))
        st.session_state.chat_history.add_user_message(question)
        st.session_state.chat_history.add_ai_message(response)
        return response

    # ---------------- UI Layout ----------------
    st.title("🤖 ChatMinds — Local AI")
    user_input = st.chat_input("Ask your question...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        ai_response = run_chain(user_input)

        with st.chat_message("ai"):
            st.markdown(ai_response)

    # ---------------- Full Chat History ----------------
    with st.expander("📜 View Full Chat Log"):
        for msg in st.session_state.chat_history.messages:
            st.write(f"**{msg.type.capitalize()}**: {msg.content}")

elif authentication_status is False:
    st.error("❌ Incorrect username or password.")

elif authentication_status is None:
    st.warning("⚠️ Please enter your login credentials.")
