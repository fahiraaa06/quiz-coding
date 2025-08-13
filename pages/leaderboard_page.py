# pages/leaderboard_page.py
import os
from state import RESULTS_FILE

# state vars yang akan dipakai di template:
# - leaderboard_df (opsional, kalau pandas ada)
# - leaderboard_csv (string untuk download)

def refresh_leaderboard(s):
    """Muat & urutkan leaderboard dari RESULTS_FILE."""
    if not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0:
        s.leaderboard_csv = "Belum ada hasil."
        # kosongkan tampilan tabel jika ada
        if hasattr(s, "leaderboard_df"):
            s.leaderboard_df = None
        return

    try:
        import pandas as pd
    except ImportError:
        # fallback tanpa pandas: hanya siapkan file untuk diunduh
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            s.leaderboard_csv = f.read()
        return

    df = pd.read_csv(RESULTS_FILE)
    # urutkan: total desc, lalu quiz_score desc, coding_score desc
    df = df.sort_values(
        by=["total", "quiz_score", "coding_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    # Simpan untuk tampilan tabel dan download
    s.leaderboard_df = df
    s.leaderboard_csv = df.to_csv(index=False)


page = r"""
        {{navbar}}
        # 🏆 Leaderboard
        
        <|Muat / Refresh Leaderboard|button|on_action=refresh_leaderboard|>
        
        <|{leaderboard_csv}|file_download|file_name=results.csv|label=⬇️ Unduh results.csv|>
        
        <|{leaderboard_df}|table|editable=False|show_all=True|rebuild|>
        
        > Kolom: `user, quiz_score, coding_score, total, passed, timestamp`.
        """