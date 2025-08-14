# utils/sessions.py
import os, csv, time
from typing import Dict, Any

SESSIONS_FILE = "data/sessions.csv"

def ensure_sessions_header():
    if not os.path.exists(SESSIONS_FILE) or os.path.getsize(SESSIONS_FILE) == 0:
        with open(SESSIONS_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["user","quiz_deadline_ts","code_deadline_ts","login_at_ts","logout_at_ts"])

def read_sessions() -> Dict[str, Dict[str, int]]:
    ensure_sessions_header()
    data = {}
    with open(SESSIONS_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = row["user"]
            data[uid] = {
                "quiz_deadline_ts": int(row["quiz_deadline_ts"] or 0),
                "code_deadline_ts": int(row["code_deadline_ts"] or 0),
                "login_at_ts": int(row["login_at_ts"] or 0),
                "logout_at_ts": int(row["logout_at_ts"] or 0),
            }
    return data

def write_sessions(rows: Dict[str, Dict[str, int]]):
    ensure_sessions_header()
    with open(SESSIONS_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["user","quiz_deadline_ts","code_deadline_ts","login_at_ts","logout_at_ts"])
        for uid, v in rows.items():
            w.writerow([
                uid,
                int(v.get("quiz_deadline_ts",0) or 0),
                int(v.get("code_deadline_ts",0) or 0),
                int(v.get("login_at_ts",0) or 0),
                int(v.get("logout_at_ts",0) or 0),
            ])

def upsert_session(user: str, **fields):
    rows = read_sessions()
    base = rows.get(user, {"quiz_deadline_ts":0,"code_deadline_ts":0,"login_at_ts":0,"logout_at_ts":0})
    base.update({k: fields[k] for k in fields})
    rows[user] = base
    write_sessions(rows)

def get_user_deadline_ts(user: str, section: str) -> int:
    key = f"{section}_deadline_ts"
    return read_sessions().get(user, {}).get(key, 0)

def set_user_deadline_ts(user: str, section: str, ts: int):
    key = f"{section}_deadline_ts"
    upsert_session(user, **{key: int(ts)})

def get_or_create_user_deadline(user: str, section: str, minutes: int) -> int:
    cur = get_user_deadline_ts(user, section)
    now_ts = int(time.time())
    if cur <= now_ts:
        new_ts = now_ts + minutes*60
        set_user_deadline_ts(user, section, new_ts)
        return new_ts
    return cur
