# routes/admin/dashboard.py
import os
import csv
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from utils.authz import admin_required
from utils.sessions import set_user_deadline_ts
from routes._helpers import ensure_results_header
from utils.content import (
    get_active_questions_name,
    get_active_problem_name,
    list_question_sets,  # hanya untuk ringkasan dropdown cepat kalau mau
)

from components.config import (
    ADMIN_PASSWORD,          # bila login admin masih di sini (bisa tidak dipakai)
    ATTEMPT_LOG,
    RESULTS_FILE,
    SESSIONS_FILE,
    USERS_FILE,
    QUESTIONS_DIR,
    QUESTIONS_ACTIVE,
    PROBLEM_ACTIVE_FILE,
    PASSING_SCORE,
    WIB,
)

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ========================
# Helpers
# ========================
def _to_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def _avg(nums):
    nums = [n for n in nums if n is not None]
    return round(sum(nums) / len(nums), 2) if nums else 0

def _finfo(path):
    return {
        "exists": os.path.exists(path),
        "size": os.path.getsize(path) if os.path.exists(path) else 0,
    }

def _iter_all_users():
    """Ambil semua uid dari USERS_FILE (kolom email/username)."""
    users = []
    if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
        try:
            with open(USERS_FILE, encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for row in r:
                    key = (row.get("email") or row.get("username") or "").strip().lower()
                    if key:
                        users.append(key)
        except OSError:
            pass
    return users


# ========================
# Dashboard (ringkasan + leaderboard + aksi)
# ========================
@bp.route("/", methods=["GET", "POST"])
@admin_required
def dashboard():
    # ---------- Aksi POST ----------
    if request.method == "POST":
        # Reset attempts.csv
        if "reset_attempts" in request.form:
            try:
                if os.path.exists(ATTEMPT_LOG):
                    os.remove(ATTEMPT_LOG)
                flash("attempts.csv direset.", "success")
            except OSError as e:
                flash(f"Gagal mereset attempts.csv: {e}", "danger")
            return redirect(url_for("admin.dashboard"))

        # Reset results.csv
        if "reset_results" in request.form:
            try:
                if os.path.exists(RESULTS_FILE):
                    os.remove(RESULTS_FILE)
                ensure_results_header()
                flash("results.csv direset.", "success")
            except OSError as e:
                flash(f"Gagal mereset results.csv: {e}", "danger")
            return redirect(url_for("admin.dashboard"))

        # Reset deadline GLOBAL (tanpa input user)
        if "reset_deadline_global" in request.form:
            # Definisi: clear semua deadline per-user agar patuh ke window post-test.
            # Implementasi: set deadline quiz & code = 0 untuk SELURUH user.
            users = _iter_all_users()
            total, ok = len(users), 0
            for uid in users:
                try:
                    set_user_deadline_ts(uid, "quiz", 0)
                    set_user_deadline_ts(uid, "code", 0)
                    ok += 1
                except OSError:
                    # lanjutkan; kalau ingin log detail, bisa print/flash ringkas
                    continue
            flash(f"Deadline global direset untuk {ok}/{total} user.", "success")
            return redirect(url_for("admin.dashboard"))

    # ---------- Ringkasan ----------
    summary = {}

    # Active quiz file
    active_q_name = get_active_questions_name()
    q_count = None
    if os.path.exists(QUESTIONS_ACTIVE) and os.path.getsize(QUESTIONS_ACTIVE) > 0:
        try:
            with open(QUESTIONS_ACTIVE, encoding="utf-8", newline="") as f:
                q_count = sum(1 for _ in csv.DictReader(f))
        except OSError:
            q_count = "?"

    summary["active_quiz"] = {
        "name": active_q_name or "(belum di-set)",
        "count": q_count,
        "path": QUESTIONS_ACTIVE,
        "exists": os.path.exists(QUESTIONS_ACTIVE),
        "size": os.path.getsize(QUESTIONS_ACTIVE) if os.path.exists(QUESTIONS_ACTIVE) else 0,
    }

    # Active problem file
    active_p_name = get_active_problem_name()
    p_meta = {"title": "(n/a)", "tests": None}
    if os.path.exists(PROBLEM_ACTIVE_FILE) and os.path.getsize(PROBLEM_ACTIVE_FILE) > 0:
        try:
            with open(PROBLEM_ACTIVE_FILE, encoding="utf-8") as f:
                obj = json.load(f)
            p_meta = {
                "title": obj.get("title") or "(tanpa judul)",
                "tests": len(obj.get("tests") or []),
            }
        except (OSError, json.JSONDecodeError):
            pass

    summary["active_problem"] = {
        "name": active_p_name or "(belum di-set)",
        "meta": p_meta,
        "path": PROBLEM_ACTIVE_FILE,
        "exists": os.path.exists(PROBLEM_ACTIVE_FILE),
        "size": os.path.getsize(PROBLEM_ACTIVE_FILE) if os.path.exists(PROBLEM_ACTIVE_FILE) else 0,
    }

    # File sizes
    summary["files"] = {
        "results": _finfo(RESULTS_FILE),
        "attempts": _finfo(ATTEMPT_LOG),
        "sessions": _finfo(SESSIONS_FILE),
    }

    # KPI hari ini & aktivitas terbaru
    today = datetime.now(WIB).date()
    latest_rows, today_rows = [], []
    if os.path.exists(RESULTS_FILE) and os.path.getsize(RESULTS_FILE) > 0:
        try:
            with open(RESULTS_FILE, encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            # parse timestamp (asumsi kolom "ts" epoch detik atau "timestamp" ISO)
            def _parse_date(r):
                ts = r.get("ts") or r.get("timestamp") or ""
                # epoch detik
                try:
                    return datetime.fromtimestamp(int(ts), WIB).date()
                except (TypeError, ValueError, OSError):
                    pass
                # fallback ISO
                try:
                    return datetime.fromisoformat(ts).date()
                except (TypeError, ValueError):
                    return None

            for r in rows[-200:]:
                d = _parse_date(r)
                if d == today:
                    today_rows.append(r)
            _latest_rows = rows[-10:][::-1]
        except OSError:
            pass

    today_total = [_to_int(r.get("total")) for r in today_rows]
    today_quiz  = [_to_int(r.get("quiz_score")) for r in today_rows]
    today_code  = [_to_int(r.get("coding_score")) for r in today_rows]
    today_pass  = sum(1 for r in today_rows if _to_int(r.get("total")) >= PASSING_SCORE)

    summary["kpi"] = {
        "today_submissions": len(today_rows),
        "today_pass_rate": f"{round((today_pass/len(today_rows))*100,1)}%" if today_rows else "0%",
        "avg_total_today": _avg(today_total),
        "avg_quiz_today": _avg(today_quiz),
        "avg_code_today": _avg(today_code),
    }

    # ---------- Leaderboard (di dashboard langsung) ----------
    sort_order = request.args.get("sort", "desc").lower()
    reverse_sort = sort_order != "asc"

    leaderboard_rows = []
    if os.path.exists(RESULTS_FILE) and os.path.getsize(RESULTS_FILE) > 0:
        try:
            with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    leaderboard_rows.append(row)
        except OSError:
            leaderboard_rows = []

        leaderboard_rows.sort(
            key=lambda x: (
                _to_int(x.get("total")),
                _to_int(x.get("quiz_score")),
                _to_int(x.get("coding_score")),
            ),
            reverse=reverse_sort,
        )

    # kirim ke template
    return render_template(
        "admin/dashboard.html",
        is_admin=True,
        summary=summary,
        leaderboard_rows=leaderboard_rows,
        sort_order=sort_order,
        # kalau mau dropdown ringkas pemilihan bank soal di dashboard:
        question_files=list_question_sets(),
        questions_dir=QUESTIONS_DIR,
    )
