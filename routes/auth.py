# routes/auth.py
import os
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import (
    IDENTITY_FIELD, POST_TEST_MODE, WIB,
    USERS_FILE
)
from routes._helpers import window_open
from utils.sessions import upsert_session
from components.config import POST_START, POST_END

bp = Blueprint("auth", __name__)

# =========================
# Util load users
# =========================
def _load_users(path: str = USERS_FILE):
    """
    Membaca CSV user (email,password,role[,name]) menjadi dict:
    { email/username: {password, name, role} }
    """
    users = {}
    if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
        return users
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            key = (row.get("email") or row.get("username") or "").strip().lower()
            if not key:
                continue
            users[key] = {
                "password": (row.get("password") or "").strip(),
                "name": (row.get("name") or key).strip(),
                "role": (row.get("role") or "user").strip().lower(),
            }
    return users

def _normalize(s: str) -> str:
    return (s or "").strip()

# =========================
# Login gabungan
# =========================

@bp.route("/", methods=["GET", "POST"])
def user_login():
    """Login untuk peserta (user)."""
    if request.method == "POST":
        uid = _normalize(request.form.get("uid")).lower()
        pwd = _normalize(request.form.get("pwd"))

        if not uid or not pwd:
            flash("Lengkapi email/username dan password.", "warning")
            return redirect(url_for("auth.user_login"))

        users = _load_users()
        info = users.get(uid)
        if not info or info.get("role") != "user":
            flash("User tidak ditemukan.", "danger")
            return redirect(url_for("auth.user_login"))

        if pwd != info["password"]:
            flash("Password salah.", "danger")
            return redirect(url_for("auth.user_login"))

        if POST_TEST_MODE and not window_open(datetime.now(WIB)):
            flash("Di luar jendela post-test.", "danger")
            return redirect(url_for("auth.user_login"))

        session.clear()
        session["user"] = uid
        session["name"] = info.get("name") or uid
        session["role"] = "user"
        upsert_session(uid, login_at_ts=int(datetime.now(WIB).timestamp()))
        return redirect(url_for("quiz.quiz"))

    return render_template(
        "user/login.html",
        identity_label=IDENTITY_FIELD,
        post_mode=POST_TEST_MODE,
        post_start=POST_START,
        post_end=POST_END
    )


@bp.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Login untuk admin (kelola soal & hasil)."""
    if request.method == "POST":
        uid = _normalize(request.form.get("uid")).lower()
        pwd = _normalize(request.form.get("pwd"))

        if not uid or not pwd:
            flash("Lengkapi username/email dan password.", "warning")
            return redirect(url_for("auth.admin_login"))

        users = _load_users()
        info = users.get(uid)
        if not info or info.get("role") != "admin":
            flash("Admin tidak ditemukan.", "danger")
            return redirect(url_for("auth.admin_login"))

        if pwd != info["password"]:
            flash("Password admin salah.", "danger")
            return redirect(url_for("auth.admin_login"))

        session.clear()
        session["role"] = "admin"
        session["_admin"] = True
        session["name"] = info.get("name") or uid
        flash("Login admin sukses.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin/login.html",
        identity_label=IDENTITY_FIELD
    )


# =========================
# Logout
# =========================
@bp.route("/logout")
def logout():
    uid = session.get("user")
    if uid:
        upsert_session(uid, logout_at_ts=int(datetime.now(WIB).timestamp()))
    session.clear()
    return redirect(url_for("auth.login"))
