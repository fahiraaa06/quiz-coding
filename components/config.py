# components/config.py
import os
from datetime import timezone, timedelta

# Direktori data
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
RESULTS_FILE  = os.path.join(DATA_DIR, "results.csv")
ATTEMPT_LOG   = os.path.join(DATA_DIR, "attempts.csv")
USERS_FILE    = os.path.join(DATA_DIR, "users.csv")
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.csv")

# Konstanta
PASSING_SCORE = 70

# Zona waktu
WIB = timezone(timedelta(hours=7))
