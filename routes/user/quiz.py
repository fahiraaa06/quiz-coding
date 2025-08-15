# routes/quiz.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import QUIZ_DURATION_MIN, QUESTION_SAMPLE, MAX_ATTEMPTS
from utils.sessions import get_or_create_user_deadline
from utils.authz import login_required
from utils.quiz_utils import load_questions, attempts_left

bp = Blueprint("quiz", __name__)

@bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    # Perbaikan: ambil user dari session dengan key yang benar
    uid = session.get("user")
    if not uid:
        return redirect(url_for("auth.login"))

    # Cek sisa attempts
    if attempts_left(uid, MAX_ATTEMPTS) <= 0:
        flash("Kesempatan post-test sudah habis.", "danger")
        return redirect(url_for("result.result"))

    # Tentukan deadline quiz/coding
    section = "code" if request.args.get("forcecode") else "quiz"
    deadline_ts = get_or_create_user_deadline(uid, section, QUIZ_DURATION_MIN)

    disabled = (deadline_ts - __import__("time").time() <= 0)

    # Ambil soal jika belum ada di session
    if "sampled_questions" not in session:
        session["sampled_questions"] = load_questions(sample=QUESTION_SAMPLE)

    qs = session["sampled_questions"]

    if request.method == "POST":
        if disabled:
            flash("Waktu habis. Jawaban tidak disimpan.", "danger")
            return redirect(url_for("quiz.quiz"))

        score = 0
        total_points = 0
        for q in qs:
            total_points += q["points"]
            if request.form.get(q["id"]) == q["answer"]:
                score += q["points"]

        session["quiz_score"] = score
        flash(f"Skor quiz: {score}/{total_points}", "success")
        return redirect(url_for("result.result"))

    return render_template(
        "user/quiz.html",
        questions=qs,
        deadline_ts=int(deadline_ts),
        minutes=QUIZ_DURATION_MIN,
        disabled=disabled
    )
