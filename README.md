# 🎵 MuSync

> **Transfer playlists seamlessly between Spotify and YouTube Music**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

MuSync is a modern, production-ready music synchronization tool that makes transferring your playlists between Spotify and YouTube Music effortless. Built with reliability, performance, and user experience at its core.

---

## ✨ Features

- 🔄 **Bidirectional Sync** - Transfer playlists between Spotify and YouTube Music in both directions
- 🎯 **Smart Matching** - Advanced fuzzy matching algorithm with confidence scoring
- 📊 **Real-Time Dashboard** - Beautiful, modern UI with live progress tracking
- ⚡ **High Performance** - Batch processing with concurrent operations and rate limiting
- 🔒 **Secure Authentication** - OAuth 2.0 flow with automatic token refresh
- 💾 **Backup & Export** - Save your playlists locally as JSON files
- 🐳 **Docker Ready** - One-command deployment with Docker Compose
- 📝 **Activity Logs** - Detailed logging of every sync operation

---

## 📸 Screenshots

### Landing Page

> _Beautiful hero section with clear call-to-action_

![Landing Page](docs/screenshots/landing-page.png)

### Dashboard

> _Real-time sync statistics and activity logs_

![Dashboard](docs/screenshots/dashboard.png)

### Sync Control Panel

> _One-click actions for all sync operations_

![Sync Panel](docs/screenshots/sync-panel.png)

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│   Render (Cloud Auth)       │
│   - OAuth Callbacks         │  ← Registered with Spotify/Google APIs
│   - Token Management        │
└──────────────┬──────────────┘
               │ Shares tokens.json
               ↓
┌─────────────────────────────┐
│   Docker (Local/Cloud)      │
│  ┌────────────────────────┐ │
│  │  React Frontend        │ │  ← Modern UI (Port 3000)
│  │  - Landing Page        │ │
│  │  - Dashboard           │ │
│  │  - Real-time Updates   │ │
│  └────────────────────────┘ │
│  ┌────────────────────────┐ │
│  │  Flask REST API        │ │  ← Backend (Port 5001)
│  │  - Sync Endpoints      │ │
│  │  - Status Management   │ │
│  └────────────────────────┘ │
│  ┌────────────────────────┐ │
│  │  Sync Engine           │ │
│  │  - Batch Processing    │ │
│  │  - Rate Limiting       │ │
│  │  - Track Matching      │ │
│  └────────────────────────┘ │
└─────────────────────────────┘
```

### Tech Stack

**Backend:**

- Python 3.11+
- Flask (REST API)
- Threading (Background Tasks)
- RapidFuzz (Fuzzy Matching)
- Spotipy & ytmusicapi (API Clients)

**Frontend:**

- React 18
- Vite (Build Tool)
- Tailwind CSS (Styling)
- Axios (HTTP Client)

**Infrastructure:**

- Docker & Docker Compose
- Nginx (Production Server)
- OAuth 2.0 (Authentication)

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Spotify Developer Account ([Create one](https://developer.spotify.com/dashboard))
- Google Cloud OAuth credentials ([Setup guide](https://console.cloud.google.com))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/MuSync.git
cd MuSync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Auth Server (Already deployed on Render)
MUSYNC_AUTH_SERVER=https://musync-k60r.onrender.com

# Spotify OAuth (Get from https://developer.spotify.com/dashboard)
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret

# Google OAuth (Get from https://console.cloud.google.com)
GOOGLE_OAUTH_CLIENT_FILE=client.json
```

### 3. Add OAuth Credentials

Place your Google OAuth credentials in `client.json` at the root directory:

