# routes/code.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import CODE_DURATION_MIN, CODE_TIMEOUT_SEC, PROBLEM, MAX_ATTEMPTS
from utils.sessions import get_or_create_user_deadline
from utils.code_runner import run_code_with_timeout
from utils.quiz_utils import attempts_left  # ✅ ambil dari quiz_utils agar konsisten
from utils.authz import login_required

bp = Blueprint("code", __name__)

@bp.route("/code", methods=["GET", "POST"])
@login_required
def code():
    uid = session.get("user")  # ✅ perbaikan: ambil dari session key "user"
    if not uid:
        return redirect(url_for("auth.login"))

    if attempts_left(uid, MAX_ATTEMPTS) <= 0:
        flash("Kesempatan post-test sudah habis.", "danger")
        return redirect(url_for("result.result"))

    deadline_ts = get_or_create_user_deadline(uid, "code", CODE_DURATION_MIN)
    disabled = (deadline_ts - __import__("time").time() <= 0)

    code_key = f"code_{PROBLEM['id']}"
    if code_key not in session:
        session[code_key] = PROBLEM["starter_code"]

    if request.method == "POST" and not disabled:
        action = request.form.get("action")
        user_code = request.form.get("code") or session[code_key]
        result = run_code_with_timeout(user_code, PROBLEM["tests"], timeout_sec=CODE_TIMEOUT_SEC)
        session[code_key] = user_code

        if action == "run":
            if result.get("ok"):
                session.update({
                    "code_stdout": result.get("stdout", ""),
                    "code_error": None,
                    "code_details": result.get("details", []),
                    "code_passed": result.get("passed", 0),
                    "code_total": result.get("total", 0),
                })
            else:
                session.update({
                    "code_stdout": result.get("stdout", ""),
                    "code_error": result.get("error", "Gagal menjalankan kode."),
                    "code_details": None,
                    "code_passed": None,
                    "code_total": None,
                })
            return redirect(url_for("code.code"))

        if action == "submit":
            if result.get("ok"):
                passed, total = result["passed"], result["total"]
                session["coding_score"] = int(PROBLEM["points"] * (passed / total))
                session["code_details"] = result.get("details", [])
                session["code_stdout"] = result.get("stdout", "")
                session["code_error"] = None
                flash(
                    f"Skor coding: {session['coding_score']}/{PROBLEM['points']} "
                    f"(lulus {passed}/{total} test).",
                    "success"
                )
            else:
                session["code_error"] = result.get("error", "Gagal menjalankan kode.")
                flash("Gagal menjalankan kode.", "danger")
            return redirect(url_for("code.code"))

        if action == "clear":
            for k in ["code_stdout", "code_error", "code_details", "code_passed", "code_total"]:
                session.pop(k, None)
            return redirect(url_for("code.code"))

    return render_template(
        "user/code.html",
        problem=PROBLEM,
        code=session.get(code_key, PROBLEM["starter_code"]),
        deadline_ts=int(deadline_ts),
        minutes=CODE_DURATION_MIN,
        disabled=disabled,
        stdout=session.get("code_stdout"),
        error=session.get("code_error"),
        details=session.get("code_details"),
        passed=session.get("code_passed"),
        total=session.get("code_total"),
    )
