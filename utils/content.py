# utils/content.py (tambahan & perubahan saja)
import json, os, shutil, csv
from typing import List, Dict, Any, Optional
from components.config import (
    QUESTIONS_DIR, QUESTIONS_ACTIVE,
    PROBLEMS_DIR, PROBLEM_ACTIVE_FILE,
    ACTIVE_MANIFEST,
)
from components.constants import DEFAULT_QUESTIONS

def _read_manifest() -> Dict[str, str]:
    if not os.path.exists(ACTIVE_MANIFEST):
        return {}
    try:
        with open(ACTIVE_MANIFEST, encoding="utf-8") as f:
            obj = json.load(f) or {}
        if not isinstance(obj, dict):
            return {}
        return obj
    except (OSError, json.JSONDecodeError):
        return {}

def _write_manifest(d: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(ACTIVE_MANIFEST), exist_ok=True)
    with open(ACTIVE_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def get_active_questions_name() -> Optional[str]:
    m = _read_manifest()
    return m.get("questions_active")  # nama file di QUESTIONS_DIR

def get_active_problem_name() -> Optional[str]:
    m = _read_manifest()
    return m.get("problem_active")  # nama file di PROBLEMS_DIR

def set_active_questions_name(filename: str) -> None:
    m = _read_manifest()
    m["questions_active"] = filename
    _write_manifest(m)

def set_active_problem_name(filename: str) -> None:
    m = _read_manifest()
    m["problem_active"] = filename
    _write_manifest(m)

# --- yang sudah ada ---
def list_question_sets() -> List[str]:
    os.makedirs(QUESTIONS_DIR, exist_ok=True)
    return sorted([fn for fn in os.listdir(QUESTIONS_DIR)
                   if os.path.isfile(os.path.join(QUESTIONS_DIR, fn)) and fn.lower().endswith(".csv")])

def list_problems() -> List[str]:
    os.makedirs(PROBLEMS_DIR, exist_ok=True)
    return sorted([fn for fn in os.listdir(PROBLEMS_DIR)
                   if os.path.isfile(os.path.join(PROBLEMS_DIR, fn)) and fn.lower().endswith(".json")])

def activate_questions(filename: str) -> None:
    """Pilih file CSV bernama 'filename' di QUESTIONS_DIR sebagai aktif:
       1) salin → QUESTIONS_ACTIVE (kompatibel runtime)
       2) simpan nama aktif ke manifest (untuk UI)"""
    if not filename:
        raise ValueError("Nama file CSV tidak boleh kosong.")
    src = os.path.join(QUESTIONS_DIR, filename)
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Tidak ada: {src}")
    os.makedirs(os.path.dirname(QUESTIONS_ACTIVE), exist_ok=True)
    shutil.copyfile(src, QUESTIONS_ACTIVE)
    set_active_questions_name(filename)

def activate_problem(filename: str) -> None:
    """Pilih file JSON bernama 'filename' di PROBLEMS_DIR sebagai aktif:
       1) validasi → salin → PROBLEM_ACTIVE_FILE
       2) simpan nama aktif ke manifest"""
    if not filename:
        raise ValueError("Nama file JSON tidak boleh kosong.")
    src = os.path.join(PROBLEMS_DIR, filename)
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Tidak ada: {src}")

    with open(src, encoding="utf-8") as f:
        json.load(f)  # hanya memastikan bisa di-load tanpa error

    os.makedirs(os.path.dirname(PROBLEM_ACTIVE_FILE), exist_ok=True)
    shutil.copyfile(src, PROBLEM_ACTIVE_FILE)
    set_active_problem_name(filename)

def get_active_questions_path() -> str:
    return QUESTIONS_ACTIVE

def read_active_questions(load_csv_func) -> List[Dict[str, Any]]:
    path = QUESTIONS_ACTIVE
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            data = load_csv_func(path)
            return data or DEFAULT_QUESTIONS
    except (OSError, csv.Error, ValueError) as e:
        print(f"[WARN] load questions failed: {e}")
    return DEFAULT_QUESTIONS
