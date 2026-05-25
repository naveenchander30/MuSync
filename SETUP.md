# MuSync 2.0 - Self-Hosting Guide

Complete setup guide for running MuSync on your own infrastructure.

## Overview

MuSync is a self-hosted playlist synchronization engine that bridges Spotify and YouTube Music. You provide your own API keys, and everything runs locally on your machine or server.

**No external services required** - no Render, no cloud dependencies, no third-party auth servers.

## Prerequisites

- Docker & Docker Compose
- Spotify Developer Account (free)
- Google Cloud Account (free)
- PostgreSQL (included in Docker Compose)

## Step 1: Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in and click **"Create App"**
3. Fill in:
   - **App name**: MuSync (or whatever you prefer)
   - **App description**: Playlist sync tool
   - **Redirect URI**: `http://localhost:5001/auth/spotify/callback` (or your domain)
4. Click **Save**
5. Copy the **Client ID** and **Client Secret**

## Step 2: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**:
   - Navigate to **APIs & Services** → **Library**
   - Search for "YouTube Data API v3" and enable it
4. Create OAuth credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **"+ CREATE CREDENTIALS"** → **OAuth client ID**
   - **Application type**: Web application
   - **Name**: MuSync
   - **Authorized JavaScript origins**: `http://localhost` (or your domain)
   - **Authorized redirect URIs**: `http://localhost:5001/auth/ytmusic/callback` (or your domain)
5. Click **Create**
6. Copy the **Client ID** and **Client Secret**

## Step 3: Configure Environment

Clone the repository:

```bash
git clone https://github.com/naveenchander30/MuSync.git
cd MuSync
```

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Required
AUTH_BASE_URL=http://localhost:5001
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/musync
MASTER_PASSWORD=your_secure_password_here

# Optional
LOG_LEVEL=INFO
PORT=5001
```

## Step 4: Start the Application

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** database (port 5432)
- **MuSync Backend** (port 5001)

## Step 5: Access the Application

Open your browser: `http://localhost:5001`

### First-time Setup

1. Click **Connect Spotify** in the sidebar
2. Authorize the app with your Spotify account
3. Click **Connect YouTube Music** in the sidebar
4. Authorize the app with your Google account
5. Start syncing!

## Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AUTH_BASE_URL` | Yes | Base URL for OAuth redirects |
| `SPOTIFY_CLIENT_ID` | Yes | Spotify OAuth client ID |
| `SPOTIFY_CLIENT_SECRET` | Yes | Spotify OAuth client secret |
| `GOOGLE_OAUTH_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `MASTER_PASSWORD` | Yes | Encryption key for stored tokens |
| `LOG_LEVEL` | No | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `PORT` | No | Backend port (default: 5001) |
| `API_RATE_LIMIT_REQUESTS` | No | Max API requests per period (default: 100) |
| `API_RATE_LIMIT_PERIOD_SECONDS` | No | Rate limit period (default: 60) |
| `BATCH_PROCESS_SIZE` | No | Tracks per batch (default: 20) |
| `MAX_CONCURRENT_WORKERS` | No | Concurrent workers (default: 5) |

### Production Deployment

For production, update `AUTH_BASE_URL` to your domain:

```bash
AUTH_BASE_URL=https://musync.yourdomain.com
```

And update OAuth redirect URIs in both Spotify and Google consoles to match.

### SSL/HTTPS

For production use, place a reverse proxy (Nginx/Caddy) in front:

```nginx
server {
    listen 443 ssl;
    server_name musync.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### "Not authenticated" errors
- Verify OAuth redirect URIs match your `AUTH_BASE_URL`
- Check that credentials are correctly set in `.env`

### Database connection errors
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

### Token refresh failures
- Re-authenticate by clicking Connect in the sidebar
- Check that `MASTER_PASSWORD` hasn't changed

## Data Storage

All data is stored in PostgreSQL:
- OAuth tokens (encrypted)
- Sync job history
- Scheduled jobs
- Activity logs

Data persists across restarts via Docker volumes.

## Backup

To backup your data:

```bash
docker-compose exec postgres pg_dump -U postgres musync > musync_backup.sql
```

To restore:

```bash
docker-compose exec -T postgres psql -U postgres musync < musync_backup.sql
```

## Architecture

```
┌─────────────────────────────────────┐
│           Your Browser              │
│        http://localhost:5001        │
└────────────────┬────────────────────┘
                 │
                 v
┌─────────────────────────────────────┐
│         MuSync Backend              │
│   Flask + APScheduler               │
│   - OAuth handling                  │
│   - Sync orchestration              │
│   - Scheduled jobs                  │
└────────────────┬────────────────────┘
                 │
        ┌────────┴────────┐
        v                 v
┌──────────────┐  ┌──────────────┐
│ PostgreSQL   │  │ Spotify API  │
│ Database     │  │ YouTube API  │
│ (encrypted)  │  │              │
└──────────────┘  └──────────────┘
```
