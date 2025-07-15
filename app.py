import streamlit as st
import google.generativeai as genai
import time
import plotly.graph_objects as go
import re
import os
import requests
from google.api_core.exceptions import ResourceExhausted

# --- Firebase Auth Setup ---
FIREBASE_API_KEY = "AIzaSyCO9W-qE9mSXJebEi-S4Phm_YRvqvOBSNc"
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts"

def firebase_login(email, password):
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    return response.json()

def firebase_register(email, password):
    url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    return response.json()

# --- Gemini API Config ---
genai.configure(api_key="AIzaSyDa35QEx4EPFo2uaZEwi5siYkqQ6wrnhcE") 

@st.cache_resource
def get_model():
    return genai.GenerativeModel("gemini-1.5-flash")

model = get_model()

def safe_generate_content(prompt):
    try:
        return model.generate_content(prompt).text.strip()
    except ResourceExhausted:
        st.error("❌ API quota exceeded. Try again after 24 hours or upgrade your API plan.")
        return "⚠️ API quota exceeded. Try again later."
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
        return "⚠️ An unexpected error occurred."

# --- Interview Roles ---
ROLES = {
    "GDG Lead": "Beginner questions on community building, event planning, leadership, and outreach.",
    "Software Engineer": "Beginner-level questions about programming, basic algorithms, and problem-solving.",
    "Data Scientist": "Entry-level questions on statistics, machine learning, and data analysis.",
    "Product Manager": "Simple questions on product thinking, prioritization, and user empathy.",
    "HR Manager": "Basic questions on recruitment, employee relations, and communication.",
    "UX Designer": "Beginner questions on design principles, user research, and prototyping.",
    "DevOps Engineer": "Questions on CI/CD, deployment, and system monitoring.",
    "QA Engineer": "Questions on testing fundamentals and automation basics.",
    "Cloud Engineer": "Questions on cloud services, basic architecture, and scalability.",
    "Frontend Developer": "Beginner questions about HTML, CSS, JavaScript, and UI frameworks.",
    "Backend Developer": "Questions about APIs, databases, and server-side logic."
}

def generate_easy_question(role, previous_qs=None):
    history = "\n".join(previous_qs) if previous_qs else ""
    prompt = (
        f"You are a professional {role} conducting a beginner-level mock interview.\n"
        f"Ask one simple and **new** question relevant to the role. "
        f"**Do NOT repeat or rephrase any of these previous questions**:\n{history}\n"
        "Return only the question text."
    )
    return safe_generate_content(prompt)

def generate_followup_response(role, user_answer):
    prompt = (
        f"You are a professional {role} interviewer.\n"
        f"Candidate answered: {user_answer}\n"
        "Provide a short, constructive reply with a tip or suggestion. Keep it concise."
    )
    return safe_generate_content(prompt)

def provide_feedback(chat_history):
    transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history])
    prompt = (
        "You are an AI interview coach. Analyze this transcript and provide:\n"
        "1. One-paragraph performance summary\n"
        "2. 3 strengths\n"
        "3. 3 suggestions for improvement\n"
        "4. Scores (1-10) for confidence, clarity, and knowledge\n\n"
        f"Transcript:\n{transcript}"
    )
    return safe_generate_content(prompt)

def extract_scores(text):
    matches = re.findall(r"(confidence|clarity|knowledge)[^\d]*(\d+)", text, re.IGNORECASE)
    scores = {"Confidence": 0, "Clarity": 0, "Knowledge": 0}
    for category, value in matches:
        scores[category.capitalize()] = int(value)
    return scores

def display_message(role, content):
    color = "#E6F0FF" if role == "assistant" else "#F5F5F5"
    font_weight = "bold" if role == "assistant" else "normal"
    font_size = "18px" if role == "assistant" else "16px"
    with st.chat_message(role):
        st.markdown(
            f"<div style='background-color: {color}; padding: 12px 20px; border-radius: 12px; "
            f"font-size: {font_size}; font-weight: {font_weight}; color: #000;'>{content}</div>",
            unsafe_allow_html=True
        )

def answer_the_question(role, question):
    prompt = (
        f"You are a professional {role}.\n"
        f"Here is a beginner-level interview question: '{question}'\n"
        "Provide a strong sample answer in 4-5 lines."
    )
    return safe_generate_content(prompt)

