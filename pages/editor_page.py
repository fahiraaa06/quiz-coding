# pages/editor_page.py
from taipy.gui import notify
import contextlib
import io
import time
import traceback

def _ensure_init(s):
    if not hasattr(s, "user_code") or s.user_code is None:
        s.user_code = (
            '# Contoh: semua yang di-print akan muncul di panel Output\n'
            'print("Halo dari Intelligo ID!")\n'
            'for i in range(3):\n'
            '    print("i =", i)\n'
            "\n"
            "# Silakan ubah kode ini, lalu klik 'Jalankan'\n"
        )
    if not hasattr(s, "last_stdout"):
        s.last_stdout = ""
    if not hasattr(s, "last_stderr"):
        s.last_stderr = ""
    if not hasattr(s, "last_error"):
        s.last_error = ""
    if not hasattr(s, "last_runtime"):
        s.last_runtime = None

def run_code(s):
    _ensure_init(s)
    code = s.user_code
    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
    t0 = time.time()
    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            exec(code, {}, {})  # nosec: demo
        s.last_error = ""
        notify(s, "success", "Kode berhasil dijalankan.")
    except Exception as e:  # noqa: BLE001
        s.last_error = traceback.format_exc()
        notify(s, "error", f"Terjadi error saat eksekusi: {type(e).__name__}")
    finally:
        s.last_runtime = int((time.time() - t0) * 1000)
        s.last_stdout = stdout_buf.getvalue()
        s.last_stderr = stderr_buf.getvalue()

def clear_output(s):
    _ensure_init(s)
    s.last_stdout = ""
    s.last_stderr = ""
    s.last_error = ""
    s.last_runtime = None
    notify(s, "info", "Output dibersihkan.")

page = r"""
{{navbar}}
# 💻 Halaman Ngoding & 🔎 Output

<|layout|columns=7 5|gap=16px|

<|part|class_name=card p-2|height=100%|
## Editor
<|{user_code}|input|type=textarea|rows=22|>

<|Jalankan|button|class_name=primary|on_action=run_code|>
<|Bersihkan Output|button|on_action=clear_output|>
|>

<|part|class_name=card p-2|height=100%|
## Output

<|Runtime: {last_runtime} ms|text|visible={last_runtime is not None}|>

**Stdout (print):**
<|{last_stdout}|text|rebuild|>

**Stderr:**
<|{last_stderr}|text|rebuild|>

<|Terjadi error saat eksekusi:|text|visible={len(last_error)>0}|>
<|{last_error}|text|visible={len(last_error)>0}|rebuild|>
|>

|>
"""
