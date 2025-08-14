# routes/leaderboard.py
import os, csv
from flask import Blueprint, render_template
from components.config import RESULTS_FILE

bp = Blueprint("leaderboard", __name__)

@bp.route("/leaderboard")
def leaderboard():
    rows = []
    if os.path.exists(RESULTS_FILE) and os.path.getsize(RESULTS_FILE) > 0:
        with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
        rows.sort(key=lambda x: (int(x["total"]), int(x["quiz_score"]), int(x["coding_score"])), reverse=True)
    return render_template("leaderboard.html", rows=rows)
