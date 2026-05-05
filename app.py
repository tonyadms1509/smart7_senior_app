from flask import Flask, render_template, request, send_file
import json, os, io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/quiz/<grade>")
def quiz(grade):
    filename = f"questions_grade{grade}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            questions = json.load(f)
        return render_template("quiz.html", grade=grade, questions=questions)
    else:
        return f"No questions found for grade {grade}", 404

@app.route("/submit", methods=["POST"])
def submit():
    grade = request.form.get("grade")
    filename = f"questions_grade{grade}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    score, total = 0, 0
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            questions = json.load(f)
        total = len(questions)
        for i, q in enumerate(questions, start=1):
            user_answer = request.form.get(f"q{i}")
            if user_answer == q.get("answer"):
                score += 1

    return render_template("summary.html", score=score, total=total, grade=grade)

@app.route("/certificate", methods=["POST"])
def certificate():
    name = request.form.get("name", "Learner")
    score = int(request.form.get("score", 0))
    total = int(request.form.get("total", 0))
    percent = (score / total * 100) if total > 0 else 0

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height-100, "Smart7 Achievement Certificate")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-180, f"Presented to {name}")
    c.drawCentredString(width/2, height-220, f"Completed {total} questions")
    c.drawCentredString(width/2, height-240, f"Score: {score}/{total} ({percent:.1f}%)")

    if percent >= 80:
        c.drawCentredString(width/2, height-280, "🌟 Gold Achievement")
    elif percent >= 60:
        c.drawCentredString(width/2, height-280, "🥈 Silver Achievement")
    elif percent >= 40:
        c.drawCentredString(width/2, height-280, "🥉 Bronze Achievement")
    else:
        c.drawCentredString(width/2, height-280, "💡 Keep practicing!")

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name="Smart7_Certificate.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
