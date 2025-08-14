# utils/quiz_utils.py
import csv, json, os, random
from typing import List, Dict, Any
from components.constants import DEFAULT_QUESTIONS

def load_questions_from_csv(path: str) -> List[Dict[str, Any]]:
    """Muat bank soal dari CSV, jika tidak ada maka pakai DEFAULT_QUESTIONS."""
    if not os.path.exists(path):
        return DEFAULT_QUESTIONS
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            choices_raw = (row.get("choices") or "").strip()
            choices = []
            if choices_raw.startswith("["):
                try:
                    choices = json.loads(choices_raw)
                except Exception:
                    pass
            if not choices:
                choices = [c.strip() for c in choices_raw.split("|") if c.strip()]
            out.append({
                "id": row.get("id") or f"q_{len(out)+1}",
                "question": (row.get("question") or "").strip(),
                "choices": choices,
                "answer": (row.get("answer") or "").strip(),
                "points": int(row.get("points") or 10),
            })
    return out or DEFAULT_QUESTIONS

def sample_questions(questions, sample_size: int):
    return random.sample(questions, min(sample_size, len(questions)))

