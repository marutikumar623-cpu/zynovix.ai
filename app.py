600import streamlit as st
from groq import Groq

# ── PAGE CONFIG ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0F0F1A !important;
    color: #E8E8F0 !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background-color: #1A1A2E !important;
    border-right: 1px solid #2A2A4A;
}
.chat-user {
    background: linear-gradient(135deg, #6C63FF22, #6C63FF11);
    border: 1px solid #6C63FF44;
    border-radius: 18px 18px 4px 18px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #E8E8F0;
}
.chat-ai {
    background: #1A1A2E;
    border: 1px solid #2A2A4A;
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #E8E8F0;
    line-height: 1.8;
    white-space: pre-wrap;
}
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #48CFAD) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100%;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #16213E !important;
    color: #E8E8F0 !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 10px !important;
}
.stSelectbox > div > div {
    background-color: #16213E !important;
    color: #E8E8F0 !important;
    border: 1px solid #2A2A4A !important;
    border-radius: 10px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #1A1A2E !important;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #9090B0 !important;
    border-radius: 8px !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6C63FF, #48CFAD) !important;
    color: white !important;
}
hr { border-color: #2A2A4A !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #E8E8F0 !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "api_configured" not in st.session_state:
    st.session_state.api_configured = False
if "groq_client" not in st.session_state:
    st.session_state.groq_client = None

# ── GROQ API CALL ────────────────────────────────────────────────────
def call_groq(messages, system_prompt):
    response = st.session_state.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ── SYSTEM PROMPT ────────────────────────────────────────────────────
def get_system_prompt(subject, level, language):
    lang_map = {
        "Hinglish (Hindi + English)": "Answer in Hinglish - Hindi for explanation, English for technical terms.",
        "Hindi": "Answer completely in Hindi (Devanagari script).",
        "English": "Answer in clear simple English.",
        "Urdu": "Answer in Urdu language.",
    }
    lang_instr = lang_map.get(language, "Answer in Hinglish.")

    prompt = "You are an expert AI Study Assistant for students in India.\n"
    prompt += "Subject: " + subject + "\n"
    prompt += "Student Level: " + level + "\n"
    prompt += "Language: " + lang_instr + "\n"
    prompt += "Rules:\n"
    prompt += "1. Always explain step-by-step\n"
    prompt += "2. Use simple language students can understand\n"
    prompt += "3. Give real-life examples wherever possible\n"
    prompt += "4. For math/science: show complete working solution\n"
    prompt += "5. End with a short summary or key points\n"
    prompt += "6. Use emojis to make it engaging\n"
    prompt += "7. Answer each part separately if multiple questions\n"
    prompt += "8. Always be encouraging and supportive"
    return prompt

# ── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:1rem 0'>"
        "<div style='font-size:2.5rem'>🎓</div>"
        "<div style='font-weight:700;font-size:1.2rem;color:#6C63FF'>AI Study Assistant</div>"
        "<div style='color:#9090B0;font-size:0.8rem'>Powered by Groq AI ⚡</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("**🔑 Groq API Key**")
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed"
    )

    if api_key:
        try:
            client = Groq(api_key=api_key)
            st.session_state.groq_client = client
            st.session_state.api_configured = True
            st.success("✅ Connected!")
        except Exception:
            st.error("❌ Invalid API key")
            st.session_state.api_configured = False
            st.session_state.groq_client = None

    st.markdown(
        "<div style='color:#9090B0;font-size:0.75rem;text-align:center'>"
        "Free key: <a href='https://console.groq.com' target='_blank' style='color:#6C63FF'>console.groq.com</a>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("**📚 Subject**")
    subject = st.selectbox(
        "Subject",
        ["General", "Mathematics", "Physics", "Chemistry", "Biology",
         "History", "Geography", "Computer Science", "English",
         "Economics", "Political Science", "Hindi", "Urdu", "Other"],
        label_visibility="collapsed"
    )

    st.markdown("**🌐 Language**")
    language = st.selectbox(
        "Language",
        ["Hinglish (Hindi + English)", "Hindi", "English", "Urdu"],
        label_visibility="collapsed"
    )

    st.markdown("**🎯 Level**")
    level = st.selectbox(
        "Level",
        ["Class 6-8", "Class 9-10", "Class 11-12",
         "Undergraduate", "JEE/NEET/UPSC", "Any Level"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<div style='background:#16213E;border:1px solid #2A2A4A;border-radius:10px;"
            "padding:10px;text-align:center'>"
            "<div style='color:#6C63FF;font-size:1.5rem;font-weight:700'>"
            + str(st.session_state.total_questions) +
            "</div><div style='color:#9090B0;font-size:0.8rem'>Questions</div></div>",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            "<div style='background:#16213E;border:1px solid #2A2A4A;border-radius:10px;"
            "padding:10px;text-align:center'>"
            "<div style='color:#48CFAD;font-size:1.5rem;font-weight:700'>"
            + str(len(st.session_state.messages)) +
            "</div><div style='color:#9090B0;font-size:0.8rem'>Messages</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.rerun()

    st.markdown(
        "<div style='color:#9090B0;font-size:0.75rem;text-align:center;padding-top:0.5rem'>"
        "⚡ Model: Llama 3.3 70B (Groq)<br>"
        "🔒 Data session mein save hota hai"
        "</div>",
        unsafe_allow_html=True
    )

# ── HEADER ───────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;padding:1.5rem 0 1rem 0'>"
    "<h1 style='background:linear-gradient(135deg,#6C63FF,#48CFAD);"
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    "font-family:Space Grotesk,sans-serif;font-size:2.4rem;font-weight:700'>"
    "🎓 AI Study Assistant</h1>"
    "<p style='color:#9090B0'>Har sawaal ka jawab • Step-by-step solutions • Free forever</p>"
    "<span style='background:#6C63FF22;border:1px solid #6C63FF44;border-radius:20px;"
    "padding:0.2rem 0.7rem;font-size:0.78rem;color:#48CFAD;margin:0.2rem'>✨ Step-by-step</span>"
    "<span style='background:#6C63FF22;border:1px solid #6C63FF44;border-radius:20px;"
    "padding:0.2rem 0.7rem;font-size:0.78rem;color:#48CFAD;margin:0.2rem'>📝 Exam Help</span>"
    "<span style='background:#6C63FF22;border:1px solid #6C63FF44;border-radius:20px;"
    "padding:0.2rem 0.7rem;font-size:0.78rem;color:#48CFAD;margin:0.2rem'>🌐 Hindi + English</span>"
    "<span style='background:#6C63FF22;border:1px solid #6C63FF44;border-radius:20px;"
    "padding:0.2rem 0.7rem;font-size:0.78rem;color:#48CFAD;margin:0.2rem'>⚡ Groq Fast AI</span>"
    "</div>",
    unsafe_allow_html=True
)

# ── TABS ─────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Chat & Ask", "🛠️ Quick Tools"])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ════════════════════════════════════════════════════════════════════
with tab1:
    if not st.session_state.api_configured:
        st.markdown(
            "<div style='background:#1A1A2E;border:1px dashed #6C63FF66;"
            "border-radius:16px;padding:2rem;text-align:center;margin:2rem 0'>"
            "<div style='font-size:3rem'>🔑</div>"
            "<h3 style='color:#E8E8F0'>Sidebar mein API Key Dalo</h3>"
            "<p style='color:#9090B0'>Groq API key bilkul <strong style=\"color:#48CFAD\">FREE</strong> milti hai!</p>"
            "<div style='background:#0F0F1A;border-radius:8px;padding:1rem;"
            "font-family:monospace;color:#48CFAD;margin-top:1rem'>"
            "console.groq.com → API Keys → Create Key → Free!"
            "</div></div>",
            unsafe_allow_html=True
        )
    else:
        # Quick buttons
        st.markdown("**⚡ Quick Start:**")
        qc1, qc2, qc3, qc4 = st.columns(4)

        quick_list = [
            (qc1, "➕ Math Solve", "Quadratic equation solve karo step by step: x^2 + 5x + 6 = 0"),
            (qc2, "🔬 Concept", "Photosynthesis kya hoti hai? Simple mein explain karo"),
            (qc3, "📝 Notes", "Important topics ke short notes banao subject: " + subject),
            (qc4, "🎯 Exam Tips", "Board exam ke liye best study tips kya hain?"),
        ]

        for col, label, prompt in quick_list:
            with col:
                if st.button(label, key="quick_" + label):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.total_questions += 1
                    with st.spinner("🤔 Soch raha hoon..."):
                        try:
                            reply = call_groq(
                                list(st.session_state.messages),
                                get_system_prompt(subject, level, language)
                            )
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.session_state.messages.append({"role": "assistant", "content": "Error: " + str(e)})
                    st.rerun()

        st.markdown("---")

        # Chat history
        if not st.session_state.messages:
            st.markdown(
                "<div style='text-align:center;padding:3rem 0;color:#9090B0'>"
                "<div style='font-size:3rem'>👋</div>"
                "<h3 style='color:#E8E8F0'>Namaste! Main tumhara Study Assistant hoon</h3>"
                "<p>Koi bhi sawaal poocho — Math, Science, History, ya kuch bhi!</p>"
                "<p style='font-size:0.85rem'>Upar quick buttons use karo ya neeche type karo 👇</p>"
                "</div>",
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        "<div class='chat-user'>"
                        "<strong style='color:#48CFAD'>Tum 👤</strong><br>"
                        + msg["content"] +
                        "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        "<div class='chat-ai'>"
                        "<strong style='color:#6C63FF'>🤖 AI Assistant</strong><br>"
                        + msg["content"] +
                        "</div>",
                        unsafe_allow_html=True
                    )

        # Input
        st.markdown("<br>", unsafe_allow_html=True)
        in_col, btn_col = st.columns([5, 1])
        with in_col:
            user_input = st.text_area(
                "Sawaal",
                placeholder="Apna sawaal likhoo... (Enter = send, Shift+Enter = new line)",
                height=80,
                key="chat_input",
                label_visibility="collapsed"
            )
        with btn_col:
            st.markdown("<br>", unsafe_allow_html=True)
            send_clicked = st.button("📤 Send", key="send_btn")

        if send_clicked and user_input.strip():
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            st.session_state.total_questions += 1
            with st.spinner("🤔 Soch raha hoon..."):
                try:
                    reply = call_groq(
                        list(st.session_state.messages),
                        get_system_prompt(subject, level, language)
                    )
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "❌ Error: " + str(e) + "\n\nAPI key check karo."
                    })
            st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 2 — QUICK TOOLS
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🛠️ Quick Study Tools")

    if not st.session_state.api_configured:
        st.warning("⚠️ Pehle sidebar mein Groq API key enter karo")
    else:
        t1, t2, t3, t4 = st.tabs(["📝 Notes", "❓ Quiz", "💡 Concept", "🔢 Math"])

        # NOTES
        with t1:
            st.markdown("**Topic ke smart notes banao instantly!**")
            notes_topic = st.text_input(
                "Topic",
                placeholder="e.g., Photosynthesis, French Revolution, Pythagoras Theorem",
                key="notes_topic_input"
            )
            notes_type = st.radio(
                "Notes type:",
                ["Short Summary", "Detailed Notes", "Bullet Points", "Mind Map Format"],
                horizontal=True
            )
            if st.button("📝 Notes Banao!", key="notes_btn"):
                if notes_topic.strip():
                    p = "Create " + notes_type + " for topic: " + notes_topic
                    p += ". Subject: " + subject
                    p += ". Level: " + level
                    p += ". Language: " + language
                    p += ". Make notes clear, well structured, include key points, dates and formulas if relevant, easy to memorize."
                    with st.spinner("📝 Notes likh raha hoon..."):
                        try:
                            result = call_groq(
                                [{"role": "user", "content": p}],
                                get_system_prompt(subject, level, language)
                            )
                            st.markdown(
                                "<div class='chat-ai'>" + result + "</div>",
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("⚠️ Topic toh batao!")

        # QUIZ
        with t2:
            st.markdown("**Practice ke liye MCQ quiz banao!**")
            quiz_topic = st.text_input(
                "Quiz topic",
                placeholder="e.g., Newton's Laws, World War 2",
                key="quiz_topic_input"
            )
            num_q = st.slider("Kitne questions?", 3, 10, 5)
            if st.button("❓ Quiz Banao!", key="quiz_btn"):
                if quiz_topic.strip():
                    p = "Create " + str(num_q) + " MCQ questions on: " + quiz_topic
                    p += ". Subject: " + subject
                    p += ". Level: " + level
                    p += ". Language: " + language
                    p += ". Format each as: Q[n]. Question, then A) B) C) D) options, then Answer with correct option, then Explanation in 1-2 lines. Make questions progressively harder."
                    with st.spinner("❓ Quiz bana raha hoon..."):
                        try:
                            result = call_groq(
                                [{"role": "user", "content": p}],
                                get_system_prompt(subject, level, language)
                            )
                            st.markdown(
                                "<div class='chat-ai'>" + result + "</div>",
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("⚠️ Topic dalo!")

        # CONCEPT
        with t3:
            st.markdown("**Koi bhi concept simply samjho!**")
            concept = st.text_input(
                "Concept",
                placeholder="e.g., Osmosis, Derivatives, Democracy",
                key="concept_input"
            )
            explain_style = st.radio(
                "Style:",
                ["Simple (Bilkul Simple)", "Standard", "Deep Dive with Examples"],
                horizontal=True
            )
            if st.button("💡 Explain Karo!", key="concept_btn"):
                if concept.strip():
                    p = "Explain concept: " + concept
                    p += ". Style: " + explain_style
                    p += ". Subject: " + subject
                    p += ". Language: " + language
                    p += ". Include: definition, real life example, importance, common mistakes students make, and a memory trick."
                    with st.spinner("💡 Samjha raha hoon..."):
                        try:
                            result = call_groq(
                                [{"role": "user", "content": p}],
                                get_system_prompt(subject, level, language)
                            )
                            st.markdown(
                                "<div class='chat-ai'>" + result + "</div>",
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("⚠️ Concept likhoo!")

        # MATH
        with t4:
            st.markdown("**Math problems step-by-step solve karo!**")
            math_prob = st.text_area(
                "Math problem",
                placeholder="e.g., Solve: 3x^2 - 7x + 2 = 0\nor: Find area of circle with radius 7cm\nor: Integrate x^2 + 3x + 2",
         
