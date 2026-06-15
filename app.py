import streamlit as st
from groq import Groq
from PIL import Image
import io

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

  :root {
    --primary: #6C63FF;
    --secondary: #48CFAD;
    --bg-dark: #0F0F1A;
    --bg-card: #1A1A2E;
    --bg-input: #16213E;
    --text: #E8E8F0;
    --text-muted: #9090B0;
    --border: #2A2A4A;
    --accent: #FF6B6B;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-dark) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
  }

  [data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border);
  }

  .main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
  }

  .main-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6C63FF, #48CFAD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
  }

  .main-header p {
    color: var(--text-muted);
    font-size: 1rem;
  }

  .chat-bubble-user {
    background: linear-gradient(135deg, #6C63FF22, #6C63FF11);
    border: 1px solid #6C63FF44;
    border-radius: 18px 18px 4px 18px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    text-align: right;
    color: var(--text);
  }

  .chat-bubble-ai {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: var(--text);
    line-height: 1.7;
  }

  .feature-pill {
    display: inline-block;
    background: linear-gradient(135deg, #6C63FF33, #48CFAD22);
    border: 1px solid #6C63FF44;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #48CFAD;
    margin: 0.2rem;
  }

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    background-color: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
  }

  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px #6C63FF33 !important;
  }

  .stButton > button {
    background: linear-gradient(135deg, #6C63FF, #48CFAD) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
    width: 100%;
  }

  .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px #6C63FF55 !important;
  }

  .stSelectbox > div > div {
    background-color: var(--bg-input) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-card) !important;
    border-radius: 12px;
    gap: 4px;
    padding: 4px;
  }

  .stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 500;
  }

  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6C63FF, #48CFAD) !important;
    color: white !important;
  }

  .stat-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
  }

  .stat-box h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6C63FF, #48CFAD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }

  .stat-box p {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin: 0;
  }

  hr { border-color: var(--border) !important; }

  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--text) !important;
  }

  [data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
  }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "api_configured" not in st.session_state:
    st.session_state.api_configured = False
if "subject" not in st.session_state:
    st.session_state.subject = "General"
if "language" not in st.session_state:
    st.session_state.language = "Hinglish (Hindi + English)"
if "groq_client" not in st.session_state:
    st.session_state.groq_client = None

# ─── HELPER: Groq API call ────────────────────────────────────────────────────
def call_groq(messages, system_prompt):
    response = st.session_state.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}] + messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ─── HELPER: System prompt ────────────────────────────────────────────────────
