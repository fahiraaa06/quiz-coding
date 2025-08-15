# routes/_helpers.py
from __future__ import annotations

import os
import csv
import time
from datetime import datetime
from typing import Tuple, Dict

from components.config import (
    RESULTS_FILE,
    ATTEMPT_LOG,
    PASSING_SCORE,
)
from utils.settings import (
    get_post_window,          # baca start/end (bisa diubah admin) atau fallback config
    window_open as _win_open, # penentu apakah 'now' dalam window
)


# =========================
# Post-test window helpers
# =========================
def window_open(now: datetime) -> bool:
    """
    True jika waktu 'now' berada dalam jendela post-test yang aktif.
    Catatan: pemanggil bebas memutuskan apakah window ini dipakai
    (mis. dibarengi POST_TEST_MODE di config).
    """
    return _win_open(now)


def get_posttest_window() -> Tuple[datetime, datetime]:
    """
    Mengembalikan (start, end) jendela post-test yang berlaku sekarang,
    berasal dari settings admin (jika ada) atau fallback dari config.
    """
    return get_post_window()


# =========================
# Results.csv helpers
# =========================
def ensure_results_header() -> None:
    """
    Pastikan RESULTS_FILE memiliki header standar.
    Header: user,quiz_score,coding_score,total,passed,timestamp
    """
    need_header = (not os.path.exists(RESULTS_FILE)) or (os.path.getsize(RESULTS_FILE) == 0)
    if not need_header:
        return

    parent = os.path.dirname(RESULTS_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user", "quiz_score", "coding_score", "total", "passed", "timestamp"])


def save_result(user: str, quiz_score: int, coding_score: int) -> tuple[int, int]:
    """
    Tambahkan 1 baris hasil.
    Return: (total, passed[0/1])
    """
    ensure_results_header()
    total = int(quiz_score) + int(coding_score)
    passed = int(total >= PASSING_SCORE)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([user, quiz_score, coding_score, total, passed, int(time.time())])
    return total, passed


# =========================
# Attempts.csv helpers
# =========================
def read_attempts() -> Dict[str, int]:
    """
    Baca ATTEMPT_LOG → dict {user: attempts}
    """
    if not os.path.exists(ATTEMPT_LOG) or os.path.getsize(ATTEMPT_LOG) == 0:
        return {}
    data: Dict[str, int] = {}
    with open(ATTEMPT_LOG, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        for row in r:
            if not row:
                continue
            name = (row[0] or "").strip()
            try:
                attempts = int(row[1])
            except (IndexError, ValueError, TypeError):
                attempts = 0
            if name:
                data[name] = attempts
    return data


def write_attempt(user: str, value: int) -> None:
    """
    Tulis ulang ATTEMPT_LOG dengan update untuk user tertentu.
    """
    parent = os.path.dirname(ATTEMPT_LOG)
    if parent:
        os.makedirs(parent, exist_ok=True)

    data = read_attempts()
    data[user] = int(value)

    with open(ATTEMPT_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in data.items():
            w.writerow([k, v])


def attempts_left(user: str, max_attempts: int) -> int:
    used = read_attempts().get(user, 0)
    return max(0, int(max_attempts) - int(used))
