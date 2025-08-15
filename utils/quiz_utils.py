# utils/quiz_utils.py
from __future__ import annotations

import os
import csv
import json
import random
from typing import List, Dict, Any, Optional

from components.constants import DEFAULT_QUESTIONS
from components.config import QUESTIONS_ACTIVE, ATTEMPT_LOG


# -----------------------------
# Helpers
# -----------------------------
def _to_int(val, default: int = 10) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _parse_choices_field(raw: str) -> List[str]:
    """
    Parse kolom 'choices' yang bisa berupa:
    - JSON list: ["A","B","C","D"]
    - String dipisah pipa: A | B | C | D
    """
    s = (raw or "").strip()
    if not s:
        return []
    if s.startswith("[") and s.endswith("]"):
        try:
            data = json.loads(s)
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
        except json.JSONDecodeError:
            pass
    return [c.strip() for c in s.split("|") if c.strip()]


def _choices_from_row(row: Dict[str, Any]) -> List[str]:
    """
    Ambil daftar pilihan dari berbagai skema kolom.
    """
    # 1) kolom 'choices'
    choices_raw = (row.get("choices") or "").strip()
    if choices_raw:
        parsed = _parse_choices_field(choices_raw)
        if parsed:
            return parsed

    # 2) kolom per huruf / varian nama
    buckets: List[List[str]] = []
    label_sets = [
        ["option_a", "option_b", "option_c", "option_d"],
        ["choice_a", "choice_b", "choice_c", "choice_d"],
        ["a", "b", "c", "d"],
    ]
    for labels in label_sets:
        vals = [str(row.get(k) or "").strip() for k in labels]
        vals = [v for v in vals if v]
        if vals:
            buckets.append(vals)

    if buckets:
        return max(buckets, key=len)

    return []


# -----------------------------
# Loader utama
# -----------------------------
def load_questions_from_csv(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Membaca file CSV soal dan mengembalikan list dict:
    { id, question, choices: [..], answer, points }
    """
    target = path or QUESTIONS_ACTIVE

    if not os.path.exists(target) or os.path.getsize(target) == 0:
        return DEFAULT_QUESTIONS.copy()

    out: List[Dict[str, Any]] = []
    try:
        with open(target, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return DEFAULT_QUESTIONS.copy()

            for row in reader:
                choices = _choices_from_row(row)
                out.append({
                    "id": (row.get("id") or f"q_{len(out)+1}").strip(),
                    "question": (row.get("question") or "").strip(),
                    "choices": choices,
                    "answer": (row.get("answer") or "").strip(),
                    "points": _to_int(row.get("points"), 10),
                })
    except (OSError, csv.Error):
        return DEFAULT_QUESTIONS.copy()

    return out or DEFAULT_QUESTIONS.copy()


def sample_questions(questions: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    """
    Kembalikan subset acak berukuran k (>=1, <=len(questions)).
    """
    if not questions:
        return DEFAULT_QUESTIONS.copy()
    k = max(1, min(k, len(questions)))
    return random.sample(questions, k)


def load_questions(path: Optional[str] = None, sample: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience wrapper:
    - Baca semua soal dari CSV (atau fallback default)
    - Ambil sejumlah 'sample' secara acak (>=1)
    """
    all_qs = load_questions_from_csv(path)
    return sample_questions(all_qs, sample)


# -----------------------------
# Attempts tracking
# -----------------------------
def attempts_left(uid: str, max_attempts: int = 1) -> int:
    """
    Hitung sisa attempts untuk user tertentu.
    """
    if not uid:
        return 0
    if not os.path.exists(ATTEMPT_LOG) or os.path.getsize(ATTEMPT_LOG) == 0:
        return max_attempts

    try:
        with open(ATTEMPT_LOG, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        user_attempts = sum(1 for r in rows if r.get("user") == uid)
        return max(0, max_attempts - user_attempts)
    except (OSError, csv.Error):
        return max_attempts
