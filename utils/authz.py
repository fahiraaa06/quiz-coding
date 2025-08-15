from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(fn):
    @wraps(fn)
    def w(*a, **k):
        if not session.get("user"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth.login"))
        return fn(*a, **k)
    return w

def admin_required(fn):
    @wraps(fn)
    def w(*a, **k):
        if not session.get("_admin"):
            flash("Akses admin diperlukan.", "danger")
            return redirect(url_for("auth.admin_login"))
        return fn(*a, **k)
    return w
