# routes/auth.py
import os, csv
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from components.config import IDENTITY_FIELD, POST_TEST_MODE, WIB
from routes._helpers import window_open
from utils.sessions import upsert_session

bp = Blueprint("auth", __name__)

# === Login dari CSV ===
USERS_FILE = "data/users.csv"

def load_users(path: str = USERS_FILE):
    """
    Membaca users.csv dan mengembalikan dict:
    { <email_or_username>: {"password": "...", "name": "..."} }
    """
    users = {}
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return users
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        # kolom minimal: email,password (name opsional)
        for row in r:
            key = (row.get("email") or row.get("username") or "").strip().lower()
            if not key:
                continue
            users[key] = {
                "password": (row.get("password") or "").strip(),
                "name": (row.get("name") or "").strip(),
            }
    return users

@bp.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        uid = (request.form.get("uid") or "").strip().lower()
        pwd = (request.form.get("pwd") or "").strip()

        if not uid or not pwd:
            flash("Lengkapi email/username dan password.", "warning")
            return redirect(url_for("auth.login"))

        if POST_TEST_MODE and not window_open(datetime.now(WIB)):
            flash("Di luar jendela post-test.", "danger")
            return redirect(url_for("auth.login"))

        users = load_users()
        if uid not in users:
            flash("User tidak ditemukan.", "danger")
            return redirect(url_for("auth.login"))

        # Catatan: ini cocok untuk demo/kelas (plain CSV).
        # Untuk produksi: simpan password hash & verifikasi dengan bcrypt/argon2.
        if pwd != users[uid]["password"]:
            flash("Password salah.", "danger")
            return redirect(url_for("auth.login"))

        # sukses login
        session.clear()
        session["user"] = uid
        session["name"] = users[uid].get("name") or uid
        upsert_session(uid, login_at_ts=int(datetime.now(WIB).timestamp()))
        return redirect(url_for("quiz.quiz"))

    return render_template(
        "login.html",
        identity_label=IDENTITY_FIELD,
        post_mode=POST_TEST_MODE
    )

@bp.route("/logout")
def logout():
    uid = session.get("user")
    if uid:
        upsert_session(uid, logout_at_ts=int(datetime.now(WIB).timestamp()))
    session.clear()
    return redirect(url_for("auth.login"))
