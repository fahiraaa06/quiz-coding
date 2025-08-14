# utils/code_runner.py
import io, sys, traceback, multiprocessing as mp
from typing import List, Dict, Any

def _worker_run(user_code: str, tests: List[Dict[str, Any]], q):
    ns = {}
    stdout = io.StringIO()
    try:
        old_stdout = sys.stdout
        sys.stdout = stdout
        # eksekusi: peserta harus mendefinisikan solve()
        exec(user_code, ns, ns)
        if "solve" not in ns or not callable(ns["solve"]):
            raise RuntimeError("Fungsi solve(nums) tidak ditemukan.")
        solve = ns["solve"]

        passed = 0
        details = []
        for i, t in enumerate(tests, start=1):
            try:
                out = solve(t["input"])
                ok = (out == t["expect"])
                passed += 1 if ok else 0
                details.append({
                    "case": i, "input": t["input"], "expect": t["expect"],
                    "got": out, "pass": ok
                })
            except Exception as e:
                details.append({
                    "case": i, "input": t["input"], "expect": t["expect"],
                    "got": repr(e), "pass": False
                })
        q.put({
            "ok": True,
            "passed": passed,
            "total": len(tests),
            "stdout": stdout.getvalue(),
            "details": details
        })
    except Exception as e:
        q.put({
            "ok": False,
            "error": "".join(traceback.format_exception_only(type(e), e)),
            "stdout": stdout.getvalue()
        })
    finally:
        try:
            sys.stdout = old_stdout
        except Exception:
            pass

def run_code_with_timeout(user_code: str, tests: List[Dict[str, Any]], timeout_sec: int = 6):
    q = mp.Queue()
    p = mp.Process(target=_worker_run, args=(user_code, tests, q))
    p.start()
    p.join(timeout=timeout_sec)
    if p.is_alive():
        p.terminate()
        return {"ok": False, "error": f"Timeout {timeout_sec}s tercapai."}
    return q.get() if not q.empty() else {"ok": False, "error": "Tidak ada output dari runner."}
