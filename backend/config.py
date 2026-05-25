from pathlib import Path
import os

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Application
DEBUG = os.getenv("FLASK_ENV", "production") != "production"
PORT = int(os.getenv("PORT", 5001))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/musync")

# Authentication
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://localhost:5001")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")

# Encryption
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "change_me_in_production")

# OAuth Scopes
SPOTIFY_SCOPES = (
    "playlist-read-private playlist-read-collaborative "
    "playlist-modify-public playlist-modify-private "
    "user-library-read user-library-modify "
    "user-read-private user-read-email"
)

YT_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

# Rate Limiting
API_RATE_LIMIT_REQUESTS = int(os.getenv("API_RATE_LIMIT_REQUESTS", 100))
API_RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("API_RATE_LIMIT_PERIOD_SECONDS", 60))

# Performance
BATCH_PROCESS_SIZE = int(os.getenv("BATCH_PROCESS_SIZE", 20))
MAX_CONCURRENT_WORKERS = int(os.getenv("MAX_CONCURRENT_WORKERS", 5))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validation
if not SPOTIFY_CLIENT_ID:
    print("⚠ Warning: SPOTIFY_CLIENT_ID not set")
if not SPOTIFY_CLIENT_SECRET:
    print("⚠ Warning: SPOTIFY_CLIENT_SECRET not set")
if MASTER_PASSWORD == "change_me_in_production":
    print("⚠ Warning: MASTER_PASSWORD not set (using default)")
