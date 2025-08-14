# routes/admin.py
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import ADMIN_PASSWORD
from routes._helpers import ensure_results_header
from components.config import ATTEMPT_LOG, RESULTS_FILE
from utils.sessions import set_user_deadline_ts

bp = Blueprint("admin", __name__)

@bp.route("/admin", methods=["GET","POST"])
def admin():
    is_admin = session.get("_admin", False)
    if request.method == "POST" and not is_admin:
        pwd = request.form.get("pwd") or ""
        session["_admin"] = (pwd == ADMIN_PASSWORD)
        return redirect(url_for("admin.admin"))

    if not session.get("_admin"):
        return render_template("admin.html", is_admin=False)

    # admin actions
    if request.method == "POST":
        if "reset_attempts" in request.form:
            if os.path.exists(ATTEMPT_LOG): os.remove(ATTEMPT_LOG)
            flash("attempts.csv direset.", "success")
        elif "reset_results" in request.form:
            if os.path.exists(RESULTS_FILE): os.remove(RESULTS_FILE)
            ensure_results_header()
            flash("results.csv direset.", "success")
        elif "upload_questions" in request.form:
            file = request.files.get("questions_file")
            if file:
                content = file.stream.read().decode("utf-8")
                with open("data/questions.csv","w",encoding="utf-8") as f:
                    f.write(content)
                flash("questions.csv disimpan. Akan terpakai pada quiz berikutnya.", "success")
        elif "reset_deadline" in request.form:
            r_uid = (request.form.get("r_uid") or "").strip()
            r_section = request.form.get("r_section") or "quiz"
            if r_uid:
                set_user_deadline_ts(r_uid, r_section, 0)
                flash(f"Deadline {r_section} untuk {r_uid} sudah direset.", "success")
            else:
                flash("Isi user/email terlebih dahulu.", "warning")
        return redirect(url_for("admin.admin"))

    return render_template("admin.html", is_admin=True)
