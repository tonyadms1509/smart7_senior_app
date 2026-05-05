import streamlit as st
import json

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
    except FileNotFoundError:
        st.error("Questions file not found.")
