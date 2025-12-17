import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Auth server configuration
AUTH_SERVER = os.getenv("MUSYNC_AUTH_SERVER", "http://localhost:8080")
API_KEY = os.getenv("MUSYNC_API_KEY", "")

# Spotify OAuth credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Auth server base URL (for OAuth redirects)
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://localhost:8080")

# Google OAuth client file path
GOOGLE_OAUTH_CLIENT_FILE = os.getenv("GOOGLE_OAUTH_CLIENT_FILE", "client.json")
