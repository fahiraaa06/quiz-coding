import os
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from taipy.gui import notify
from components.constants import DEFAULT_QUESTIONS
from components.config import RESULTS_FILE, ATTEMPT_LOG, USERS_FILE, SESSIONS_FILE, WIB
from utils.quiz_utils import load_questions_from_csv, sample_questions

logger = logging.getLogger(__name__)

# ====== CONFIG QUIZ ======
POST_TEST_MODE = True
POST_START = datetime(2025, 8, 7, 9, 0, tzinfo=WIB)
POST_END = datetime(2025, 8, 31, 23, 59, tzinfo=WIB)
PASSING_SCORE = 70
MAX_ATTEMPTS = 1
IDENTITY_FIELD = "email"
QUESTION_SAMPLE = 5
QUIZ_DURATION_MIN = 12
CODE_DURATION_MIN = 20
CODE_TIMEOUT_SEC = 6
ADMIN_PASSWORD = os.environ.get("BOOTCAMP_ADMIN_PASS", "intelligo-admin")

# ====== GLOBAL RUNTIME STATE ======
auth = False
user = ""
login_email = ""
login_password = ""
login_window_text = f"{POST_START.strftime('%d %b %Y %H:%M')} - {POST_END.strftime('%d %b %Y %H:%M')} WIB"
page = "home"

nav_items = [
    ("/quiz", "Quiz"),
    ("/result", "Result"),
]

def on_nav(state, _var_name, value):
    """Handler perubahan navbar/menu."""
    state.page = value
    if value == "/quiz":
        init_quiz(state)

# ====== QUIZ STATE ======
sampled_questions: List[Dict[str, Any]] = []
quiz_score: int = 0
quiz_submitted: bool = False
quiz_deadline = None

# Variabel UI
quiz_timer_text: str = ""
quiz_body: str = ""
quiz_content: str = ""

# ---- Helpers ----
def _load_question_bank() -> List[Dict[str, Any]]:
    try:
        qs = load_questions_from_csv("./data/questions.csv")
        if qs:
            logger.info(f"Loaded {len(qs)} questions from CSV")
            return qs
        logger.warning("File questions.csv kosong, menggunakan DEFAULT_QUESTIONS.")
    except FileNotFoundError:
        logger.warning("File questions.csv tidak ditemukan, menggunakan DEFAULT_QUESTIONS.")
    except (ValueError, OSError) as e:
        logger.error(f"Gagal memuat questions.csv: {e}")
    return DEFAULT_QUESTIONS

def _ensure_sampled_questions(state):
    if not getattr(state, "sampled_questions", None):
        qs = _load_question_bank()
        state.sampled_questions = sample_questions(qs, QUESTION_SAMPLE)
        logger.info(f"Sampled {len(state.sampled_questions)} questions")

    for q in state.sampled_questions:
        key = f"ans_{q['id']}"
        if not hasattr(state, key):
            setattr(state, key, None)

def _lov_from_choices(choices):
    return ";".join(str(c) for c in choices)

def _compute_timer_text(state) -> str:
    if not state.quiz_deadline:
        return "⏳ Timer belum dimulai"

    now = datetime.now(tz=WIB)
    remaining = int((state.quiz_deadline - now).total_seconds())
    if remaining <= 0:
        if not state.quiz_submitted:
            action_submit_quiz(state)
        return "00:00"

    mins, secs = divmod(remaining, 60)
    return f"{mins:02d}:{secs:02d}"

def _render_quiz(state) -> str:
    _ensure_sampled_questions(state)
    if not state.sampled_questions:
        logger.warning("Tidak ada soal yang bisa ditampilkan.")
        return "**Belum ada soal yang tersedia.**"

    parts = []
    for idx, q in enumerate(state.sampled_questions, start=1):
        key = f"ans_{q['id']}"
        lov = _lov_from_choices(q.get("choices", []))
        parts.append(
            f"<|part|class_name=card p-3 mb-2 shadow-sm|>\n"
            f"**{idx}. {q.get('question', 'Pertanyaan kosong')}**\n"
            f"<|{{{key}}}|selector|lov={lov}|dropdown|class_name=full-width|>\n"
            "|>"
        )
    html = "\n".join(parts)
    logger.debug(f"render_quiz: built {len(parts)} blocks, length={len(html)}")
    return html

# ====== Actions ======
def submit_quiz(state):
    _ensure_sampled_questions(state)
    score = 0
    total_points = 0
    for q in state.sampled_questions:
        total_points += int(q.get("points", 10))
        ans = getattr(state, f"ans_{q['id']}")
        if ans == q["answer"]:
            score += int(q.get("points", 10))
    state.quiz_score = score
    state.quiz_submitted = True
    notify(state, "success", f"Skor quiz: {score}/{total_points}")

def action_submit_quiz(state):
    submit_quiz(state)
    state.page = "/result"

# ====== Lifecycle ======
def init_quiz(state):
    """Reset quiz, mulai timer, dan siapkan konten."""
    _ensure_sampled_questions(state)
    state.quiz_submitted = False
    state.quiz_score = 0
    state.quiz_deadline = datetime.now(tz=WIB) + timedelta(minutes=QUIZ_DURATION_MIN)

    body = _render_quiz(state)
    state.quiz_body = body
    state.quiz_content = body
    state.quiz_timer_text = _compute_timer_text(state)
    logger.info("Quiz initialized")

def update_quiz_timer(state):
    state.quiz_timer_text = _compute_timer_text(state)
