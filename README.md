# MuSync

MuSync is a high-performance playlist synchronization tool designed to bridge the gap between Spotify and YouTube Music. It enables bidirectional playlist transfer with intelligent fuzzy matching, ensuring high accuracy in song mapping across platforms. The application is containerized for easy deployment and features a modern React-based interface.

## Features

- **Bidirectional Synchronization**: Transfer playlists from Spotify to YouTube Music and vice versa.
- **Fuzzy Matching Algorithm**: Utilizes `RapidFuzz` to accurately match tracks between platforms despite metadata discrepancies.
- **Concurrent Processing**: Implements threaded batch processing for efficient handling of large playlists.
- **OAuth 2.0 Authentication**: Secure, token-based authentication for both Spotify and Google services.
- **Containerized Architecture**: Fully Dockerized application with Nginx reverse proxy, React frontend, and Flask backend.
- **Real-time Feedback**: WebSocket-based status updates for live progress tracking.

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS
- **Backend**: Python 3.11, Flask, Werkzeug
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Libraries**: Spotipy, ytmusicapi, RapidFuzz

## Prerequisites

Before deploying, ensure you have the following:

- **Docker Desktop** (or Docker Engine + Compose)
- **Spotify Developer Account**: Create an app to obtain `CLIENT_ID` and `CLIENT_SECRET`.
- **Google Cloud Project**: Enable YouTube Data API v3 and download the OAuth 2.0 Client ID JSON file.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/musync.git
   cd musync
   ```

2. **Configuration**

   Create a `.env` file in the root directory:

   ```env
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   FLASK_ENV=production
   ```

   Place your Google OAuth credentials file in the root directory and rename it to `client.json`.

3. **Build and Run**

   ```bash
   docker-compose up --build -d
   ```

   The application will be accessible at `http://localhost`.

## Project Structure

```
MuSync/
├── auth/               # Authentication logic (Spotify/Google)
├── clients/            # API Clients (Spotipy, ytmusicapi)
├── matching/           # Normalization and scoring algorithms
├── sync/               # Core synchronization logic
├── frontend/           # React application
├── api.py              # Flask entry point
├── config.py           # Configuration management
├── docker-compose.yml  # Container orchestration
└── Dockerfile.*        # Docker build instructions
```

## Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### Sync Interface

![Sync Interface](docs/screenshots/sync-panel.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