def get_system_prompt(subject, level, language):
    lang_instruction = {
        "Hinglish (Hindi + English)": "Answer in Hinglish (mix of Hindi and English). Use Hindi for explanations and English for technical terms.",
        "Hindi (हिंदी)": "Answer completely in Hindi (Devanagari script).",
        "English": "Answer in clear, simple English.",
        "Urdu (اردو)": "Answer in Urdu language.",
    }.get(language, "Answer in Hinglish.")

    return f"""You are an expert AI Study Assistant for students in India.
Subject: {subject}
Student Level: {level}
Language instruction: {lang_instruction}

Your rules:
1. ALWAYS explain step-by-step (har step clearly explain karo)
2. Use simple language that students can understand
3. Give examples wherever possible
4. For math/science: show complete working/solution
5. End with a short summary or key points
6. Use emojis to make it engaging (but not too many)
7. If the question has multiple parts, answer each part separately
8. Always be encouraging and supportive
Format your answers clearly with headings where needed."""

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
      <div style='font-size:2.5rem;'>🎓</div>
      <div style='font-family: Space Grotesk; font-size:1.2rem; font-weight:700;
                  background: linear-gradient(135deg, #6C63FF, #48CFAD);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        AI Study Assistant
      </div>
      <div style='color:#9090B0; font-size:0.8rem;'>Powered by Groq AI ⚡</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # API Key
    st.markdown("**🔑 Groq API Key**")
    api_key = st.text_input(
        "Enter your API key",
        type="password",
        placeholder="gsk_...",
        help="Free key: console.groq.com",
        label_visibility="collapsed"
    )

    if api_key:
        try:
            client = Groq(api_key=api_key)
            st.session_state.groq_client = client
            st.session_state.api_configured = True
            st.success("✅ Connected!")
        except Exception as e:
            st.error("❌ Invalid API key")
            st.session_state.api_configured = False
            st.session_state.groq_client = None

    st.markdown("""
    <div style='color:#9090B0; font-size:0.75rem; text-align:center;'>
      Free key: <a href='https://console.groq.com' target='_blank'
      style='color:#6C63FF;'>console.groq.com</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Subject
    st.markdown("**📚 Subject**")
    subject = st.selectbox(
        "Choose subject",
        ["General", "Mathematics", "Physics", "Chemistry", "Biology",
         "History", "Geography", "Computer Science", "English", "Economics",
         "Political Science", "Hindi", "Urdu", "Sanskrit", "Other"],
        label_visibility="collapsed"
    )
    st.session_state.subject = subject

    # Language
    st.markdown("**🌐 Answer Language**")
    language = st.selectbox(
        "Choose language",
        ["Hinglish (Hindi + English)", "Hindi (हिंदी)", "English", "Urdu (اردو)"],
        label_visibility="collapsed"
    )
    st.session_state.language = language

    # Level
    st.markdown("**🎯 Study Level**")
    level = st.selectbox(
        "Choose level",
        ["Class 6-8", "Class 9-10 (Secondary)", "Class 11-12 (Senior Secondary)",
         "Undergraduate", "Competitive Exams (JEE/NEET/UPSC)", "Any Level"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='stat-box'>
          <h2>{st.session_state.total_questions}</h2>
          <p>Questions</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='stat-box'>
          <h2>{len(st.session_state.messages)}</h2>
          <p>Messages</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.rerun()

    st.markdown("""
    <div style='color:#9090B0; font-size:0.75rem; text-align:center; padding-top:0.5rem;'>
      🔒 Chat session mein save hoti hai<br>
      ⚡ Model: Llama 3.3 70B (Groq)
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN AREA ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
  <h1>🎓 AI Study Assistant</h1>
  <p>Har sawaal ka jawab • Step-by-step solutions • Free forever</p>
  <div style='margin-top:0.5rem;'>
    <span class='feature-pill'>✨ Step-by-step Solutions</span>
    <span class='feature-pill'>📝 Exam Help</span>
    <span class='feature-pill'>🌐 Hindi + English</span>
    <span class='feature-pill'>⚡ Groq Fast AI</span>
    <span class='feature-pill'>📱 Mobile Friendly</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Chat & Ask", "📋 Quick Tools"])

# ══════════════════════════════════════════════════════════════════════
# TAB 1: CHAT
# ══════════════════════════════════════════════════════════════════════
with tab1:
    if not st.session_state.api_configured:
        st.markdown("""
        <div style='background: #1A1A2E; border: 1px dashed #6C63FF66;
                    border-radius: 16px; padding: 2rem; text-align: center; margin: 2rem 0;'>
          <div style='font-size: 3rem;'>🔑</div>
          <h3 style='color: #E8E8F0;'>API Key Dalo Sidebar Mein</h3>
          <p style='color: #9090B0;'>Groq API key bilkul <strong style="color:#48CFAD;">FREE</strong> milti hai!</p>
          <p style='color: #9090B0;'>👈 Sidebar mein key enter karo, phir koi bhi sawaal poocho</p>
          <div style='background:#0F0F1A; border-radius:8px; padding:1rem; margin-top:1rem;
                      font-family:monospace; color:#48CFAD; font-size:0.9rem;'>
            console.groq.com → API Keys → Create Key → Free!
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Quick prompts
        st.markdown("**⚡ Quick Start — In pe click karo:**")
        qcol1, qcol2, qcol3, qcol4 = st.columns(4)
        quick_prompts = {
            qcol1: ("➕ Math solve", f"Ek quadratic equation solve karo step by step: x² + 5x + 6 = 0"),
            qcol2: ("🔬 Concept explain", f"Photosynthesis kya hoti hai? Simple mein explain karo"),
            qcol3: ("📝 Notes banao", f"{subject} ke important topics ke short notes banao"),
            qcol4: ("🎯 Exam tips", f"Board exam ke liye best study tips kya hain?"),
        }

        for col, (label, prompt) in quick_prompts.items():
            with col:
                if st.button(label, key=f"qp_{label}"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.total_questions += 1
                    with st.spinner("🤔 Soch raha hoon..."):
                        try:
                            history = [{"role": m["role"], "content": m["content"]}
                                       for m in st.session_state.messages]
                            reply = call_groq(history, get_system_prompt(subject, level, language))
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
                    st.rerun()

        st.markdown("---")

        # Chat history
        if not st.session_state.messages:
            st.markdown("""
            <div style='text-align:center; padding: 3rem 0; color: #9090B0;'>
              <div style='font-size: 3rem; margin-bottom: 1rem;'>👋</div>
              <h3 style='color:#E8E8F0;'>Namaste! Main tumhara Study Assistant hoon</h3>
              <p>Koi bhi sawaal poocho — Math, Science, History, ya kuch bhi!</p>
              <p style='font-size:0.85rem;'>Upar quick buttons use karo ya neeche type karo 👇</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class='chat-bubble-user'>
                      <strong>Tum 👤</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-bubble-ai'>
                      <strong>🤖 AI Assistant</strong><br>{msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # Input area
        st.markdown("<br>", unsafe_allow_html=True)
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_area(
                "Apna sawaal likhoo...",
                placeholder=f"Example: '{subject} mein Newton ka pehla niyam kya hai?' ya '2x + 5 = 15 solve karo'",
                height=80,
                key="chat_input",
                label_visibility="collapsed"
            )
        with btn_col:
            st.markdown("<br>", unsafe_allow_html=True)
            send_clicked = st.button("📤 Send", key="send_btn")

        if send_clicked and user_input.strip():
            user_msg = user_input.strip()
            st.session_state.messages.append({"role": "user", "content": user_msg})
            st.session_state.total_questions += 1

            with st.spinner("🤔 Soch raha hoon..."):
                try:
                    history = [{"role": m["role"], "content": m["content"]}
                               for m in st.session_state.messages]
                    reply = call_groq(history, get_system_prompt(subject, level, language))
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {str(e)}\n\nPlease check your API key."
                    })

            st.rerun()

# ══════════════════════════════════════════════════════════════════════
# TAB 2: QUICK TOOLS
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🛠️ Quick Study Tools")

    if not st.session_state.api_configured:
        st.warning("⚠️ Pehle sidebar mein Groq API key enter karo")
    else:
        tool_tabs = st.tabs([
            "📝 Notes Generator",
            "❓ Quiz Maker",
            "💡 Concept Explain",
            "🔢 Math Solver"
        ])

        # ── NOTES ──
        with tool_tabs[0]:
            st.markdown("**Topic ke smart notes banao instantly!**")
            notes_topic = st.text_input("Topic likhoo:", placeholder="e.g., Photosynthesis, French Revolution, Pythagoras Theorem", key="notes_topic")
            notes_type = st.radio("Notes type:", ["Short Summary", "Detailed Notes", "Bullet Points", "Mind Map Format"], horizontal=True)
            if st.button("📝 Notes Banao!", key="notes_btn"):
                if notes_topic.strip():
                    prompt = f"Create {notes_type} for the topic: '{notes_topic}'\nSubject: {subject}, Level: {level}, Language: {language}\nMake notes clear, well-structured, include key points, dates/formulas if relevant, and easy to memorize."
                    with st.spinner("📝 Notes likh raha hoon..."):
                        try:
                            result = call_groq([{"role": "user", "content": prompt}],
                                              get_system_prompt(subject, level, language))
                            st.markdown(f"""<div class='chat-bubble-ai'>{result}</div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("⚠️ Topic toh batao!")

        # ── QUIZ ──
        with tool_tabs[1]:
            st.markdown("**Practice ke liye MCQ quiz banao!**")
            quiz_topic = st.text_input("Quiz topic:", placeholder="e.g., Newton's Laws, World War 2", key="quiz_topic")
            num_q = st.slider("Kitne questions?", 3, 10, 5)
            if st.button("❓ Quiz Banao!", key="quiz_btn"):
                if quiz_topic.strip():
                    prompt = f"Create a {num_q}-question MCQ quiz on: '{quiz_topic}'\nSubject: {subject}, Level: {level}, Language: {language}\n\nFormat each question as:\nQ[n]. [Question]\nA) [option]  B) [option]  C) [option]  D) [option]\nAnswer: [correct option]\nExplanation: [brief explanation in 1-2 lines]\n\nMake questions progressively harder."
                    with st.spinner("❓ Quiz bana raha hoon..."):
                        try:
                            result = call_groq([{"role": "user", "content": prompt}],
                                              get_system_prompt(subject, level, language))
                            st.markdown(f"""<div class='chat-bubble-ai'>{result}</div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(str(e))
                else:
                    st.warning("⚠️ Topic dalo!")

        # ── CONCEPT ──
        with tool_tabs[2]:
            st.markdown("**Koi bhi concept simply samjho!**")
            concept = st.text_input("Concept:", placeholder="e.g., Osmosis, Derivatives, Democracy", key="concept_input")
            explain_style = st.radio("Style:", ["Simple (Like I'm 10)", "Standard", "Deep Dive with Examples"], horizontal=True)
            if st.button("💡 Explain Karo!", key="concept_btn"):
                if concept.strip():
                    prompt = f"Explain the concept: '{concept}'\nStyle: {explain_style}\nSubject: {subject}, Language: {language}\nInclude: definition, real-life example, 
