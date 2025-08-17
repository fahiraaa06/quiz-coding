# routes/result.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import PASSING_SCORE, MAX_ATTEMPTS
from routes._helpers import save_result, read_attempts, write_attempt
from utils.quiz_utils import attempts_left
from utils.authz import login_required

bp = Blueprint("result", __name__)

@bp.route("/result", methods=["GET", "POST"])
@login_required
def result():
    uid = session.get("user")  # ambil user ID dari session
    if not uid:
        return redirect(url_for("auth.login"))

    quiz_score = int(session.get("quiz_score", 0))
    coding_score = int(session.get("coding_score", 0))
    total = quiz_score + coding_score

    # Hitung sisa kesempatan
    used_attempts = read_attempts().get(uid, 0)
    remaining = max(0, MAX_ATTEMPTS - used_attempts)

    if request.method == "POST":
        if attempts_left(uid, MAX_ATTEMPTS) <= 0:
            flash("Kesempatan habis. Tidak bisa menyimpan.", "warning")
            return redirect(url_for("result.result"))

        total_after_save, passed = save_result(uid, quiz_score, coding_score)
        used = used_attempts + 1
        write_attempt(uid, used)

        flash(
            f"Hasil disimpan. Status: {'LULUS' if passed else 'TIDAK LULUS'}. "
            f"Attempt: {used}/{MAX_ATTEMPTS}",
            "success"
        )
        return redirect(url_for("result.result"))

    # GET
    return render_template(
        "user/result.html",
        quiz_score=quiz_score,
        coding_score=coding_score,
        total=total,
        passing=PASSING_SCORE,
        used_attempts=used_attempts,
        remaining_attempts=remaining,
        max_attempts=MAX_ATTEMPTS,
    )
