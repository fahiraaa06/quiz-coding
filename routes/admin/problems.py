import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.authz import admin_required
from utils.content import (
    list_problems,
    activate_problem,
    get_active_problem_name,
)
from components.config import PROBLEMS_DIR, PROBLEM_ACTIVE_FILE

bp = Blueprint("admin_problems", __name__, url_prefix="/admin")

@bp.route("/problems", methods=["GET", "POST"])
@admin_required
def manage_problems():
    # POST: aktifkan file terpilih
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        try:
            activate_problem(name)
            flash(f"Problem aktif: {name}", "success")
        except (ValueError, FileNotFoundError) as e:
            flash(str(e), "danger")
        return redirect(url_for("admin_problems.manage_problems"))

    # GET: tampilkan daftar + penanda aktif + meta (title/points/tests)
    files = list_problems()
    active_name = get_active_problem_name()

    metas = {}
    for fname in files:
        path = os.path.join(PROBLEMS_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                obj = json.load(f)
            metas[fname] = {
                "title": obj.get("title") or "(tanpa judul)",
                "points": obj.get("points"),
                "tests": len(obj.get("tests") or []),
            }
        except (OSError, json.JSONDecodeError):
            metas[fname] = {"title": "(gagal dibaca)", "points": "-", "tests": "-"}

    active_info = None
    if os.path.exists(PROBLEM_ACTIVE_FILE):
        try:
            with open(PROBLEM_ACTIVE_FILE, encoding="utf-8") as f:
                obj = json.load(f)
            active_info = {
                "path": PROBLEM_ACTIVE_FILE,
                "title": obj.get("title") or "(tanpa judul)",
                "points": obj.get("points"),
                "tests": len(obj.get("tests") or []),
            }
        except (OSError, json.JSONDecodeError):
            active_info = None

    return render_template(
        "admin/problems.html",
        files=files,
        active_name=active_name,
        metas=metas,
        active_info=active_info,
        problems_dir=PROBLEMS_DIR,
    )
