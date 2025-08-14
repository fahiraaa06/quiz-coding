# utils/storage.py
from __future__ import annotations
import csv
import os
import time
from typing import Dict
from components.config import USERS_FILE, RESULTS_FILE, ATTEMPT_LOG, PASSING_SCORE

# ---------- Attempts (limit per user) ----------

def _ensure_parent_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def read_attempts() -> Dict[str, int]:
    """Baca jumlah attempt per user dari ATTEMPT_LOG."""
    if not os.path.exists(ATTEMPT_LOG) or os.path.getsize(ATTEMPT_LOG) == 0:
        return {}
    data: Dict[str, int] = {}
    with open(ATTEMPT_LOG, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            user, attempts_str = row[0], row[1]
            try:
                data[user] = int(attempts_str)
            except ValueError:
                continue
    return data

def write_attempt(user: str, value: int) -> None:
    """Tulis/overwrite attempt untuk user tertentu."""
    _ensure_parent_dir(ATTEMPT_LOG)
    data = read_attempts()
    data[user] = value
    with open(ATTEMPT_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in data.items():
            w.writerow([k, v])

# ---------- Results (nilai akhir) ----------

def ensure_results_header() -> None:
    """Pastikan RESULTS_FILE ada dan memiliki header yang benar."""
    _ensure_parent_dir(RESULTS_FILE)
    need_header = (not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0)
    if not need_header:
        return
    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user", "quiz_score", "coding_score", "total", "passed", "timestamp"])

def save_result(user: str, quiz_score: int, coding_score: int) -> tuple[int, int]:
    """Simpan hasil akhir. Return: (total, passed[0/1])."""
    ensure_results_header()
    total = int(quiz_score) + int(coding_score)
    passed = int(total >= PASSING_SCORE)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([user, quiz_score, coding_score, total, passed, int(time.time())])
    return total, passed

# ---------- Users (login) ----------

def ensure_users_file() -> None:
    """
    Pastikan data/users.csv ada dengan header 'email,password'.
    Tidak membuat user default; isi manual atau lewat panel admin.
    """
    _ensure_parent_dir(USERS_FILE)
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["email", "password"])

def read_users() -> Dict[str, str]:
    """
    Baca users dari data/users.csv → dict {email(lower): password}.
    Abaikan baris tanpa email. Header wajib: email,password
    """
    ensure_users_file()
    users: Dict[str, str] = {}
    try:
        with open(USERS_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("email") or "").strip().lower()
                pwd = row.get("password") or ""
                if email:
                    users[email] = pwd
    except (FileNotFoundError, csv.Error, UnicodeDecodeError):
        return {}
    return users
