import pytest
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from backend.database import db
from backend.database.models import SyncJob, FailedTrack
from backend.sync.orchestrator import SyncOrchestrator


class TestSyncOrchestrator:
    """Test SyncOrchestrator with mocked API clients"""

    def test_initialization(self, app, default_user):
        with app.app_context():
            orch = SyncOrchestrator('test_user')
            assert orch.user_id == 'test_user'
            assert orch.sync_logs == []
            assert orch.is_running is False

    def test_log_adds_entry(self, app, default_user):
        with app.app_context():
            orch = SyncOrchestrator('test_user')
            orch.log("Test message")
            assert len(orch.sync_logs) == 1
            assert orch.sync_logs[0]['message'] == "Test message"
            assert orch.sync_logs[0]['level'] == "INFO"

    def test_log_adds_entry_with_level(self, app, default_user):
        with app.app_context():
            orch = SyncOrchestrator('test_user')
            orch.log("Warning message", "WARNING")
            assert orch.sync_logs[0]['level'] == "WARNING"

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_sync_spotify_to_ytmusic_success(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_spotify_instance.get_playlists.return_value = [
                {'id': 'pl1', 'name': 'Test Playlist', 'description': 'A test'}
            ]
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
            mock_ytmusic_instance.get_playlists.return_value = []
            mock_ytmusic_instance.create_playlist.return_value = {
                'playlistId': 'yt_pl1'
            }
            mock_ytmusic_instance.search.return_value = [
                {
                    'videoId': 'vid1',
                    'title': 'Song 1',
                    'artists': [{'name': 'Artist 1'}],
                    'videoType': 'MUSIC_VIDEO_TYPE_ATV',
                    'durationMs': '200000'
                }
            ]

            orch = SyncOrchestrator('test_user')
            orch.sync_spotify_to_ytmusic()

            mock_spotify_instance.get_playlists.assert_called_once()
            mock_spotify_instance.get_playlist_tracks.assert_called_once_with('pl1')
            mock_ytmusic_instance.create_playlist.assert_called_once()
            mock_ytmusic_instance.add_playlist_items.assert_called_once()

            jobs = SyncJob.query.filter_by(user_id='test_user').all()
            assert len(jobs) > 0
            latest_job = jobs[-1]
            assert latest_job.status == 'success'
            assert latest_job.added_tracks == 1
            assert latest_job.failed_tracks == 0
            assert latest_job.current_playlist_name == 'Test Playlist'
            assert latest_job.current_track_name == 'Song 1'
            assert latest_job.current_track_artist == 'Artist 1'
            assert latest_job.current_track_image_url == 'https://example.com/art.jpg'

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_sync_spotify_to_ytmusic_with_existing_playlist(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_spotify_instance.get_playlists.return_value = [
                {'id': 'pl1', 'name': 'Existing Playlist'}
            ]
            mock_spotify_instance.get_playlist_tracks.return_value = [
                {
                    'track': {
                        'name': 'Song 1',
                        'artists': [{'name': 'Artist 1'}],
                        'duration_ms': 200000
                    }
                }
            ]
            mock_ytmusic_instance.get_playlists.return_value = [
                {'playlistId': 'yt_existing', 'title': 'Existing Playlist'}
            ]
            mock_ytmusic_instance.search.return_value = [
                {
                    'videoId': 'vid1',
                    'title': 'Song 1',
                    'artists': [{'name': 'Artist 1'}],
                    'videoType': 'MUSIC_VIDEO_TYPE_ATV'
                }
            ]

            orch = SyncOrchestrator('test_user')
            orch.sync_spotify_to_ytmusic()

            mock_ytmusic_instance.create_playlist.assert_not_called()
            mock_ytmusic_instance.add_playlist_items.assert_called_once()

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_sync_spotify_to_ytmusic_no_match(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_spotify_instance.get_playlists.return_value = [
                {'id': 'pl1', 'name': 'Test Playlist'}
            ]
            mock_spotify_instance.get_playlist_tracks.return_value = [
                {
                    'track': {
                        'name': 'Obscure Song',
                        'artists': [{'name': 'Unknown Artist'}],
                        'duration_ms': 200000
                    }
                }
            ]
            mock_ytmusic_instance.get_playlists.return_value = []
            mock_ytmusic_instance.create_playlist.return_value = {
                'playlistId': 'yt_pl1'
            }
            mock_ytmusic_instance.search.return_value = []

            orch = SyncOrchestrator('test_user')
            orch.sync_spotify_to_ytmusic()

            jobs = SyncJob.query.filter_by(user_id='test_user').all()
            latest_job = jobs[-1]
            assert latest_job.status == 'success'
            assert latest_job.added_tracks == 0
            assert latest_job.failed_tracks == 1

            failed = FailedTrack.query.filter_by(sync_job_id=latest_job.id).first()
            assert failed is not None
            assert failed.track_name == 'Obscure Song'

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_sync_spotify_to_ytmusic_api_error(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_spotify_instance.get_playlists.side_effect = Exception(
                "API rate limit exceeded"
            )

            orch = SyncOrchestrator('test_user')
            orch.sync_spotify_to_ytmusic()

            jobs = SyncJob.query.filter_by(user_id='test_user').all()
            latest_job = jobs[-1]
            assert latest_job.status == 'failed'
            assert 'API rate limit' in latest_job.error_message

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_sync_ytmusic_to_spotify_success(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_ytmusic_instance.get_playlists.return_value = [
                {
                    'playlistId': 'yt_pl1',
                    'title': 'YT Playlist',
                    'description': 'From YouTube'
                }
            ]
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
            mock_spotify_instance.get_playlists.return_value = []
            mock_spotify_instance.create_playlist.return_value = {
                'id': 'sp_pl1'
            }
            mock_spotify_instance.search_track.return_value = {
                'tracks': {
                    'items': [
                        {
                            'uri': 'spotify:track:abc123',
                            'name': 'Song 1',
                            'artists': [{'name': 'Artist 1'}]
                        }
                    ]
                }
            }

            orch = SyncOrchestrator('test_user')
            orch.sync_ytmusic_to_spotify()

            mock_ytmusic_instance.get_playlists.assert_called_once()
            mock_spotify_instance.create_playlist.assert_called_once()
            mock_spotify_instance.add_tracks_to_playlist.assert_called_once()

            jobs = SyncJob.query.filter_by(user_id='test_user').all()
            latest_job = jobs[-1]
            assert latest_job.status == 'success'
            assert latest_job.current_playlist_name == 'YT Playlist'
            assert latest_job.current_track_name == 'Song 1'
            assert latest_job.current_track_artist == 'Artist 1'
            assert latest_job.current_track_image_url == 'https://example.com/yt_thumb.jpg'

    @patch('backend.sync.orchestrator.SpotifyClient')
    @patch('backend.sync.orchestrator.YTMusicClient')
    def test_resume_from_checkpoint(
        self, mock_ytmusic, mock_spotify, app, default_user
    ):
        with app.app_context():
            mock_spotify_instance = MagicMock()
            mock_ytmusic_instance = MagicMock()
            mock_spotify.return_value = mock_spotify_instance
            mock_ytmusic.return_value = mock_ytmusic_instance

            mock_spotify_instance.get_playlists.return_value = [
                {'id': 'pl1', 'name': 'First'},
                {'id': 'pl2', 'name': 'Second'},
            ]
            mock_spotify_instance.get_playlist_tracks.return_value = []
            mock_ytmusic_instance.get_playlists.return_value = []
            mock_ytmusic_instance.create_playlist.return_value = {
                'playlistId': 'yt_pl'
            }

            job = SyncJob(
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic',
                status='pending'
            )
            db.session.add(job)
            db.session.commit()

            orch = SyncOrchestrator('test_user')
            orch.sync_spotify_to_ytmusic(
                job_id=job.id,
                resume_from={'playlist_index': 1}
            )

            assert mock_ytmusic_instance.create_playlist.call_count == 1
            job_refreshed = db.session.get(SyncJob, job.id)
            assert job_refreshed.status == 'success'

    def test_thread_safety(self, app, default_user):
        with app.app_context():
            orch = SyncOrchestrator('test_user')

            def add_log():
                for _ in range(100):
                    orch.log("Concurrent message")

            threads = [
                threading.Thread(target=add_log) for _ in range(5)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(orch.sync_logs) == 500
