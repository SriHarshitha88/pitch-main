import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = "sqlite:///./pitch.db"

# File Storage
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Security
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS
ALLOWED_ORIGINS = ["http://localhost:3000"]

# Analysis Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
] 