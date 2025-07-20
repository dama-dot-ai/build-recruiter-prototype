import streamlit as st
import openai
import gspread
import pandas as pd
import json

# Load secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
GSHEET_URL = st.secrets["GSHEET_URL"]

# Set page config
st.set_page_config(page_title="BUILD - Recruiter Assistant", layout="wide")

# Session state setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []

# Recruiter credentials
users = {
    "daniel": {"name": "Daniel M", "password": "godblessdama123$$"},
    "alice": {"name": "Alice Sharon", "password": "godblessdama123$$"},
    "neelima": {"name": "Neelima", "password": "godblessdama123$$"},
    "romilton": {"name": "Romilton", "password": "godblessdama123$$"},
}

# Login UI
def login():
    st.title("Welcome to Dama.AI")
    st.write("Recruiter Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid credentials")

# Main UI
def main_app():
    st.sidebar.title("Navigation")
    st.sidebar.write(f"👤 {users[st.session_state.username]['name']}")
    st.sidebar.markdown("---")
    nav = st.sidebar.radio("Menu", ["Chat", "Job Reqs", "Candidates"])

    st.title("BUILD Recruiter Assistant")
    col1, col2 = st.columns([2, 1])

    # Load Google Sheet
    gc = gspread.service_account(filename="service_account.json") if "GOOGLE_SERVICE_ACCOUNT" in st.secrets else gspread.public()
    sheet = gc.open_by_url(GSHEET_URL)
    job_reqs = pd.DataFrame(sheet.worksheet("Job_Requisitions").get_all_records())
    candidates = pd.DataFrame(sheet.worksheet("Candidates").get_all_records())

    with col1:
        prompt = st.text_input("Type your prompt here...")
        if st.button("Submit") and prompt:
            # GPT call
            st.session_state.history.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": h["role"], "content": h["content"]}
                        for h in st.session_state.history
                    ],
                    temperature=0.4,
                )
                reply = response["choices"][0]["message"]["content"]
                st.session_state.history.append({"role": "assistant", "content": reply})

        for msg in st.session_state.history:
            st.markdown(f"**{msg['role'].capitalize()}**: {msg['content']}")

    with col2:
        st.subheader("📋 Context")
        st.dataframe(job_reqs[job_reqs["Primary Recruiter"] == users[st.session_state.username]["name"]])

# Run App
if not st.session_state.logged_in:
    login()
else:
    main_app()
