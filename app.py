import streamlit as st
import json
from reportlab.pdfgen import canvas
import io

st.title("Smart7 Senior Maths Practice")

grade = st.selectbox("Choose your grade:", ["8", "9", "10", "11", "12"])

if grade:
    filename = f"questions_grade{grade}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            questions = json.load(f)
        score = 0
        for q in questions:
            st.write(q["question"])
            choice = st.radio("Select answer:", q["options"], key=q["id"])
            if choice == q["answer"]:
                score += 1

        if st.button("Submit Answers"):
            percentage = round((score / len(questions)) * 100, 2)
            st.success(f"Score: {score}/{len(questions)} ({percentage}%)")

            # Certificate download
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(100, 750, "Smart7 Senior Certificate")
            c.setFont("Helvetica", 14)
            c.drawString(100, 700, f"Grade {grade} Learner")
            c.drawString(100, 670, f"Score: {score}/{len(questions)} ({percentage}%)")
            c.drawString(100, 640, "Congratulations on your achievement!")
            c.showPage()
            c.save()
            buffer.seek(0)

            st.download_button(
                label="Download Certificate",
                data=buffer,
                file_name="certificate.pdf",
                mime="application/pdf"
            )

    except FileNotFoundError:
        st.error("Questions file not found.")
