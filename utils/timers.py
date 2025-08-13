# utils/timers.py
import os, csv, time
from typing import Dict, Any
from components.config import SESSIONS_FILE

# ===== Session CSV helpers =====
def ensure_sessions_header():
    """Pastikan file sesi ada dan punya header."""
    if not os.path.exists(SESSIONS_FILE) or os.path.getsize(SESSIONS_FILE) == 0:
        with open(SESSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["user", "quiz_deadline_ts", "code_deadline_ts", "login_at_ts", "logout_at_ts"])

def read_sessions() -> Dict[str, Dict[str, Any]]:
    ensure_sessions_header()
    data = {}
    with open(SESSIONS_FILE, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            uid = row["user"]
            data[uid] = {
                "quiz_deadline_ts": int(row["quiz_deadline_ts"]) if row["quiz_deadline_ts"] else 0,
                "code_deadline_ts": int(row["code_deadline_ts"]) if row["code_deadline_ts"] else 0,
                "login_at_ts": int(row["login_at_ts"]) if row["login_at_ts"] else 0,
                "logout_at_ts": int(row["logout_at_ts"]) if row["logout_at_ts"] else 0,
            }
    return data

def write_sessions(all_rows: Dict[str, Dict[str, Any]]):
    ensure_sessions_header()
    with open(SESSIONS_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user", "quiz_deadline_ts", "code_deadline_ts", "login_at_ts", "logout_at_ts"])
        for uid, v in all_rows.items():
            w.writerow([
                uid,
                int(v.get("quiz_deadline_ts", 0) or 0),
                int(v.get("code_deadline_ts", 0) or 0),
                int(v.get("login_at_ts", 0) or 0),
                int(v.get("logout_at_ts", 0) or 0),
            ])

def upsert_session(user: str, **fields):
    rows = read_sessions()
    base = rows.get(user, {"quiz_deadline_ts": 0, "code_deadline_ts": 0, "login_at_ts": 0, "logout_at_ts": 0})
    base.update({k: fields[k] for k in fields})
    rows[user] = base
    write_sessions(rows)

# ===== Deadline Helpers =====
def get_user_deadline_ts(user: str, section: str) -> int:
    rows = read_sessions()
    cur = rows.get(user, {})
    key = f"{section}_deadline_ts"
    return int(cur.get(key, 0) or 0)

def set_user_deadline_ts(user: str, section: str, ts: int):
    key = f"{section}_deadline_ts"
    upsert_session(user, **{key: int(ts)})

def get_or_create_user_deadline(user: str, section: str, minutes: int) -> int:
    """Ambil deadline user untuk section, buat baru jika belum ada atau sudah lewat."""
    cur = get_user_deadline_ts(user, section)
    now_ts = int(time.time())
    if cur <= now_ts:
        new_ts = now_ts + minutes * 60
        set_user_deadline_ts(user, section, new_ts)
        return new_ts
    return cur

def format_mmss(sec: int) -> str:
    mm = sec // 60
    ss = sec % 60
    return f"{mm:02d}:{ss:02d}"

def timer_text(user: str, section: str, minutes: int) -> str:
    """Mengembalikan string countdown untuk user pada section tertentu."""
    deadline_ts = get_or_create_user_deadline(user, section, minutes)
    left = max(0, int(deadline_ts - time.time()))

    if left <= 0:
        return f"⏳ Waktu {section} telah habis"
    return f"⏳ Waktu tersisa {section}: {format_mmss(left)}"

