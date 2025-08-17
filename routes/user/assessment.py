# routes/assessment.py
from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint("assessment", __name__)

@bp.route("/choose-test")
def choose_test():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("user/choose.html")

@bp.route("/go-quiz")
def quiz():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return redirect(url_for("quiz.quiz"))

@bp.route("/go-code")
def coding():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return redirect(url_for("code.code"))
