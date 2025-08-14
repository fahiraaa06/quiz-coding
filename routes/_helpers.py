# routes/_helpers.py
import os, csv, json, time, random
from datetime import datetime
from typing import List, Dict, Any
from components.config import (
    RESULTS_FILE, ATTEMPT_LOG, PASSING_SCORE,
    POST_TEST_MODE, POST_START, POST_END
)
from components.constants import DEFAULT_QUESTIONS

def window_open(now: datetime) -> bool:
    if not POST_TEST_MODE:
        return True
    return POST_START <= now <= POST_END

def ensure_results_header():
    if not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0:
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["user","quiz_score","coding_score","total","passed","timestamp"])

def read_attempts() -> Dict[str, int]:
    if not os.path.exists(ATTEMPT_LOG) or os.path.getsize(ATTEMPT_LOG) == 0:
        return {}
    data = {}
    with open(ATTEMPT_LOG, newline="", encoding="utf-8") as f:
        for name, attempts in csv.reader(f):
            data[name] = int(attempts)
    return data

def write_attempt(user: str, value: int):
    data = read_attempts()
    data[user] = value
    with open(ATTEMPT_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in data.items():
            w.writerow([k, v])

def attempts_left(user: str, max_attempts: int) -> int:
    used = read_attempts().get(user, 0)
    return max(0, max_attempts - used)

def save_result(user: str, quiz_score: int, coding_score: int):
    ensure_results_header()
    total = quiz_score + coding_score
    passed = int(total >= PASSING_SCORE)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([user, quiz_score, coding_score, total, passed, int(time.time())])
    return total, passed

def load_questions(path="data/questions.csv", sample: int = 5) -> List[Dict[str, Any]]:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        qs = DEFAULT_QUESTIONS.copy()
    else:
        qs = []
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                choices_raw = (row.get("choices") or "").strip()
                if choices_raw.startswith("["):
                    try:
                        choices = json.loads(choices_raw)
                    except Exception:
                        choices = []
                else:
                    choices = [c.strip() for c in choices_raw.split("|") if c.strip()]
                qs.append({
                    "id": row.get("id") or f"q_{len(qs)+1}",
                    "question": (row.get("question") or "").strip(),
                    "choices": choices,
                    "answer": (row.get("answer") or "").strip(),
                    "points": int(row.get("points") or 10),
                })
        if not qs:
            qs = DEFAULT_QUESTIONS.copy()
    random.shuffle(qs)
    return qs[:max(1, min(sample, len(qs)))]
