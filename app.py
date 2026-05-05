import json
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import requests

# -------------------------------
# Custom CSS for Color-Coded Buttons
# -------------------------------
st.markdown(
    """
    <style>
    /* Submit Answer = Green */
    div[data-testid="stForm"] button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold;
    }
    div[data-testid="stForm"] button:hover {
        background-color: #45a049 !important;
    }

    /* Navigation buttons by column */
    div[data-testid="stForm"] div:nth-child(1) button { background-color: #FF9800 !important; } /* Previous = Orange */
    div[data-testid="stForm"] div:nth-child(2) button { background-color: #2196F3 !important; } /* Next = Blue */
    div[data-testid="stForm"] div:nth-child(3) button { background-color: #9C27B0 !important; } /* Back to Top = Purple */
    div[data-testid="stForm"] div:nth-child(4) button { background-color: #FFC107 !important; color: black !important; } /* Reset = Yellow */
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Initialize session state
# -------------------------------
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.show_feedback = False
    st.session_state.mode = "Splash"
    st.session_state.paid_status = False

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.image("logo.png", width=200)
st.sidebar.title("Smart7 Navigation")

BACKEND_URL = "https://sectional-sighing-moonshine.ngrok-free.dev"

try:
    response = requests.get(f"{BACKEND_URL}/payment-status")
    st.session_state.paid_status = response.json().get("paid", False)
except Exception:
    pass

mode = st.sidebar.radio("Select Mode:", ["Splash", "Demo Mode", "Full Mode", "Admin"], key="mode_selector")
difficulty = st.sidebar.radio("Select Difficulty:", ["Easy", "Medium", "Hard"], key="difficulty_selector")
topic = st.sidebar.radio("Select Topic:", ["Algebra", "Geometry", "Fractions"], key="topic_selector")
grade = st.sidebar.radio("Select Grade:", ["8", "9", "10", "11", "12"], key="grade_selector")

# -------------------------------
# Load questions dynamically
# -------------------------------
grade_files = {
    "8": "questions/questions_grade8.json",
    "9": "questions/questions_grade9.json",
    "10": "questions/questions_grade10.json",
    "11": "questions/questions_grade11.json",
    "12": "questions/questions_grade12.json"
}
selected_file = grade_files.get(grade, "questions/questions_demo.json")

try:
    with open(selected_file, "r", encoding="utf-8") as f:
        all_questions = json.load(f)
except FileNotFoundError:
    st.error(f"❌ Question file for Grade {grade} not found.")
    all_questions = []

filtered_questions = [
    q for q in all_questions
    if (difficulty == "All" or q.get("difficulty") == difficulty or "difficulty" not in q)
    and (topic == "All" or q.get("topic") == topic or "topic" not in q)
]


# -------------------------------
# Mode Handling
# -------------------------------
if mode == "Splash":
    st.title("👋 Welcome to Smart7 Senior")
    st.markdown("""
    Smart7 Senior is a learning tool designed for **Grade 8–12 learners** to practice and master key maths concepts.

    ✨ **Features:**
    - Demo Mode: 10 free questions
    - Full Mode: Unlock all 100 questions with Yoco
    - Covers fractions, algebra, geometry, word problems, and probability
    - Instant feedback with clear explanations
    - Achievement certificate after completing all questions
    """)
    st.info("Select a mode from the sidebar to begin.")
    active_questions = []

elif mode == "Demo Mode":
    st.sidebar.info(f"🔓 Demo Mode: Free sample of 10 Grade {grade} questions.")
    active_questions = filtered_questions[:10]

elif mode == "Full Mode":
    st.sidebar.success("✅ Full Mode: Unlock all 100 questions.")
    if not st.session_state.paid_status:
        st.sidebar.warning("🔒 Please complete payment to unlock all questions.")
        st.sidebar.markdown("[💳 Pay with Yoco](https://pay.yoco.com/stocklinksa)")
        active_questions = filtered_questions[:10]
    else:
        st.success("Payment confirmed! 🎉 Full access unlocked.")
        active_questions = filtered_questions

elif mode == "Admin":
    st.sidebar.warning("⚙️ Admin Panel")
    st.write("Coming soon: question management and stats.")
    active_questions = []

# -------------------------------
# Quiz Loop
# -------------------------------
if active_questions and st.session_state.index < len(active_questions):
    q = active_questions[st.session_state.index]

    st.subheader(f"Question {st.session_state.index+1} of {len(active_questions)}")
    st.write(q.get("question", "No question text found"))

    choice = st.radio("Choose an answer:", q.get("options", []), key=f"radio_{st.session_state.index}")

    # Submit Answer
    with st.form(key=f"answer_form_{st.session_state.index}", clear_on_submit=False):
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            if choice == q.get("answer"):
                st.success("Correct!")
                st.session_state.score += 1
            else:
                st.error("Incorrect.")
                st.info(q.get("explanation", "No explanation available."))
            st.session_state.show_feedback = True

    # Navigation
    with st.form(key=f"nav_form_{st.session_state.index}", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns(4)
        prev_btn = col1.form_submit_button("Previous")
        next_btn = col2.form_submit_button("Next")
        top_btn  = col3.form_submit_button("Back to Top")
        reset_btn = col4.form_submit_button("Reset Quiz")

        if prev_btn and st.session_state.index > 0:
            st.session_state.index -= 1
        if next_btn and st.session_state.index < len(active_questions) - 1:
            st.session_state.index += 1
        if top_btn:
            st.session_state.index = 0
        if reset_btn:
            st.session_state.index = 0
            st.session_state.score = 0

elif active_questions and st.session_state.index >= len(active_questions):
    st.success("Quiz complete! 🎉")
    st.write(f"Your final score: {st.session_state.score}/{len(active_questions)}")
    percent = (st.session_state.score / len(active_questions)) * 100
    st.write(f"Percentage: {percent:.1f}%")

    if percent >= 80:
        st.success("🌟 Gold Achievement")
    elif percent >= 60:
        st.info("🥈 Silver Achievement")
    elif percent >= 40:
        st.warning("🥉 Bronze Achievement")
    else:
        st.error("💡 Keep practicing!")

    # Certificate
    def create_certificate(name, score, total, percent):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-100, "Smart7 Achievement Certificate")
        c.setFont("Helvetica", 14)
        c.drawCentredString(width/2, height-220, f"Completed {total} questions with {score}/{total} ({percent:.1f}%).")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    name = st.text_input("Enter your name for the certificate:")
    if name:
        pdf_buffer = create_certificate(name, st.session_state.score, len(active_questions), percent)
        st.download_button("📄 Download PDF Certificate", data=pdf_buffer, file_name="Smart7_Certificate.pdf", mime="application/pdf")

    if st.button("Reset Quiz", key="reset_btn_summary"):
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.show_feedback = False
        st.rerun()
