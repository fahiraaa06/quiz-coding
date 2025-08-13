# pages/admin_page.py
import os
from taipy.gui import notify
from state import ADMIN_PASSWORD, ATTEMPT_LOG, RESULTS_FILE
from utils.storage import ensure_results_header
from utils.timers import set_user_deadline_ts
from utils.auth import admin_login  # akan kamu terima filenya setelah ini

def reset_attempts(s):
    """Hapus attempts.csv di folder data."""
    try:
        if os.path.exists(ATTEMPT_LOG):
            os.remove(ATTEMPT_LOG)
        notify(s, "success", "attempts.csv direset.")
    except OSError as e:
        notify(s, "error", f"Gagal reset attempts: {e.strerror}")

def reset_results(s):
    """Reset results.csv (buat ulang dengan header)."""
    try:
        if os.path.exists(RESULTS_FILE):
            os.remove(RESULTS_FILE)
        ensure_results_header()
        notify(s, "success", "results.csv direset.")
    except OSError as e:
        notify(s, "error", f"Gagal reset results: {e.strerror}")

def upload_questions_csv(s):
    """
    Simpan bank soal yang di-upload admin.
    Catatan: quiz_page saat ini membaca dari 'questions.csv' (root project).
    Jika mau pindah ke data/questions.csv, kita bisa update quiz_page.py untuk pakai path itu.
    """
    up = getattr(s, "questions_file", None)
    if up is None:
        notify(s, "warning", "Pilih file CSV terlebih dahulu.")
        return
    try:
        with open("questions.csv", "wb") as f:
            f.write(up["content"])  # Taipy file_selector mengembalikan dict {name, content, ...}
        notify(s, "success", "questions.csv disimpan. Akan terpakai saat halaman Quiz dibuka.")
    except OSError as e:
        notify(s, "error", f"Gagal menyimpan questions.csv: {e.strerror}")

def reset_deadline(s):
    """Reset deadline user untuk section quiz/code (agar timer mulai ulang saat dibuka lagi)."""
    r_uid = getattr(s, "r_uid", "").strip()
    r_section = getattr(s, "r_section", "quiz")
    if not r_uid:
        notify(s, "warning", "Isi user/email terlebih dahulu.")
        return
    if r_section not in ("quiz", "code"):
        notify(s, "warning", "Section tidak valid (pilih 'quiz' atau 'code').")
        return
    try:
        set_user_deadline_ts(r_uid, r_section, 0)
        notify(s, "success", f"Deadline {r_section} untuk {r_uid} direset.")
    except Exception as e:  # noqa: BLE001 (ingin menangkap error tak terduga agar admin dapat notifikasi)
        notify(s, "error", f"Gagal reset deadline: {type(e).__name__}")

page = r"""
{{navbar}}
# 🔐 Admin Panel

<|Password admin|label|>
<|{admin_pwd}|input|type=password|>
<|Login Admin|button|on_action=admin_login|>

<|part|class_name=card p-2|
### Reset Data
<|Reset attempts.csv|button|on_action=reset_attempts|>
<|Reset results.csv|button|on_action=reset_results|>
|>

<|part|class_name=card p-2|
### Upload bank soal (questions.csv)
Format header: `id,question,choices,answer,points` (choices boleh JSON list atau dipisah `|`).

<|{questions_file}|file_selector|extensions=.csv|>
<|Simpan|button|on_action=upload_questions_csv|>
|>

<|part|class_name=card p-2|
### Reset Deadline User
<|User/email|label|> <|{r_uid}|input|>
<|Section|label|> <|{r_section}|selector|lov=quiz;code|dropdown|value=quiz|>
<|Reset Deadline|button|on_action=reset_deadline|>
|>
"""

