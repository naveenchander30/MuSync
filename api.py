from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from pathlib import Path
import sys
from collections import deque
import pickle
import os

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from state import SyncState
from sync.spotify_import import import_spotify
from sync.spotify_export import export_spotify
from sync.ytmusic_import import import_ytmusic
from sync.ytmusic_export import export_ytmusic
from config import AUTH_SERVER
from auth.token_store import JSONTokenStore

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global state
sync_state = SyncState()
sync_logs = deque(maxlen=1000)
is_running = False
current_task = None

store = JSONTokenStore()

# Thread lock for state updates
state_lock = threading.Lock()


def log_message(msg):
    """Add a timestamped log message"""
    timestamp = time.strftime('%H:%M:%S')
    with state_lock:
        sync_logs.append(f"[{timestamp}] {msg}")


def check_auth(service):
    """Check if service is authenticated"""
    if service == "ytmusic":
        try:
            if not os.path.exists("yt_creds.pkl"):
                return False
            with open("yt_creds.pkl", "rb") as f:
                creds = pickle.load(f)
            return creds and creds.valid
        except Exception:
            return False
            
    token = store.load(service)
    return token is not None and not store.is_expired(token)


def run_sync_task(task_func, task_name, service):
    """Run a sync task in background"""
    global is_running, current_task
    
    with state_lock:
        is_running = True
        current_task = task_name
        sync_state.reset()
        sync_logs.clear()
    
    log_message(f"🚀 Starting: {task_name}")
    
    def progress_callback(state):
        """Callback for task progress updates"""
        log_message(f"Processing: {state.current_playlist or 'Initializing...'}")
    
    try:
        task_func(AUTH_SERVER, sync_state, progress_callback)
        log_message(f"✅ Completed: {task_name}")
        log_message(f"📊 Added: {len(sync_state.added)} | Failed: {len(sync_state.failed)}")
    except Exception as e:
        log_message(f"❌ Error: {str(e)}")
    finally:
        with state_lock:
            is_running = False
            current_task = None


# API Routes
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "MuSync API is running"})


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Get authentication status for all services"""
    return jsonify({
        "spotify": check_auth("spotify"),
        "ytmusic": check_auth("ytmusic")
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current sync status and logs"""
    with state_lock:
        return jsonify({
            "is_running": is_running,
            "current_task": current_task,
            "current_playlist": sync_state.current_playlist,
            "added": len(sync_state.added),
            "failed": len(sync_state.failed),
            "logs": list(sync_logs)[-50:]  # Last 50 logs
        })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get all logs"""
    with state_lock:
        return jsonify({"logs": list(sync_logs)})


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all logs"""
    with state_lock:
        sync_logs.clear()
    return jsonify({"status": "ok"})


@app.route('/api/sync/export/spotify', methods=['POST'])
def export_spotify_route():
    """Export playlists from Spotify"""
    if not check_auth("spotify"):
        return jsonify({"error": "Not authenticated with Spotify"}), 401
    
    if is_running:
        return jsonify({"error": "A sync task is already running"}), 409
    
    # Run in background thread
    thread = threading.Thread(
        target=run_sync_task,
        args=(export_spotify, "Export Spotify", "spotify")
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "task": "Export Spotify"})


@app.route('/api/sync/export/ytmusic', methods=['POST'])
def export_ytmusic_route():
    """Export playlists from YouTube Music"""
    if not check_auth("ytmusic"):
        return jsonify({"error": "Not authenticated with YouTube Music"}), 401
    
    if is_running:
        return jsonify({"error": "A sync task is already running"}), 409
    
    thread = threading.Thread(
        target=run_sync_task,
        args=(export_ytmusic, "Export YouTube Music", "ytmusic")
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "task": "Export YouTube Music"})


@app.route('/api/sync/import/spotify', methods=['POST'])
def import_spotify_route():
    """Import playlists to Spotify"""
    if not check_auth("spotify"):
        return jsonify({"error": "Not authenticated with Spotify"}), 401
    
    if is_running:
        return jsonify({"error": "A sync task is already running"}), 409
    
    thread = threading.Thread(
        target=run_sync_task,
        args=(import_spotify, "Import to Spotify", "spotify")
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "task": "Import to Spotify"})


@app.route('/api/sync/import/ytmusic', methods=['POST'])
def import_ytmusic_route():
    """Import playlists to YouTube Music"""
    if not check_auth("ytmusic"):
        return jsonify({"error": "Not authenticated with YouTube Music"}), 401
    
    if is_running:
        return jsonify({"error": "A sync task is already running"}), 409
    
    thread = threading.Thread(
        target=run_sync_task,
        args=(import_ytmusic, "Import to YouTube Music", "ytmusic")
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "task": "Import to YouTube Music"})


if __name__ == '__main__':
    import os
    print("🎵 MuSync API Server")
    print(f"📡 Auth Server: {AUTH_SERVER}")
    print("🚀 Starting on http://localhost:5001")
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
