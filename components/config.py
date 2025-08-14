# components/config.py
from datetime import datetime, timezone, timedelta
import os

# Zona waktu
WIB = timezone(timedelta(hours=7))

# Mode & jendela post-test
POST_TEST_MODE = True
POST_START = datetime(2025, 8, 7, 9, 0, tzinfo=WIB)
POST_END   = datetime(2025, 8, 31, 23, 59, tzinfo=WIB)

# Parameter penilaian & durasi
PASSING_SCORE = 70
MAX_ATTEMPTS = 1
IDENTITY_FIELD = "email"
QUESTION_SAMPLE = 5
QUIZ_DURATION_MIN = 12
CODE_DURATION_MIN = 20
CODE_TIMEOUT_SEC = 6

# Lokasi file data
USERS_FILE = "data/users.csv"
RESULTS_FILE = "data/results.csv"
ATTEMPT_LOG = "data/attempts.csv"
SESSIONS_FILE = "data/sessions.csv"

# Admin
ADMIN_PASSWORD = os.environ.get("BOOTCAMP_ADMIN_PASS", "intelligo-admin")

# Soal coding (single problem)
PROBLEM = {
    "id": "p1",
    "title": "Sum of Numbers",
    "prompt": """Buat fungsi `solve(nums: list[int]) -> int` yang mengembalikan jumlah semua angka di nums.
Contoh:
- solve([1,2,3]) -> 6
- solve([]) -> 0
""",
    "starter_code": """# Lengkapi fungsi di bawah ini
def solve(nums: list[int]) -> int:
    # TODO: kembalikan jumlah semua angka
    # hint: gunakan built-in sum()
    pass
""",
    "tests": [
        {"input":[1,2,3], "expect":6},
        {"input":[-1,1,5], "expect":5},
        {"input":[], "expect":0},
        {"input":[10], "expect":10},
        {"input":[100, -50, -25], "expect":25},
    ],
    "points": 70,
}
