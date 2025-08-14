# routes/result.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import PASSING_SCORE, MAX_ATTEMPTS
from routes._helpers import save_result, read_attempts, write_attempt, attempts_left

bp = Blueprint("result", __name__)

@bp.route("/result", methods=["GET","POST"])
def result():
    uid = session.get("user")
    if not uid:
        return redirect(url_for("auth.login"))
    quiz_score = int(session.get("quiz_score", 0))
    coding_score = int(session.get("coding_score", 0))

    if request.method == "POST":
        if attempts_left(uid, MAX_ATTEMPTS) <= 0:
            flash("Kesempatan habis. Tidak bisa menyimpan.", "warning")
            return redirect(url_for("result.result"))

        total, passed = save_result(uid, quiz_score, coding_score)
        used = read_attempts().get(uid, 0) + 1
        write_attempt(uid, used)
        flash(f"Hasil disimpan. Status: {'LULUS' if passed else 'TIDAK LULUS'}. Attempt: {used}/{MAX_ATTEMPTS}", "success")
        return redirect(url_for("leaderboard.leaderboard"))

    return render_template("result.html",
                           quiz_score=quiz_score,
                           coding_score=coding_score,
                           total=quiz_score+coding_score,
                           passing=PASSING_SCORE)
