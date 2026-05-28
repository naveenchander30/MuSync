# Live Sync Display Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add live progress display to the Dashboard showing the current playlist and track being processed during an active sync, including album art.

**Architecture:** 4 nullable columns on SyncJob store live state. Orchestrator sets them during its loop. Existing `GET /api/jobs/<id>` returns them. Frontend Dashboard banner reads them via existing 3s polling. Album art URLs pass through from API responses.

**Tech Stack:** Flask/SQLAlchemy, React, polling-based updates

---

### Task 1: Add live state columns to SyncJob model

**Files:**
- Modify: `backend/database/models.py`

- [ ] **Step 1: Add 4 new columns to SyncJob**

After `progress_percentage = db.Column(db.Integer, default=0)` (line 54), add:

```python
    current_playlist_name = db.Column(db.String(255), nullable=True)
    current_track_name = db.Column(db.String(255), nullable=True)
    current_track_artist = db.Column(db.String(255), nullable=True)
    current_track_image_url = db.Column(db.Text, nullable=True)
```

- [ ] **Step 2: Run model tests to verify**

Run: `python -m pytest backend/tests/test_models.py -v 2>&1 | tail -10` (from `/home/neo/Projects/Musync`)
Expected: All model tests pass (test DB uses `db.create_all()` so new columns exist)

- [ ] **Step 3: Commit**

```bash
git add backend/database/models.py
git commit -m "feat: add live sync state columns to SyncJob"
```

---

### Task 2: Set live fields in orchestrator

**Files:**
- Modify: `backend/sync/orchestrator.py`

- [ ] **Step 1: Add live field updates to `sync_spotify_to_ytmusic`**

After `self.log(f"Processing playlist: {playlist['name']}")` (line 91), add:

```python
            job.current_playlist_name = playlist['name']
            job.current_track_name = None
            job.current_track_image_url = None
```

After `track = track_data.get('track', {})` (line 125), add:

```python
                    job.current_track_name = track.get('name', '')
                    job.current_track_artist = ", ".join([a.get('name', '') for a in track.get('artists', [])])
                    album = track.get('album', {})
                    images = album.get('images', [])
                    job.current_track_image_url = images[0].get('url') if images else None
```

- [ ] **Step 2: Add live field updates to `sync_ytmusic_to_spotify`**

After `self.log(f"Processing playlist: {playlist.get('title', 'Unknown')}")` (line 250), add:

```python
            job.current_playlist_name = playlist.get('title', 'Unknown')
            job.current_track_name = None
            job.current_track_image_url = None
```

After `query_track = {...}` (line 281), add:

```python
                    job.current_track_name = track_data.get('title', '')
                    job.current_track_artist = ", ".join([a.get('name', '') for a in track_data.get('artists', [])])
                    thumbnails = track_data.get('thumbnails', [])
                    job.current_track_image_url = thumbnails[-1].get('url') if thumbnails else None
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_orchestrator.py -v 2>&1 | tail -10` (from `/home/neo/Projects/Musync`)
Expected: All pass (new columns exist, fields are set)

- [ ] **Step 4: Commit**

```bash
git add backend/sync/orchestrator.py
git commit -m "feat: set current playlist/track fields during sync"
```

---

### Task 3: Return live fields in job detail endpoint

**Files:**
- Modify: `backend/api/routes.py`

- [ ] **Step 1: Add 4 fields to `GET /api/jobs/<job_id>` response**

After `"error_message": job.error_message` (line 131), add:

```python
        "current_playlist_name": job.current_playlist_name,
        "current_track_name": job.current_track_name,
        "current_track_artist": job.current_track_artist,
        "current_track_image_url": job.current_track_image_url,
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest backend/tests/test_api.py -v 2>&1 | tail -10` (from `/home/neo/Projects/Musync`)
Expected: All pass

- [ ] **Step 3: Commit**

```bash
git add backend/api/routes.py
git commit -m "feat: return live sync fields in job detail endpoint"
```

---

### Task 4: Update Dashboard live banner in frontend

**Files:**
- Modify: `frontend/src/components/Dashboard.jsx`

- [ ] **Step 1: Add live display row to active sync banner**

Replace the active sync banner JSX block (lines 110-142) with:

```jsx
        {activeJob && (
          <div className="mb-8 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 border border-blue-500/30 rounded-2xl p-6 animate-pulse-slow">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-4 h-4 bg-blue-400 rounded-full" />
                  <div className="absolute inset-0 w-4 h-4 bg-blue-400 rounded-full animate-ping opacity-50" />
                </div>
                <div>
                  <div className="text-blue-400 font-bold text-xl">Sync in Progress</div>
                  <div className="text-gray-400 text-sm">{formatDirection(activeJob.source_service, activeJob.target_service)}</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-gray-400 text-xs uppercase tracking-wider">Progress</div>
                  <div className="text-white font-bold text-2xl">{activeJob.progress_percentage}%</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-400 text-xs uppercase tracking-wider">Tracks</div>
                  <div className="text-emerald-400 font-bold text-lg">+{activeJob.added_tracks || 0}</div>
                </div>
                <div className="w-48 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${activeJob.progress_percentage}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-blue-500/20 flex items-center gap-4">
              {activeJob.current_track_image_url ? (
                <img
                  src={activeJob.current_track_image_url}
                  alt="Album art"
                  className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-lg">🎵</span>
                </div>
              )}
              <div className="min-w-0">
                {activeJob.current_playlist_name && (
                  <div className="text-gray-400 text-sm truncate">
                    Playlist: <span className="text-white">{activeJob.current_playlist_name}</span>
                  </div>
                )}
                {activeJob.current_track_name && (
                  <div className="text-gray-300 text-sm truncate mt-0.5">
                    <span className="text-blue-400">→</span> Now: <span className="text-white font-medium">{activeJob.current_track_name}</span>
                    {activeJob.current_track_artist && (
                      <span className="text-gray-400"> — {activeJob.current_track_artist}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
```

