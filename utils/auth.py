# utils/auth.py
from __future__ import annotations
import time
from datetime import datetime
from taipy.gui import notify, navigate
from state import POST_TEST_MODE, POST_START, POST_END, IDENTITY_FIELD, ADMIN_PASSWORD, WIB
from utils.timers import upsert_session
from utils.storage import read_users

def _now_wib() -> datetime:
    return datetime.now(WIB)

def window_open(now_func=_now_wib) -> bool:
    if not POST_TEST_MODE:
        return True
    now = now_func()
    return POST_START <= now <= POST_END

def do_login(state) -> None:
    email = (getattr(state, "login_email", "") or "").strip().lower()
    pwd = getattr(state, "login_password", "") or ""

    if not email or not pwd:
        notify(state, "warning", f"Masukkan {IDENTITY_FIELD} dan password.")
        return

    if POST_TEST_MODE and not window_open():
        notify(
            state,
            "error",
            f"Di luar jendela post-test "
            f"({POST_START.strftime('%d %b %Y %H:%M')}–{POST_END.strftime('%d %b %Y %H:%M')} WIB)."
        )
        return

    users = read_users()
    ok = users.get(email) == pwd

    if not ok and email.startswith("admin"):
        ok = (pwd == ADMIN_PASSWORD)

    if not ok:
        notify(state, "error", "Email atau password salah.")
        return

    state.auth = True
    state.user = email
    upsert_session(email, login_at_ts=int(time.time()))
    notify(state, "success", f"Login sebagai {email}")

    # ✅ Navigasi terakhir
    navigate(state, "quiz")

def do_logout(state) -> None:
    uid = getattr(state, "user", "")
    if uid:
        upsert_session(uid, logout_at_ts=int(time.time()))
    state.auth = False
    state.user = ""
    notify(state, "info", "Anda sudah logout.")
    navigate(state, to="/")

def admin_login(state) -> None:
    pwd = getattr(state, "admin_pwd", "")
    state._admin = bool(pwd == ADMIN_PASSWORD)
    if state._admin:
        notify(state, "success", "Admin login sukses.")
    else:
        notify(state, "error", "Password admin salah.")