# --- Main App ---
def main():
    st.set_page_config("Interview Simulator", page_icon="💻", layout="wide")
    with st.sidebar:
        st.title("Interview Settings")
        selected_role = st.selectbox("Role", list(ROLES.keys()))
        total_questions = st.slider("Number of Questions", 3, 20, 5)
        timer_seconds = st.slider("Time per Question (sec)", 10, 120, 60)
        if st.button("Reset Interview"):
            st.session_state.clear()

    st.title(f"AI Interview – {selected_role}")
    st.markdown("Answer the questions below. You can also skip or ask the AI to answer.")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.asked_questions = []
        st.session_state.question_index = -1
        st.session_state.feedback_given = False
        st.session_state.feedback_text = ""
        st.session_state.followup_count = 0
        st.session_state.followup_unlocked = False
        st.session_state.show_followup_buttons = False
        st.session_state.scores_progression = []

    if st.session_state.question_index == -1:
        st.session_state.question_index += 1
        question = generate_easy_question(selected_role)
        st.session_state.asked_questions.append(question)
        st.session_state.messages.append({"role": "assistant", "content": question})

    for msg in st.session_state.messages:
        display_message(msg["role"], msg["content"])

    if st.session_state.question_index < total_questions - 1:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            if st.button("🆕 Next Question"):
                st.session_state.question_index += 1
                st.session_state.followup_count = 0
                st.session_state.followup_unlocked = False
                st.session_state.show_followup_buttons = False
                question = generate_easy_question(selected_role, st.session_state.asked_questions)
                st.session_state.asked_questions.append(question)
                st.session_state.messages.append({"role": "assistant", "content": question})
                display_message("assistant", question)

        with col2:
            if st.button("🤖 Answer it for me"):
                if st.session_state.question_index >= 0:
                    question = st.session_state.asked_questions[-1]
                    ai_answer = answer_the_question(selected_role, question)
                    st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                    display_message("assistant", ai_answer)

    if 0 <= st.session_state.question_index < total_questions:
        user_input = st.chat_input("Your answer... (type 'answer' or 'skip')")
        if user_input is not None:
            lowered = user_input.strip().lower()
            st.session_state.messages.append({"role": "user", "content": user_input})
            display_message("user", user_input)

            if lowered in ["", "i don't know", "idk", "not sure", "can't answer", "skip"]:
                st.info("Question skipped.")
                st.session_state.question_index += 1
                st.session_state.followup_count = 0
                st.session_state.followup_unlocked = False
                st.session_state.show_followup_buttons = False
                if st.session_state.question_index < total_questions:
                    question = generate_easy_question(selected_role, st.session_state.asked_questions)
                    st.session_state.asked_questions.append(question)
                    st.session_state.messages.append({"role": "assistant", "content": question})
                    display_message("assistant", question)

            elif lowered in ["answer", "show answer", "example answer"]:
                question = st.session_state.asked_questions[-1]
                ai_answer = answer_the_question(selected_role, question)
                st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                display_message("assistant", ai_answer)

            else:
                reply = generate_followup_response(selected_role, user_input)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                display_message("assistant", reply)

                st.session_state.followup_count += 1
                if st.session_state.followup_count <= 3 or st.session_state.followup_unlocked:
                    followup_prompt = (
                        f"As a {selected_role} interviewer, ask a follow-up question based on this answer: '{user_input}'."
                    )
                    followup_question = safe_generate_content(followup_prompt)
                    st.session_state.messages.append({"role": "assistant", "content": followup_question})
                    display_message("assistant", followup_question)
                elif st.session_state.followup_count == 4:
                    st.info("✅ You've reached 3 AI follow-ups. Choose your next step:")
                    st.session_state.show_followup_buttons = True

    if st.session_state.show_followup_buttons:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 Next Question (After Follow-ups)"):
                st.session_state.question_index += 1
                st.session_state.followup_count = 0
                st.session_state.show_followup_buttons = False
                st.session_state.followup_unlocked = False
                if st.session_state.question_index < total_questions:
                    question = generate_easy_question(selected_role, st.session_state.asked_questions)
                    st.session_state.asked_questions.append(question)
                    st.session_state.messages.append({"role": "assistant", "content": question})
                    display_message("assistant", question)

        with col2:
            if st.button("🔄 Ask More Follow-ups"):
                st.session_state.followup_unlocked = True
                st.session_state.show_followup_buttons = False
                st.rerun()

    if st.session_state.question_index == total_questions - 1 and not st.session_state.feedback_given:
        if st.button("✅ Get Feedback"):
            with st.spinner("Analyzing your interview..."):
                feedback = provide_feedback(st.session_state.messages)
                st.session_state.feedback_given = True
                st.session_state.feedback_text = feedback
                st.session_state.messages.append({"role": "assistant", "content": feedback})

    if st.session_state.feedback_given:
        st.subheader("Interview Feedback")
        st.markdown(st.session_state.feedback_text)

        scores = extract_scores(st.session_state.feedback_text)
        labels = list(scores.keys())
        values = list(scores.values())

        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name='Scores'
        ))
        radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=400)
        st.plotly_chart(radar, use_container_width=True)

        bar = go.Figure([go.Bar(x=labels, y=values, marker_color='steelblue')])
        bar.update_layout(yaxis_title="Score (1-10)", height=400)
        st.plotly_chart(bar, use_container_width=True)

    if st.button("📄 Download Full Transcript"):
        full_transcript = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
        st.download_button("📥 Download Full Transcript", data=full_transcript, file_name="interview_transcript.txt", mime="text/plain")

# --- Login Page Wrapper ---
def login_page():
    st.set_page_config("Login | Interview App", page_icon="🔐")
    st.title("🔐 Login to AI Interview Simulator")
    login_mode = st.radio("Choose", ["Login", "Register"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if login_mode == "Login":
            result = firebase_login(email, password)
        else:
            result = firebase_register(email, password)

        if "error" in result:
            st.error(f"❌ {result['error']['message']}")
        else:
            st.success(f"✅ {login_mode} successful!")
            st.session_state["user"] = email
            st.rerun()

# --- Auth Gate ---
if "user" not in st.session_state:
    login_page()
else:
    main()
