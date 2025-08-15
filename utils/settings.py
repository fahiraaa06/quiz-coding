import os, json
from datetime import datetime
from typing import Optional, Tuple
from components.config import WIB, POST_WINDOW_FILE, POST_START, POST_END

def _ensure_dir():
    d = os.path.dirname(POST_WINDOW_FILE)
    if d:
        os.makedirs(d, exist_ok=True)

def _serialize(dt: datetime) -> str:
    # Simpan ISO string dengan offset WIB, contoh: 2025-08-07T09:00:00+07:00
    return dt.astimezone(WIB).isoformat(timespec="seconds")

def _parse_local_iso(s: str) -> datetime:
    """
    Terima string dari input <input type="datetime-local"> yang TIDAK ada offset,
    contoh: '2025-08-07T09:00'. Anggap itu WIB.
    """
    # fromisoformat untuk 'YYYY-MM-DDTHH:MM' → naive
    dt = datetime.fromisoformat(s)
    # pasang tz WIB
    return dt.replace(tzinfo=WIB)

def get_post_window() -> Tuple[datetime, datetime]:
    """
    Kembalikan (start, end) jendela post-test.
    - Jika file setting ada → gunakan isinya
    - Jika tidak → fallback ke config.POST_START/POST_END
    """
    if os.path.exists(POST_WINDOW_FILE) and os.path.getsize(POST_WINDOW_FILE) > 0:
        try:
            with open(POST_WINDOW_FILE, encoding="utf-8") as f:
                obj = json.load(f) or {}
            s = obj.get("start")
            e = obj.get("end")
            if s and e:
                # s & e disimpan dalam ISO dengan offset; fromisoformat bisa parsing offset
                start = datetime.fromisoformat(s)
                end   = datetime.fromisoformat(e)
                return start, end
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return POST_START, POST_END

def set_post_window(start_local_str: str, end_local_str: str) -> None:
    """
    Terima string dari form (datetime-local, tanpa offset), jadikan WIB, validasi, lalu simpan.
    """
    start = _parse_local_iso(start_local_str)
    end   = _parse_local_iso(end_local_str)
    if end <= start:
        raise ValueError("End time harus lebih besar dari start time.")

    _ensure_dir()
    with open(POST_WINDOW_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"start": _serialize(start), "end": _serialize(end)},
            f, ensure_ascii=False, indent=2
        )

def clear_post_window() -> None:
    """Hapus file setting agar fallback ke default config."""
    try:
        if os.path.exists(POST_WINDOW_FILE):
            os.remove(POST_WINDOW_FILE)
    except OSError:
        pass

def window_open(now: Optional[datetime] = None) -> bool:
    """
    True jika 'now' berada dalam [start, end].
    """
    if now is None:
        now = datetime.now(WIB)
    start, end = get_post_window()
    return start <= now <= end
