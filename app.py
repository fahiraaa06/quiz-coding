from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from utils.quiz_utils import load_questions_from_csv, sample_questions
from utils.storage import read_users

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

QUESTION_SAMPLE = 5


def require_login(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        users = read_users()
        if users.get(email) == password:
            session["user"] = email
            return redirect(url_for("quiz"))
        flash("Email atau password salah.")
    return render_template("login.html")


@app.route("/quiz", methods=["GET", "POST"])
@require_login
def quiz():
    if request.method == "POST":
        questions = session.get("questions", [])
        score = 0
        for q in questions:
            ans = request.form.get(q["id"])
            if ans == q["answer"]:
                score += int(q.get("points", 10))
        session["score"] = score
        return redirect(url_for("result"))

    questions = load_questions_from_csv("data/questions.csv")
    questions = sample_questions(questions, QUESTION_SAMPLE)
    session["questions"] = questions
    return render_template("quiz.html", questions=questions)


@app.route("/result")
@require_login
def result():
    score = session.get("score")
    return render_template("result.html", score=score)


if __name__ == "__main__":
    app.run(debug=True)
