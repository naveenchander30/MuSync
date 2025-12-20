# <img src="docs/logo.svg" width="50" height="50" align="center" alt="MuSync Logo"/> MuSync

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask_2.3-000000.svg)](https://flask.palletsprojects.com/)

**MuSync** is an enterprise-grade playlist synchronization engine designed to bridge the ecosystem gap between Spotify and YouTube Music. Engineered for high performance and reliability, it enables bidirectional playlist transfer with intelligent fuzzy matching, ensuring 99% accuracy in song mapping across platforms.

Refurnished with a modern React architecture and containerized for cloud-native deployment, MuSync represents a robust solution for cross-platform music library management.

## 🚀 Key Features

- **Bidirectional Synchronization Engine**: Seamlessly transfer playlists from Spotify to YouTube Music and vice versa, preserving track order and metadata.
- **Intelligent Fuzzy Matching**: Leverages `RapidFuzz` to implement advanced string matching algorithms, handling metadata discrepancies (e.g., "Feat." artists, remastered tags) with high precision.
- **High-Concurrency Architecture**: Implements a threaded batch processing system with rate limiting and exponential backoff to handle large datasets efficiently.
- **Secure Authentication**: Built on OAuth 2.0 standards, ensuring secure, token-based access to user data without compromising credentials.
- **Cloud-Native Design**: Fully containerized using Docker and Docker Compose, orchestrating a Flask backend, React frontend, and Nginx reverse proxy.
- **Real-time Observability**: Provides WebSocket-based live status updates and detailed transaction logs for complete process visibility.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 (Vite)
- **Styling**: Tailwind CSS (Modern, Responsive Design)
- **State Management**: React Hooks & Context
- **Assets**: Custom SVG Graphics & Icons

### Backend
- **Core**: Python 3.11, Flask
- **Processing**: ThreadPoolExecutor (Concurrency), collections.deque (Memory Management)
- **Algorithms**: RapidFuzz (String Matching)
- **APIs**: Spotipy (Spotify Web API), ytmusicapi (YouTube Music API)

### DevOps & Infrastructure
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (Reverse Proxy & Static Serving)

## 📋 Prerequisites

- **Docker Desktop** (or Docker Engine + Compose)
- **Spotify Developer Credentials**: Obtain `CLIENT_ID` and `CLIENT_SECRET` from the [Spotify Dashboard](https://developer.spotify.com/dashboard).
- **Google Cloud Credentials**: Enable YouTube Data API v3 and download the OAuth 2.0 Client ID JSON file.

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/musync.git
cd musync
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
# Optional: Set a custom auth server URL if not running locally
# MUSYNC_AUTH_SERVER=https://your-deployment-url.com
```

### 3. Setup Credentials

- Place your Google OAuth JSON file in the root as `client.json`.
- (The application will handle token generation on first login).

### 4. Deploy with Docker

```bash
docker-compose up --build -d
```

Access the application dashboard at **http://localhost:3000**.

## 📂 Project Architecture

```
MuSync/
├── api.py              # Flask Application Entry Point
├── auth/               # OAuth 2.0 Authentication Handlers
├── clients/            # API Wrapper Clients (Retry Logic/Error Handling)
├── config.py           # Environment Configuration
├── docker-compose.yml  # Container Orchestration
├── Dockerfile.*        # Multi-stage Build Definitions
├── docs/               # Documentation & Assets
├── frontend/           # React Single Page Application (SPA)
├── matching/           # Intelligent Scoring Algorithms
└── sync/               # Core Synchronization Logic
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