- [ ] **Step 2: Run frontend tests**

Run: `npx vitest run` (from `/home/neo/Projects/Musync/frontend`)
Expected: All 40 pass

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/Dashboard.jsx
git commit -m "feat: add live playlist/track display to dashboard banner"
```

---

### Task 5: Update backend orchestrator tests

**Files:**
- Modify: `backend/tests/test_orchestrator.py`

- [ ] **Step 1: Add album art to Spotify mock track + add live field assertions**

Change the mock track at lines 49-55 to include album data:

```python
            mock_spotify_instance.get_playlist_tracks.return_value = [
                {
                    'track': {
                        'name': 'Song 1',
                        'artists': [{'name': 'Artist 1'}],
                        'duration_ms': 200000,
                        'album': {
                            'images': [
                                {'url': 'https://example.com/art.jpg', 'width': 640, 'height': 640}
                            ]
                        }
                    }
                }
            ]
```

After line 84 (`assert latest_job.added_tracks == 1`), add:

```python
            assert latest_job.current_playlist_name == 'Test Playlist'
            assert latest_job.current_track_name == 'Song 1'
            assert latest_job.current_track_artist == 'Artist 1'
            assert latest_job.current_track_image_url == 'https://example.com/art.jpg'
```

- [ ] **Step 2: Add thumbnails to YT mock track + add live field assertions**

Change the YT mock track at lines 211-217 to include thumbnails:

```python
            mock_ytmusic_instance.get_playlist.return_value = {
                'tracks': [
                    {
                        'title': 'Song 1',
                        'artists': [{'name': 'Artist 1'}],
                        'duration_seconds': 200,
                        'thumbnails': [
                            {'url': 'https://example.com/yt_thumb.jpg', 'width': 120}
                        ]
                    }
                ]
            }
```

After line 244 (`assert latest_job.status == 'success'`), add:

```python
            assert latest_job.current_playlist_name == 'YT Playlist'
            assert latest_job.current_track_name == 'Song 1'
            assert latest_job.current_track_artist == 'Artist 1'
            assert latest_job.current_track_image_url == 'https://example.com/yt_thumb.jpg'
```

- [ ] **Step 3: Run orchestrator tests**

Run: `python -m pytest backend/tests/test_orchestrator.py -v 2>&1 | tail -15` (from `/home/neo/Projects/Musync`)
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_orchestrator.py
git commit -m "test: verify live sync fields in orchestrator tests"
```

---

### Task 6: Update frontend Dashboard tests

**Files:**
- Modify: `frontend/src/test/Dashboard.test.jsx`

- [ ] **Step 1: Add live fields to running job mock data**

Add to the running job (job_3) after `progress_percentage: 45` (line 43):

```jsx
    current_playlist_name: "My Mix",
    current_track_name: "Test Song",
    current_track_artist: "Test Artist",
    current_track_image_url: "https://example.com/art.jpg",
```

- [ ] **Step 2: Add tests for live banner display**

After the "shows added tracks count in banner" test (line 106), add:

```jsx
  it("shows current playlist name in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText("My Mix")).toBeInTheDocument();
    });
  });

  it("shows current track info in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Test Song/)).toBeInTheDocument();
    });
  });

  it("shows album art image in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      const img = screen.getByAltText("Album art");
      expect(img).toHaveAttribute("src", "https://example.com/art.jpg");
    });
  });

  it("shows track artist in banner", async () => {
    render(<Dashboard />);
    await waitFor(() => {
      expect(screen.getByText(/Test Artist/)).toBeInTheDocument();
    });
  });
```

- [ ] **Step 3: Run frontend tests**

Run: `npx vitest run` (from `/home/neo/Projects/Musync/frontend`)
Expected: All pass (44 tests — 40 old + 4 new)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/test/Dashboard.test.jsx
git commit -m "test: verify live sync display in dashboard tests"
```

---

### Task 7: Run full test suite and verify

**Files:** None

- [ ] **Step 1: Run all backend tests**

Run: `python -m pytest backend/tests/ -v 2>&1 | tail -5` (from `/home/neo/Projects/Musync`)
Expected: 95 passed

- [ ] **Step 2: Run all frontend tests**

Run: `npx vitest run 2>&1 | tail -8` (from `/home/neo/Projects/Musync/frontend`)
Expected: 44 tests passed

- [ ] **Step 3: Final commit if needed**

```bash
git add -A && git commit -m "chore: full test suite passing after live sync display"
```
