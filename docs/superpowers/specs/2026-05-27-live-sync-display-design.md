# Live Sync Display Design

## Summary

Add live progress display to MuSync's Dashboard showing which playlist and track the orchestrator is currently processing during an active sync, including album art for the current track.

## Data Model

Add 4 nullable columns to `SyncJob`:

| Column | Type | Source |
|--------|------|--------|
| `current_playlist_name` | `db.String(255)` | Set before processing each playlist |
| `current_track_name` | `db.String(255)` | Set before processing each track |
| `current_track_artist` | `db.String(255)` | Parsed from track's artist list |
| `current_track_image_url` | `db.Text` | Album art URL from API response |

These are nullable — null when no sync is active or the orchestrator hasn't started processing tracks yet.

No migration tooling. `db.create_all()` on fresh DB picks them up. For existing dev SQLite DBs, add in conftest.py.

## Orchestrator Changes (`backend/sync/orchestrator.py`)

### `sync_spotify_to_ytmusic`

Before processing each playlist (after `self.log(f"Processing playlist: {playlist['name']}")`):
```python
job.current_playlist_name = playlist['name']
job.current_track_name = None
job.current_track_image_url = None
```

Before searching each track (in the `for track_data in spotify_tracks` loop):
```python
query_track = ... (existing)
job.current_track_name = query_track['name']
job.current_track_artist = ", ".join(query_track['artists'])
# Album art from Spotify track object
track_obj = track.get('track', {})
album = track_obj.get('album', {})
images = album.get('images', [])
job.current_track_image_url = images[0]['url'] if images else None
```

### `sync_ytmusic_to_spotify`

Same pattern — current playlist name before processing, current track info before searching.

Album art for YT Music source: YT Music search results return `thumbnails` on track items. Use `track_data.get('thumbnails', [])[-1]['url']` if available, else null.

## API Changes (`backend/api/routes.py`)

`GET /api/jobs/<job_id>` — add 4 new fields to response:

```python
"current_playlist_name": job.current_playlist_name,
"current_track_name": job.current_track_name,
"current_track_artist": job.current_track_artist,
"current_track_image_url": job.current_track_image_url,
```

`GET /api/jobs/user/<user_id>` — unchanged (list endpoint stays lightweight).

## Frontend Changes (`frontend/src/components/Dashboard.jsx`)

The Dashboard already polls `endpoints.jobs.getByUser` every 3s and shows a "Sync in Progress" banner for running jobs. Enhance the banner:

### Current banner layout
```
┌──────────────────────────────────────────────────────┐
│  ● Sync in Progress                    45%   +8     │
│  Spotify → YT Music                         ████░░  │
└──────────────────────────────────────────────────────┘
```

### New banner layout (Option 1 — album art + playlist, then track)
```
┌──────────────────────────────────────────────────────┐
│  ● Sync in Progress          Progress   Tracks       │
│                             ████████░░░░  45%   +8   │
├──────────────────────────────────────────────────────┤
│  [img 48x48]  Playlist: Chill Vibes                  │
│              → Now: Breathe — Artist Name            │
└──────────────────────────────────────────────────────┘
```

- Album art: `<img>` tag with the `current_track_image_url`, 48x48 rounded
- "Playlist: {name}" shows current playlist
- "→ Now: {track} — {artist}" shows current track
- If image_url is null, show a muted placeholder div
- If no sync is running, hide the extra info row entirely

## Album Art Sourcing

- **Spotify API**: `track['album']['images'][0]['url']` — always available for Spotify tracks
- **YT Music API**: `thumbnails[-1]['url']` from search results — may be absent; handle gracefully
- No caching or downloading on the backend. URLs are passed through as-is.
- Frontend loads images directly from CDN URLs.

## Testing

### Backend tests
- Update `test_orchestrator.py`: Verify `current_playlist_name`, `current_track_name`, `current_track_artist`, `current_track_image_url` are set during mocked sync calls
- No new test file needed — extend existing orchestrator tests

### Frontend tests
- Update `Dashboard.test.jsx`: Verify album art img appears in banner, playlist name shown, track info shown
- Mock `current_track_image_url` in test data
- Test null image_url shows placeholder

## Files Modified

1. `backend/database/models.py` — 4 new columns on SyncJob
2. `backend/sync/orchestrator.py` — set fields during playlist/track processing
3. `backend/api/routes.py` — add 4 fields to job detail response
4. `frontend/src/components/Dashboard.jsx` — enhanced live banner
5. `backend/tests/test_orchestrator.py` — verify new fields
6. `frontend/src/test/Dashboard.test.jsx` — test new banner content
