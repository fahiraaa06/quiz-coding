# components/constants.py
from typing import List, Dict, Any

DEFAULT_QUESTIONS: List[Dict[str, Any]] = [
    {"id": "q1", "question": "Di Python, struktur data untuk pasangan kunci-nilai adalah?", "choices": ["list", "tuple", "set", "dict"], "answer": "dict", "points": 10},
    {"id": "q2", "question": "Kompleksitas waktu pencarian rata-rata pada dict (hash map)?", "choices": ["O(n)", "O(log n)", "O(1)", "O(n log n)"], "answer": "O(1)", "points": 10},
    {"id": "q3", "question": "Perintah membuat virtual env (Python 3.10+) adalah?", "choices": ["pip venv .venv", "python -m venv .venv", "conda create venv", ".venv activate"], "answer": "python -m venv .venv", "points": 10},
    {"id": "q4", "question": "Library untuk manipulasi data tabular di Python?", "choices": ["matplotlib", "pandas", "seaborn", "numpy"], "answer": "pandas", "points": 10},
    {"id": "q5", "question": "SQL untuk menggabungkan baris dari dua tabel berdasarkan kondisi sama?", "choices": ["GROUP BY", "JOIN", "WHERE", "ORDER BY"], "answer": "JOIN", "points": 10},
    {"id": "q6", "question": "Tipe data tak berurutan dan unik di Python?", "choices": ["dict", "set", "list", "tuple"], "answer": "set", "points": 10},
    {"id": "q7", "question": "Metode Pandas untuk menghapus NA?", "choices": ["fillna", "dropna", "replace", "astype"], "answer": "dropna", "points": 10},
]
