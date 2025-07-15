# 💼 AI Interview Simulator

An AI-powered interactive mock interview platform built with **Streamlit**, **Google Gemini API**, and **Firebase Authentication**. This app simulates beginner-level mock interviews for roles such as Software Engineer, Data Scientist, Product Manager, and more — providing real-time feedback, follow-up questions, and performance analysis.

---

## 🔥 Features

- 🎯 Role-based mock interviews (e.g., DevOps, HR, UX Designer, etc.)
- 🤖 AI-generated interview questions & follow-ups using Google Gemini API
- 💬 Dynamic chat UI built with Streamlit
- 📊 Performance analysis with feedback and scoring charts
- 🔐 Firebase Authentication for secure login
- 💾 Downloadable interview transcript

---


## 🚀 Setup Instructions

1. **Clone the repo**
   
   git clone https://github.com/yourusername/AI-Interview-Simulator.git
   cd AI-Interview-Simulator
   

3. **Create a virtual environment & activate it**

   python -m venv venv
   .\venv\Scripts\Activate.ps1       # On PowerShell


4. **Install dependencies**

   pip install -r requirements.txt


5. **Add your Gemini API Key**
   Inside `app.py`:

   genai.configure(api_key="your_google_gemini_api_key")


6. **Add Firebase config**
   Inside your Firebase setup block, add your Firebase Web SDK configuration.

7. **Run the app**

   streamlit run app.py

---

## 📦 Requirements

Dependencies listed in [`requirements.txt`](./requirements.txt). Includes:

* streamlit
* firebase-admin
* pyrebase
* google-generativeai
* plotly
* regex

---
## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python-based UI)
- **Backend**: Google Generative AI (Gemini API)
- **Authentication**: Firebase Auth (Email/Password)
- **Visualization**: Plotly (radar & bar charts)

---


## 🙌 Acknowledgments

* Google Gemini API
* Streamlit Team
* Firebase by Google
