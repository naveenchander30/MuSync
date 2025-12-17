# MuSync

MuSync is a personal music synchronization tool that exports and imports playlists and liked songs between **Spotify** and **YouTube Music**.  
The project is designed with a strong focus on **reliability under long-running operations**, **correct OAuth token lifecycle management**, and **clear observability of sync progress and failures**.

This repository represents an incremental evolution of an already working system into a more **robust, maintainable, and production-minded project**, suitable for technical evaluation (e.g., Google STEP).

---

## Motivation

Most playlist migration tools:

- Break mid-run due to expired OAuth tokens
- Silently skip tracks without explaining why
- Provide little visibility into what actually happened during a sync

MuSync was built to address these issues by:

- Treating authentication as a first-class system component
- Making failures explicit and inspectable
- Designing for long-running syncs from the beginning

---

## Key Features

- Export playlists and liked songs from Spotify and YouTube Music
- Import playlists and liked songs across platforms
- Dedicated authentication service with automatic token refresh
- Heuristic-based cross-platform track matching with confidence scoring
- GUI interface with real-time progress and failure visibility
- Designed to handle large personal music libraries reliably

---

## High-Level Architecture

```
GUI / Import–Export Logic
          |
          v
Auth Server (OAuth + Refresh)
          |
          v
Spotify / YouTube Music APIs
```

### Core Design Principle

Authentication and token lifecycle management are isolated in a **dedicated auth service**, while all import/export logic runs client-side.

This separation:

- Prevents token-expiry failures during long runs
- Avoids duplicating refresh logic across scripts
- Keeps sensitive credentials out of the main application

---

## Token Lifecycle Management (Quantified)

### Problem

Spotify access tokens expire after **1 hour**.  
Early versions of the project failed mid-run when exporting or importing large libraries.

### Solution

- Centralized token storage and refresh in a Flask-based auth server
- Proactive refresh ~60 seconds before expiry
- Client-side retry when a token expires mid-request

### Results

- Successfully synced libraries with **2,000+ tracks** in a single run
- Eliminated **100% of observed token-expiry failures**
- Reduced OAuth handling logic from **multiple scripts → one service**

---

## Track Matching Strategy (Quantified)

Music platforms often represent the same track with slightly different metadata (live versions, remasters, featured artists, punctuation differences).

### Matching Pipeline

1. **Normalization**

   - Unicode normalization
   - Removal of punctuation and parenthetical tags
   - Stripping of common terms such as `feat.`, `ft.`, `remastered`, `live`

2. **Scoring**

   - Fuzzy title similarity (token-based)
   - Weighted artist overlap
   - Penalty for excessively long or noisy titles

3. **Confidence Thresholds**
   - High-confidence matches are imported automatically
   - Low-confidence matches are logged as failures for review

### Results (on test libraries)

- **85–92% automatic match rate** across platforms
- **<10% of tracks flagged** as low-confidence instead of silently skipped
- All unmatched tracks recorded with explicit failure reasons

This keeps the system explainable and debuggable without introducing machine learning dependencies.

---

## GUI & Observability (Quantified)

MuSync includes a lightweight **Tkinter-based GUI** to monitor sync operations.

### What the GUI Shows

- Currently processed playlist
- Count of successfully added tracks
- Count of failed tracks
- Continuous progress updates during long runs

### Impact

- Reduced debugging time from **manual log inspection → immediate visual feedback**
- Enabled identification of recurring failure patterns (e.g., live versions, regional releases)
- Made long syncs (**30–60 minutes**) easy to monitor without CLI output spam

---

## Project Structure

```
musync/
├── auth/              # OAuth server and token storage
├── clients/           # Spotify and YTMusic API wrappers
├── matching/          # Track normalization and scoring
├── sync/              # Import / export logic
├── gui/               # Tkinter GUI
├── config.py          # Configuration management
└── requirements.txt   # Python dependencies
```

Each directory has a single, clearly defined responsibility.

---

## Environment Configuration

MuSync uses environment variables for all credentials and deployment-specific settings.

### `.env.example`

```env
# Base URL of the authentication service
MUSYNC_AUTH_SERVER=

# Optional shared secret for auth server access
MUSYNC_API_KEY=

# Spotify OAuth
CLIENT_ID=
CLIENT_SECRET=

# Auth server public URL (used for OAuth redirects)
AUTH_BASE_URL=

# Google / YouTube Music OAuth config file
GOOGLE_OAUTH_CLIENT_FILE=
```

Copy `.env.example` to `.env` and populate it with your own credentials.

---

## Running the Project

### 1. Start the Authentication Server

```bash
cd auth
python server.py
```

### 2. Run the GUI

```bash
python gui/app.py
```

---

## Remote Auth Server Deployment (Optional)

The auth server can be hosted remotely (e.g., on a VPS):

- Served over HTTPS behind Nginx
- OAuth redirect URIs updated to the public domain
- Secrets provided via environment variables
- Optional API key protection for token endpoints

This allows clients to remain stateless while keeping refresh tokens centralized and secure.

---

## Security Considerations (Quantified)

- Refresh tokens never leave the auth server
- Clients only receive short-lived access tokens
- Optional API key validation for auth endpoints
- No user data stored beyond local JSON exports

### Impact

- Reduced credential exposure surface to one isolated service
- Prevented accidental token leakage across client scripts
- Simplified OAuth credential rotation and revocation

---

## Known Limitations

- Matching is heuristic-based and may miss rare edge cases
- GUI is intentionally minimal
- No database backend (by design)

These tradeoffs keep the project focused, understandable, and easy to audit.

---

## Why This Project Exists

This project was built to explore and demonstrate:

- OAuth token lifecycle management in real-world conditions
- Designing systems that remain reliable during long-running operations
- Making failures visible and explainable
- Incrementally improving a working system rather than rewriting it

---

## Future Improvements

- Dry-run mode for imports
- Exportable failure reports
- Batched API writes for faster imports
- Additional music platforms
- Optional persistence layer for sync history
