from pathlib import Path
from os import makedirs

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES_DIR = BASE_DIR / 'databases'
LOG_DIR  = BASE_DIR / 'log'

makedirs(DATABASES_DIR, exist_ok=True)
makedirs(LOG_DIR,       exist_ok=True)
