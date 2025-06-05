import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pitch.db")

# File Storage
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Analysis Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation").split(",")

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found in environment variables. AI analysis will not work.")
else:
    print(f"Groq API key found: {GROQ_API_KEY[:5]}...{GROQ_API_KEY[-4:]}")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure AI API Key is set (check for either OpenAI or Groq)
if not OPENAI_API_KEY and not GROQ_API_KEY:
    print("Warning: Neither OPENAI_API_KEY nor GROQ_API_KEY found in environment variables. AI analysis will not work.")

# Ensure OpenAI API Key is set
# if not OPENAI_API_KEY:
#     print("Warning: OPENAI_API_KEY not found in environment variables. AI analysis will not work.") 