```json
{
  "installed": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uris": ["http://localhost:8080/"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### 4. Launch with Docker

```bash
docker-compose up -d
```

### 5. Access MuSync

Open your browser and navigate to:

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **API:** [http://localhost:5001](http://localhost:5001)

---

## 📖 Usage Guide

### First-Time Setup

1. **Open MuSync** at http://localhost:3000
2. **Click "Get Started"** on the landing page
3. **Connect Services** in the sidebar:
   - Click "Connect" next to Spotify
   - Click "Connect" next to YouTube Music
4. **Complete OAuth** flows in the popup windows
5. **Return to Dashboard** - You're ready to sync!

### Syncing Playlists

#### Export (Backup)

1. Go to **Sync** tab
2. Click **"Export from Spotify"** or **"Export from YouTube Music"**
3. Wait for completion - playlists saved to `playlists.json`

#### Import (Restore)

1. Ensure you have exported playlists first
2. Go to **Sync** tab
3. Click **"Import to Spotify"** or **"Import to YouTube Music"**
4. Monitor progress in real-time

### Monitoring

- **Dashboard** shows:
  - Total tracks added
  - Failed tracks (with reasons)
  - Current playlist being processed
  - Live activity logs

---

## 🛠️ Development

### Running Locally (Without Docker)

**Backend:**

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask API
python api.py
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Access:

- Frontend: http://localhost:3000
- Backend API: http://localhost:5001

### Project Structure

```
MuSync/
├── frontend/                # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── LandingPage.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SyncPanel.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
├── auth/                    # OAuth authentication
│   ├── server.py           # Flask auth server
│   └── token_store.py      # Token management
├── clients/                 # API clients
│   ├── spotify_client.py
│   └── ytmusic_client.py
├── matching/                # Track matching logic
│   ├── normalize.py
│   └── scorer.py
├── sync/                    # Sync operations
│   ├── batch_processor.py  # Batch processing
│   ├── spotify_export.py
│   ├── spotify_import.py
│   ├── ytmusic_export.py
│   └── ytmusic_import.py
├── api.py                   # Main Flask API
├── state.py                 # State management
├── config.py                # Configuration
├── docker-compose.yml       # Docker orchestration
├── Dockerfile.backend       # Backend container
├── Dockerfile.frontend      # Frontend container
└── requirements.txt         # Python dependencies
```

---

## 🔐 Authentication Flow

MuSync uses a hybrid authentication approach:

1. **User clicks "Connect"** in the sidebar
2. **Browser redirects** to Render-hosted auth server
3. **Auth server handles OAuth** with Spotify/Google
4. **Tokens saved** to `tokens.json` (shared volume)
5. **Local app reads tokens** from shared file
6. **Automatic refresh** when tokens expire

**Why separate auth server?**

- OAuth redirect URIs are registered with Spotify/Google and cannot change
- Keeps the main app portable while auth stays stable
- Allows for easy credential rotation

---

## 📊 API Endpoints

| Method | Endpoint                   | Description                        |
| ------ | -------------------------- | ---------------------------------- |
| `GET`  | `/api/health`              | Health check                       |
| `GET`  | `/api/auth/status`         | Check auth status for all services |
| `GET`  | `/api/status`              | Get current sync progress          |
| `GET`  | `/api/logs`                | Retrieve all activity logs         |
| `POST` | `/api/logs/clear`          | Clear activity logs                |
| `POST` | `/api/sync/export/spotify` | Export Spotify playlists           |
| `POST` | `/api/sync/export/ytmusic` | Export YouTube Music playlists     |
| `POST` | `/api/sync/import/spotify` | Import playlists to Spotify        |
| `POST` | `/api/sync/import/ytmusic` | Import playlists to YouTube Music  |

---

## 🤝 Contributing

Contributions are welcome! This project was built as a technical demonstration for Google STEP, but improvements and suggestions are appreciated.

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Spotify Web API** for music streaming integration
- **YouTube Music API** for video music platform support
- **RapidFuzz** for high-performance fuzzy string matching
- **Tailwind CSS** for modern, responsive styling
- **React** for building interactive user interfaces

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/MuSync/issues) page
2. Review existing discussions
3. Open a new issue with detailed information

---

## 🎯 Roadmap

- [ ] Support for Apple Music
- [ ] Automatic periodic sync
- [ ] Playlist collaboration features
- [ ] Mobile app (React Native)
- [ ] Advanced filtering and matching options
- [ ] Export to CSV/Excel formats

---

<div align="center">

**Made with ❤️ for seamless music synchronization**

[⬆ Back to Top](#-musync)

</div>
