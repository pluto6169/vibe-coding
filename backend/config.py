import os
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# File limitations
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}

ALLOWED_MIMES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "image/png": ".png",
    "image/jpeg": ".jpg"
}

# Auto-detect Tesseract cmd or use default
TESSERACT_CMD = os.getenv("TESSERACT_CMD", shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe")

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'metascholar.db'}"
