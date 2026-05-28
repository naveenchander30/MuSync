# MuSync 2.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask_3.0-000000.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

**MuSync** is a self-hosted playlist synchronization engine that bridges Spotify and YouTube Music. You provide your own API keys, everything runs locally.

## Features

- **Self-Hosted**: No external services, no cloud dependencies. Runs entirely on your machine
- **Bidirectional Sync**: Transfer playlists both ways (Spotify ↔ YouTube Music)
- **Smart Matching**: Conservative fuzzy matching with weighted scoring (name 60%, artist 35%, duration 5%)
- **Scheduled Sync**: Automated sync jobs with configurable intervals via APScheduler
- **Encrypted Tokens**: OAuth refresh tokens encrypted with AES-256-GCM
- **Resumable Syncs**: Checkpoint system to resume failed syncs from where they stopped
- **Real-Time Dashboard**: Live sync progress, track-by-track display, and sync history
- **Rate-Limited**: Token bucket algorithm prevents API throttling
- **Neo Design**: Minimalist dark UI with true black background, Inter typography, and sharp edges

## Prerequisites

- Docker & Docker Compose
- Spotify Developer Account (free)
- Google Cloud Account (free)

## Quick Start

### 1. Get API Credentials

**Spotify:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Set Redirect URI: `http://localhost:5001/auth/spotify/callback`
4. Copy Client ID and Client Secret

**Google:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Web application)
4. Set Redirect URI: `http://localhost:5001/auth/ytmusic/callback`
5. Copy Client ID and Client Secret

### 2. Clone & Configure

```bash
git clone https://github.com/naveenchander30/MuSync.git
cd MuSync
cp .env.example .env
```

Edit `.env` with your credentials:

```env
AUTH_BASE_URL=http://localhost:5001
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/musync
MASTER_PASSWORD=your_secure_password
```

### 3. Start

```bash
docker-compose up -d
```

Open `http://localhost:5001` and connect your accounts.

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Architecture

```
┌─────────────────────────────────────┐
│           Your Browser              │
│        http://localhost:5001        │
└────────────────┬────────────────────┘
                 │
                 v
┌─────────────────────────────────────┐
│         Flask Backend               │
│  - OAuth handling                   │
│  - Sync orchestration               │
│  - APScheduler (cron jobs)          │
│  - Encrypted token storage          │
│  - REST API (JSON)                  │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        v                 v
┌──────────────┐  ┌──────────────┐
│ PostgreSQL   │  │ External APIs│
│ Database     │  │ Spotify      │
│ (encrypted)  │  │ YouTube Music│
└──────────────┘  └──────────────┘
```

The frontend is a single-page React app served by the Flask backend. The backend exposes a JSON REST API for sync operations, scheduling, and authentication.

## Project Structure

```
MuSync/
├── backend/
│   ├── app.py                 # Flask application entry
│   ├── config.py              # Environment configuration
│   ├── requirements.txt       # Python dependencies
│   ├── auth/                  # OAuth & token management
│   ├── database/              # SQLAlchemy models
│   ├── sync/                  # Sync engine & matching
│   ├── scheduler/             # APScheduler integration
│   ├── api/                   # REST API routes
│   ├── utils/                 # Logging & helpers
│   └── tests/                 # Python test suite
├── frontend/
│   ├── src/
│   │   ├── components/        # React components (Neo design)
│   │   ├── test/              # Frontend test suite (Vitest)
│   │   ├── App.jsx            # App root with routing
│   │   ├── api.js             # API client (Axios)
│   │   └── index.css          # Tailwind base styles
│   └── tailwind.config.js     # Design tokens (Neo theme)
├── docker-compose.yml         # Docker orchestration
├── Dockerfile.backend         # Backend container
├── Dockerfile.frontend        # Frontend container
├── SETUP.md                   # Detailed setup guide
└── .env.example               # Environment template
```

## Testing

```bash
# Backend tests
cd backend
pip install -r requirements.txt
pytest tests/ -v

# Frontend tests
cd frontend
npm install
npx vitest run
```

## License

MIT License - see [LICENSE](LICENSE)
