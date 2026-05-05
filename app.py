from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
import io
import json
import os

app = Flask(__name__)

# Load questions by grade
def load_questions(grade):
    filename = f"questions_grade{grade}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/quiz/<grade>", methods=["GET", "POST"])
def quiz(grade):
    questions = load_questions(grade)
    if request.method == "POST":
        score = 0
        for q in questions:
            user_answer = request.form.get(str(q["id"]))
            if user_answer == q["answer"]:
                score += 1
        percentage = round((score / len(questions)) * 100, 2)
        achievement = "Excellent" if percentage >= 80 else "Keep Practicing"
        return render_template("summary.html",
                               grade=grade,
                               score=score,
                               total=len(questions),
                               percentage=percentage,
                               achievement=achievement)
    return render_template("quiz.html", grade=grade, questions=questions)

@app.route("/certificate/<grade>/<score>/<total>/<percentage>/<achievement>/<username>")
def certificate(grade, score, total, percentage, achievement, username):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "Smart7 Senior Certificate")
    c.setFont("Helvetica", 14)
    c.drawString(100, 700, f"Name: {username}")
    c.drawString(100, 675, f"Grade: {grade}")
    c.drawString(100, 650, f"Score: {score}/{total}")
    c.drawString(100, 625, f"Percentage: {percentage}%")
    c.drawString(100, 600, f"Achievement: {achievement}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"certificate_{username}.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run()
