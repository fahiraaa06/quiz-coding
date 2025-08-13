# pages/result_page.py
from taipy.gui import notify
from state import PASSING_SCORE,nav_items, page, on_nav, quiz_score, PASSING_SCORE
from utils.storage import save_result, read_attempts, write_attempt

def save_final(s):
    """Simpan nilai akhir ke results.csv dan catat attempt."""
    if not getattr(s, "_user", ""):
        notify(s, "warning", "Belum login.")
        return
    total, passed = save_result(s._user, s.quiz_score, s.coding_score)
    used = read_attempts().get(s._user, 0) + 1
    write_attempt(s._user, used)
    status = "LULUS" if passed else "TIDAK LULUS"
    notify(s, "success", f"Hasil disimpan. Status: {status}. Attempt: {used}")

page_result = r"""
<|navbar|lov={nav_items}|value={page}|on_change=on_nav|>
# 📊 Hasil
<|layout|columns=1 1 1|gap=16px|
<|Skor Quiz: {quiz_score}|text|>
<|Skor Coding: {coding_score}|text|>
<|Total: {quiz_score + coding_score}|text|>
|>
<|Passing Grade: {PASSING_SCORE}|>
<|Simpan Nilai (final)|button|on_action=save_final|class_name=primary|>
"""