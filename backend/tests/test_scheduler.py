import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from backend.database import db
from backend.database.models import ScheduledJob
from backend.scheduler.manager import SchedulerManager


class TestSchedulerManager:
    """Test SchedulerManager"""

    def test_initialization(self, app):
        with app.app_context():
            manager = SchedulerManager()
            assert manager.scheduler is not None
            manager.shutdown()

    def test_add_job(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='Test Job',
                source_service='spotify',
                target_service='ytmusic',
                interval_minutes=60
            )

            assert job.name == 'Test Job'
            assert job.source_service == 'spotify'
            assert job.target_service == 'ytmusic'
            assert job.schedule_interval_minutes == 60
            assert job.enabled is True
            assert job.job_id.startswith('job_')

            db_job = db.session.get(ScheduledJob, job.id)
            assert db_job is not None
            assert db_job.name == 'Test Job'

            manager.shutdown()

    def test_get_user_jobs(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            manager.add_job(
                user_id='test_user',
                name='Job 1',
                source_service='spotify',
                target_service='ytmusic'
            )
            manager.add_job(
                user_id='test_user',
                name='Job 2',
                source_service='ytmusic',
                target_service='spotify'
            )

            jobs = manager.get_user_jobs('test_user')
            assert len(jobs) == 2

            other_jobs = manager.get_user_jobs('other_user')
            assert len(other_jobs) == 0

            manager.shutdown()

    def test_delete_job(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='To Delete',
                source_service='spotify',
                target_service='ytmusic'
            )
            job_id = job.id

            result = manager.delete_job(job_id)
            assert result is True

            deleted = db.session.get(ScheduledJob, job_id)
            assert deleted is None

            result = manager.delete_job('nonexistent')
            assert result is False

            manager.shutdown()

    def test_update_job_enable_disable(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='Toggle Job',
                source_service='spotify',
                target_service='ytmusic'
            )

            updated = manager.update_job(job.id, enabled=False)
            assert updated.enabled is False

            updated = manager.update_job(job.id, enabled=True)
            assert updated.enabled is True

            manager.shutdown()

    def test_update_job_interval(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='Interval Job',
                source_service='spotify',
                target_service='ytmusic',
                interval_minutes=60
            )

            updated = manager.update_job(job.id, interval_minutes=120)
            assert updated.schedule_interval_minutes == 120

            manager.shutdown()

    def test_update_nonexistent_job(self, app):
        with app.app_context():
            manager = SchedulerManager()
            result = manager.update_job('nonexistent', enabled=False)
            assert result is None
            manager.shutdown()

    @patch('backend.scheduler.manager.SyncOrchestrator')
    def test_run_sync_job_spotify(self, mock_orch, app, default_user):
        with app.app_context():
            mock_orch_instance = MagicMock()
            mock_orch.return_value = mock_orch_instance

            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='Auto Sync',
                source_service='spotify',
                target_service='ytmusic'
            )
            job.last_run = None
            db.session.commit()

            manager._run_sync_job(job.id)

            db.session.refresh(job)
            assert job.last_run is not None
            mock_orch_instance.sync_spotify_to_ytmusic.assert_called_once()

            manager.shutdown()

    @patch('backend.scheduler.manager.SyncOrchestrator')
    def test_run_sync_job_ytmusic(self, mock_orch, app, default_user):
        with app.app_context():
            mock_orch_instance = MagicMock()
            mock_orch.return_value = mock_orch_instance

            manager = SchedulerManager()
            job = manager.add_job(
                user_id='test_user',
                name='Auto Sync YT',
                source_service='ytmusic',
                target_service='spotify'
            )

            manager._run_sync_job(job.id)

            mock_orch_instance.sync_ytmusic_to_spotify.assert_called_once()

            manager.shutdown()

    def test_run_sync_job_nonexistent(self, app):
        with app.app_context():
            manager = SchedulerManager()
            manager._run_sync_job('nonexistent')
            manager.shutdown()

    def test_initialize_jobs(self, app, default_user):
        with app.app_context():
            manager = SchedulerManager()
            manager.add_job(
                user_id='test_user',
                name='Init Job',
                source_service='spotify',
                target_service='ytmusic'
            )
            manager.shutdown()

            new_manager = SchedulerManager()
            new_manager.initialize_jobs()
            jobs = new_manager.get_user_jobs('test_user')
            assert len(jobs) >= 1
            new_manager.shutdown()

    def test_shutdown_cleanup(self, app):
        with app.app_context():
            manager = SchedulerManager()
            manager.shutdown()
            assert manager.scheduler.running is False

    def test_shutdown_twice(self, app):
        with app.app_context():
            manager = SchedulerManager()
            manager.shutdown()
            manager.shutdown()
