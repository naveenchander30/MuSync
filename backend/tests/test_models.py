import pytest
from backend.database import db
from backend.database.models import (
    User, Credential, SyncJob, FailedTrack,
    PlaylistSnapshot, ScheduledJob, ActivityLog
)
from datetime import datetime


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            assert user.id == 'test_user'
            assert user.username == 'testuser'
            assert user.created_at is not None
    
    def test_user_unique_username(self, app):
        with app.app_context():
            user1 = User(id='user1', username='same_username')
            user2 = User(id='user2', username='same_username')
            db.session.add(user1)
            db.session.commit()
            db.session.add(user2)
            
            with pytest.raises(Exception):
                db.session.commit()


class TestCredentialModel:
    """Test Credential model"""
    
    def test_create_credential(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            cred = Credential(
                user_id='test_user',
                service='spotify',
                refresh_token_encrypted='encrypted_token',
                access_token_expiry=datetime.utcnow()
            )
            db.session.add(cred)
            db.session.commit()
            
            assert cred.service == 'spotify'
            assert cred.refresh_token_encrypted == 'encrypted_token'
    
    def test_unique_user_service_constraint(self, app):
        with app.app_context():
            cred1 = Credential(
                user_id='test_user',
                service='spotify',
                refresh_token_encrypted='token1'
            )
            cred2 = Credential(
                user_id='test_user',
                service='spotify',
                refresh_token_encrypted='token2'
            )
            db.session.add(cred1)
            db.session.commit()
            db.session.add(cred2)
            
            with pytest.raises(Exception):
                db.session.commit()


class TestSyncJobModel:
    """Test SyncJob model"""
    
    def test_create_sync_job(self, app):
        with app.app_context():
            job = SyncJob(
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic',
                status='pending'
            )
            db.session.add(job)
            db.session.commit()
            
            assert job.status == 'pending'
            assert job.added_tracks == 0
            assert job.failed_tracks == 0
    
    def test_sync_job_defaults(self, app):
        with app.app_context():
            job = SyncJob(
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic'
            )
            db.session.add(job)
            db.session.commit()
            
            assert job.progress_percentage == 0
            assert job.total_playlists == 0
            assert job.total_tracks == 0
    
    def test_sync_job_status_transitions(self, app):
        with app.app_context():
            job = SyncJob(
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic',
                status='pending'
            )
            db.session.add(job)
            db.session.commit()
            
            job.status = 'running'
            db.session.commit()
            assert job.status == 'running'
            
            job.status = 'success'
            job.completed_at = datetime.utcnow()
            db.session.commit()
            assert job.status == 'success'


class TestFailedTrackModel:
    """Test FailedTrack model"""
    
    def test_create_failed_track(self, app):
        with app.app_context():
            job = SyncJob(
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic'
            )
            db.session.add(job)
            db.session.commit()
            
            failed = FailedTrack(
                sync_job_id=job.id,
                track_name='Test Song',
                artist_names='Test Artist',
                reason='No match found'
            )
            db.session.add(failed)
            db.session.commit()
            
            assert failed.track_name == 'Test Song'
            assert failed.attempt_count == 1


class TestPlaylistSnapshotModel:
    """Test PlaylistSnapshot model"""
    
    def test_create_playlist_snapshot(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            snapshot = PlaylistSnapshot(
                user_id='test_user',
                service='spotify',
                playlist_id='pl_123',
                playlist_name='My Playlist',
                tracks=[{'name': 'Song1', 'artist': 'Artist1'}]
            )
            db.session.add(snapshot)
            db.session.commit()
            
            assert snapshot.playlist_name == 'My Playlist'
            assert len(snapshot.tracks) == 1


class TestScheduledJobModel:
    """Test ScheduledJob model"""
    
    def test_create_scheduled_job(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            job = ScheduledJob(
                user_id='test_user',
                job_id='job_123',
                name='Daily Sync',
                source_service='spotify',
                target_service='ytmusic',
                schedule_interval_minutes=60
            )
            db.session.add(job)
            db.session.commit()
            
            assert job.enabled == True
            assert job.schedule_interval_minutes == 60


class TestActivityLogModel:
    """Test ActivityLog model"""
    
    def test_create_activity_log(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            log = ActivityLog(
                user_id='test_user',
                log_level='INFO',
                message='Test log message'
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.log_level == 'INFO'
            assert log.message == 'Test log message'
