# pages/code_page.py
from taipy.gui import notify
from state import PROBLEM, CODE_TIMEOUT_SEC, CODE_DURATION_MIN
from utils.code_runner import run_code_with_timeout
from utils.timers import timer_text

# Pakai alias variabel agar template tidak melakukan indexing dict
problem_title = PROBLEM["title"]
problem_prompt = PROBLEM["prompt"]

# --- Actions -----------------------------------------------------------------
def clear_code_output(s):
    s.code_stdout = ""
    s.code_error = ""
    s.code_runtime_ms = None
    s.code_details = []
    s.code_passed = None
    s.code_total = None

def run_code_check(s):
    import time
    t0 = time.time()
    result = run_code_with_timeout(s.code_text, PROBLEM["tests"], timeout_sec=CODE_TIMEOUT_SEC)
    s.code_runtime_ms = int((time.time() - t0) * 1000)

    if result.get("ok"):
        s.code_stdout = result.get("stdout", "")
        s.code_error = ""
        s.code_details = result.get("details", [])
        s.code_passed = result.get("passed", 0)
        s.code_total = result.get("total", 0)
        notify(s, "success", f"Lulus {s.code_passed}/{s.code_total} test.")
    else:
        s.code_stdout = result.get("stdout", "")
        s.code_error = result.get("error", "Gagal menjalankan kode.")
        s.code_details = []
        s.code_passed = None
        s.code_total = None
        notify(s, "error", "Gagal menjalankan kode.")

def submit_code(s):
    result = run_code_with_timeout(s.code_text, PROBLEM["tests"], timeout_sec=CODE_TIMEOUT_SEC)
    if result.get("ok"):
        passed = result["passed"]; total = result["total"]
        s.coding_score = int(PROBLEM["points"] * (passed / total))
        s.code_stdout = result.get("stdout", "")
        s.code_error = ""
        s.code_details = result.get("details", [])
        s.code_passed = passed
        s.code_total = total
        notify(s, "success", f"Skor coding: {s.coding_score}/{PROBLEM['points']} (lulus {passed}/{total} test)")
    else:
        s.code_error = result.get("error", "")
        notify(s, "error", "Gagal menjalankan kode.")

# --- Page Template ------------------------------------------------------------
page = r"""
{{navbar}}
# 💻 Coding Test — {problem_title}

<|{timer_text(_user, 'code', CODE_DURATION_MIN)}|text|>
<|⟳ Refresh waktu|button|on_action=go_code|>

<|layout|columns=7 5|gap=16px|

<|part|class_name=card p-2|height=100%|
### 📘 Deskripsi Soal
{problem_prompt}

### Editor
<|{code_text}|input|type=textarea|rows=18|>

<|Jalankan & Cek|button|on_action=run_code_check|class_name=primary|>
<|Bersihkan Output|button|on_action=clear_code_output|>
<|Kumpulkan Jawaban|button|on_action=submit_code|class_name=success|>
|>

<|part|class_name=card p-2|height=100%|
### Output
<|Runtime: {code_runtime_ms} ms|text|visible={code_runtime_ms is not None}|>

**Hasil Test:** {code_passed}/{code_total}

<|Detail Hasil|expander|expanded=False|
<|{code_details}|json|>
|>

**Stdout (print):**
<|{code_stdout}|text|rebuild|>

<|Terjadi error saat eksekusi:|text|visible={len(code_error)>0}|>
<|{code_error}|text|visible={len(code_error)>0}|rebuild|>
|>

|>
"""
