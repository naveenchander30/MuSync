import threading
import time
from datetime import datetime
from backend.database import db, SyncJob, FailedTrack, PlaylistSnapshot
from backend.sync.spotify_client import SpotifyClient
from backend.sync.ytmusic_client import YTMusicClient
from backend.sync.matcher import find_best_match
from backend.sync.checkpoint import CheckpointManager


class SyncOrchestrator:
    """Orchestrate sync operations between Spotify and YouTube Music"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.spotify = SpotifyClient(user_id)
        self.ytmusic = YTMusicClient(user_id)
        self.sync_logs = []
        self.is_running = False
        self.lock = threading.Lock()
    
    def log(self, message: str, level: str = "INFO"):
        """Add log message"""
        timestamp = datetime.utcnow().strftime('%H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        
        with self.lock:
            self.sync_logs.append(log_entry)
    
    def sync_spotify_to_ytmusic(self, job_id: str = None, resume_from: dict = None):
        """Sync Spotify playlists to YouTube Music"""
        self.is_running = True
        self.log("Starting Spotify → YouTube Music sync")
        
        try:
            # Get or create sync job
            if job_id:
                job = SyncJob.query.get(job_id)
            else:
                job = SyncJob(
                    user_id=self.user_id,
                    job_type='sync',
                    source_service='spotify',
                    target_service='ytmusic',
                    status='running',
                    started_at=datetime.utcnow()
                )
                db.session.add(job)
                db.session.commit()
                job_id = job.id
            
            # Check for checkpoint
            checkpoint = resume_from or CheckpointManager.load_checkpoint(job_id)
            start_playlist_index = checkpoint.get('playlist_index', 0)
            
            # Get Spotify playlists
            self.log("Fetching Spotify playlists")
            playlists = self.spotify.get_playlists()
            job.total_playlists = len(playlists)
            db.session.commit()
            
            for playlist_idx, playlist in enumerate(playlists):
                if playlist_idx < start_playlist_index:
                    continue  # Skip already processed playlists
                
                self.log(f"Processing playlist: {playlist['name']}")
                job.progress_percentage = int((playlist_idx / len(playlists)) * 100)
                db.session.commit()
                
                # Get tracks from Spotify playlist
                spotify_tracks = self.spotify.get_playlist_tracks(playlist['id'])
                job.total_tracks += len(spotify_tracks)
                
                # Check if playlist already exists in YouTube Music
                ytmusic_playlists = self.ytmusic.get_playlists()
                existing_playlist = None
                
                for yt_pl in ytmusic_playlists:
                    if yt_pl.get('title') == playlist['name']:
                        existing_playlist = yt_pl
                        break
                
                # Create or use existing playlist
                if not existing_playlist:
                    self.log(f"Creating YouTube Music playlist: {playlist['name']}")
                    new_playlist = self.ytmusic.create_playlist(
                        title=playlist['name'],
                        description=playlist.get('description', '')
                    )
                    playlist_id = new_playlist.get('playlistId')
                else:
                    playlist_id = existing_playlist.get('playlistId')
                    self.log(f"Using existing YouTube Music playlist: {playlist['name']}")
                
                # Process tracks in batches
                video_ids_to_add = []
                
                for track_data in spotify_tracks:
                    track = track_data.get('track', {})
                    if not track:
                        continue
                    
                    # Extract track info
                    query_track = {
                        'name': track.get('name', ''),
                        'artists': [a.get('name', '') for a in track.get('artists', [])],
                        'duration_ms': track.get('duration_ms', 0)
                    }
                    
                    # Search on YouTube Music
                    try:
                        search_results = self.ytmusic.search(
                            f"{query_track['name']} {' '.join(query_track['artists'])}",
                            limit=5
                        )
                        
                        # Filter to video results
                        video_results = [
                            r for r in search_results
                            if r.get('videoType') == 'MUSIC_VIDEO_TYPE_ATV' or r.get('videoId')
                        ]
                        
                        # Find best match
                        best_match = find_best_match(
                            query_track,
                            video_results,
                            threshold=0.90
                        )
                        
                        if best_match:
                            video_id = best_match.get('videoId')
                            if video_id and video_id not in video_ids_to_add:
                                video_ids_to_add.append(video_id)
                                job.added_tracks += 1
                                self.log(f"Matched: {query_track['name']}")
                        else:
                            # Track not found
                            failed_track = FailedTrack(
                                sync_job_id=job_id,
                                track_name=query_track['name'],
                                artist_names=", ".join(query_track['artists']),
                                reason="No match found"
                            )
                            db.session.add(failed_track)
                            job.failed_tracks += 1
                            self.log(f"Not found: {query_track['name']}", "WARNING")
                    
                    except Exception as e:
                        failed_track = FailedTrack(
                            sync_job_id=job_id,
                            track_name=query_track['name'],
                            artist_names=", ".join(query_track['artists']),
                            reason=str(e)
                        )
                        db.session.add(failed_track)
                        job.failed_tracks += 1
                        self.log(f"Error processing track: {query_track['name']}", "ERROR")
                    
                    # Add in batches of 20
                    if len(video_ids_to_add) >= 20:
                        self.ytmusic.add_playlist_items(playlist_id, video_ids_to_add[:20])
                        video_ids_to_add = video_ids_to_add[20:]
                        db.session.commit()
                
                # Add remaining tracks
                if video_ids_to_add:
                    self.ytmusic.add_playlist_items(playlist_id, video_ids_to_add)
                    db.session.commit()
                
                # Save checkpoint
                CheckpointManager.save_checkpoint(job_id, {
                    'playlist_index': playlist_idx + 1
                })
            
            # Complete job
            job.status = 'success'
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100
            db.session.commit()
            
            self.log(f"Sync complete: {job.added_tracks} added, {job.failed_tracks} failed")
            
        except Exception as e:
            self.log(f"Sync failed: {str(e)}", "ERROR")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
        
        finally:
            self.is_running = False
    
    def sync_ytmusic_to_spotify(self, job_id: str = None, resume_from: dict = None):
        """Sync YouTube Music playlists to Spotify (reverse direction)"""
        self.is_running = True
        self.log("Starting YouTube Music → Spotify sync")
        
        # Similar implementation to spotify_to_ytmusic but reversed
        # For brevity, implementing the skeleton
        try:
            if job_id:
                job = SyncJob.query.get(job_id)
            else:
                job = SyncJob(
                    user_id=self.user_id,
                    job_type='sync',
                    source_service='ytmusic',
                    target_service='spotify',
                    status='running',
                    started_at=datetime.utcnow()
                )
                db.session.add(job)
                db.session.commit()
                job_id = job.id
            
            # Get YouTube Music playlists
            self.log("Fetching YouTube Music playlists")
            playlists = self.ytmusic.get_playlists()
            job.total_playlists = len(playlists)
            db.session.commit()
            
            # Process each playlist
            for playlist_idx, playlist in enumerate(playlists):
                self.log(f"Processing playlist: {playlist.get('title', 'Unknown')}")
                job.progress_percentage = int((playlist_idx / len(playlists)) * 100)
                db.session.commit()
                
                # Get playlist details
                playlist_data = self.ytmusic.get_playlist(playlist.get('playlistId'))
                tracks = playlist_data.get('tracks', [])
                job.total_tracks += len(tracks)
                
                # Create or find Spotify playlist
                spotify_playlists = self.spotify.get_playlists()
                existing_playlist = None
                
                for sp_pl in spotify_playlists:
                    if sp_pl.get('name') == playlist.get('title'):
                        existing_playlist = sp_pl
                        break
                
                if not existing_playlist:
                    new_playlist = self.spotify.create_playlist(
                        name=playlist.get('title', 'Unknown'),
                        description=playlist.get('description', '')
                    )
                    playlist_id = new_playlist.get('id')
                else:
                    playlist_id = existing_playlist.get('id')
                
                # Process tracks
                track_uris_to_add = []
                
                for track_data in tracks:
                    query_track = {
                        'name': track_data.get('title', ''),
                        'artists': [a.get('name', '') for a in track_data.get('artists', [])],
                        'duration_ms': track_data.get('durationMs', track_data.get('duration_seconds', 0) * 1000)
                    }
                    
                    try:
                        search_results = self.spotify.search_track(
                            f"{query_track['name']} {' '.join(query_track['artists'])}",
                            limit=5
                        )
                        
                        tracks_list = search_results.get('tracks', {}).get('items', [])
                        
                        best_match = find_best_match(
                            query_track,
                            tracks_list,
                            threshold=0.90
                        )
                        
                        if best_match:
                            uri = best_match.get('uri')
                            if uri and uri not in track_uris_to_add:
                                track_uris_to_add.append(uri)
                                job.added_tracks += 1
                        else:
                            failed_track = FailedTrack(
                                sync_job_id=job_id,
                                track_name=query_track['name'],
                                artist_names=", ".join(query_track['artists']),
                                reason="No match found"
                            )
                            db.session.add(failed_track)
                            job.failed_tracks += 1
                    
                    except Exception as e:
                        failed_track = FailedTrack(
                            sync_job_id=job_id,
                            track_name=query_track['name'],
                            artist_names=", ".join(query_track['artists']),
                            reason=str(e)
                        )
                        db.session.add(failed_track)
                        job.failed_tracks += 1
                    
                    if len(track_uris_to_add) >= 20:
                        self.spotify.add_tracks_to_playlist(playlist_id, track_uris_to_add[:20])
                        track_uris_to_add = track_uris_to_add[20:]
                        db.session.commit()
                
                if track_uris_to_add:
                    self.spotify.add_tracks_to_playlist(playlist_id, track_uris_to_add)
                    db.session.commit()
            
            job.status = 'success'
            job.completed_at = datetime.utcnow()
            job.progress_percentage = 100
            db.session.commit()
            
            self.log(f"Sync complete: {job.added_tracks} added, {job.failed_tracks} failed")
            
        except Exception as e:
            self.log(f"Sync failed: {str(e)}", "ERROR")
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
        
        finally:
            self.is_running = False
