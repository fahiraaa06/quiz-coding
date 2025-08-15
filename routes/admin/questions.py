import os
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.authz import admin_required
from utils.content import (
    list_question_sets,
    activate_questions,
    get_active_questions_name,
    get_active_questions_path,
)
from components.config import QUESTIONS_DIR

bp = Blueprint("admin_questions", __name__, url_prefix="/admin")

@bp.route("/questions", methods=["GET", "POST"])
@admin_required
def manage_questions():
    # POST: aktifkan file terpilih
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        try:
            activate_questions(name)
            flash(f"Bank soal aktif: {name}", "success")
        except (ValueError, FileNotFoundError) as e:
            flash(str(e), "danger")
        return redirect(url_for("admin_questions.manage_questions"))

    # GET: tampilkan daftar + penanda aktif + ringkasan jumlah soal
    files = list_question_sets()
    active_name = get_active_questions_name()

    stats = {}
    for fname in files:
        path = os.path.join(QUESTIONS_DIR, fname)
        try:
            with open(path, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                stats[fname] = sum(1 for _ in reader)
        except OSError:
            stats[fname] = "?"

    active_path = get_active_questions_path()
    active_info = None
    if os.path.exists(active_path):
        try:
            active_info = {
                "path": active_path,
                "size": os.path.getsize(active_path),
                "mtime": os.path.getmtime(active_path),
            }
        except OSError:
            active_info = None

    return render_template(
        "admin/questions.html",
        files=files,
        active_name=active_name,
        stats=stats,
        active_info=active_info,
        questions_dir=QUESTIONS_DIR,
    )
