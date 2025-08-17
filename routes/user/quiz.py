from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from components.config import QUIZ_DURATION_MIN, QUESTION_SAMPLE, MAX_ATTEMPTS, PASSING_SCORE
from utils.sessions import get_or_create_user_deadline
from utils.authz import login_required
from utils.quiz_utils import load_questions, attempts_left
from routes._helpers import save_result, read_attempts, write_attempt
import time

bp = Blueprint("quiz", __name__)


@bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    uid = session.get("user")
    if not uid:
        return redirect(url_for("auth.login"))

    # Kalau sudah habis attempt → paksa ke result
    if attempts_left(uid, MAX_ATTEMPTS) <= 0:
        flash("Kesempatan post-test sudah habis.", "danger")
        return redirect(url_for("result.result"))

    # Tentukan deadline khusus quiz
    section = "quiz"
    deadline_ts = get_or_create_user_deadline(uid, section, QUIZ_DURATION_MIN)
    disabled = (deadline_ts - time.time() <= 0)

    # Ambil soal sekali saja per sesi
    if "sampled_questions" not in session:
        session["sampled_questions"] = load_questions(sample=QUESTION_SAMPLE)
    qs = session["sampled_questions"]

    # === Handle submit (AJAX JSON) ===
    if request.method == "POST":
        if disabled:
            return jsonify({"ok": False, "msg": "Waktu habis. Jawaban tidak disimpan."})

        answers = {}
        score = 0
        total_points = 0
        correct_count = 0

        for q in qs:
            pts = int(q.get("points", 1))
            total_points += pts

            user_answer = (request.form.get(q["id"]) or "").strip().lower()
            correct = (q.get("answer") or "").strip().lower()

            is_correct = (user_answer == correct)
            if is_correct:
                score += pts
                correct_count += 1

            answers[q["id"]] = {
                "chosen": user_answer,
                "correct": correct,
                "is_correct": is_correct,
            }

        # Simpan ke session
        session["quiz_score"] = score
        session["quiz_answers"] = answers

        # Simpan ke DB + increment attempt
        used_attempts = read_attempts().get(uid, 0)
        write_attempt(uid, used_attempts + 1)

        # Hitung hasil total (quiz + coding)
        total_after_save, overall_passed = save_result(
            uid,
            score,
            session.get("coding_score", 0)
        )

        return jsonify({
            "ok": True,
            # hasil quiz
            "quiz_score": score,
            "quiz_total_points": total_points,
            "quiz_pct": round((score / total_points) * 100) if total_points else 0,
            "correct_count": correct_count,
            "total_questions": len(qs),
            # status gabungan
            "overall_passed": overall_passed,
            "has_coding": "coding_score" in session
        })

    # === Kalau GET → render quiz page ===
    go_to_coding = "coding_score" not in session
    return render_template(
        "user/quiz.html",
        questions=qs,
        deadline_ts=int(deadline_ts),
        minutes=QUIZ_DURATION_MIN,
        disabled=disabled,
        answers=session.get("quiz_answers"),
        passing=PASSING_SCORE,
        go_to_coding=go_to_coding,
    )
