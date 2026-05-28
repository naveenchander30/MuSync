import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_health_returns_ok_status(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'MuSync 2.0'


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_auth_status_requires_user_id(self, client):
        response = client.get('/api/auth/status')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_auth_status_returns_correct_format(self, client):
        response = client.get('/api/auth/status?user_id=test_user')
        assert response.status_code == 200
        data = response.get_json()
        assert 'spotify' in data
        assert 'ytmusic' in data
        assert data['spotify'] == False
        assert data['ytmusic'] == False
    
    def test_spotify_login_requires_user_id(self, client):
        response = client.get('/auth/spotify/login')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_ytmusic_login_requires_user_id(self, client):
        response = client.get('/auth/ytmusic/login')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestSyncEndpoints:
    """Test sync endpoints"""
    
    def test_sync_spotify_to_ytmusic_requires_user_id(self, client):
        response = client.post('/api/sync/spotify-to-ytmusic', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_sync_ytmusic_to_spotify_requires_user_id(self, client):
        response = client.post('/api/sync/ytmusic-to-spotify', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestJobEndpoints:
    """Test job management endpoints"""
    
    def test_get_nonexistent_job_returns_404(self, client):
        response = client.get('/api/jobs/nonexistent_id')
        assert response.status_code == 404
    
    def test_get_job_returns_live_sync_fields(self, client, app):
        from backend.database import db
        from backend.database.models import SyncJob
        import uuid

        with app.app_context():
            job = SyncJob(
                id=str(uuid.uuid4()),
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic',
                status='running',
                current_playlist_name='Test Playlist',
                current_track_name='Test Track',
                current_track_artist='Test Artist',
                current_track_image_url='https://example.com/art.jpg',
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        response = client.get(f'/api/jobs/{job_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['current_playlist_name'] == 'Test Playlist'
        assert data['current_track_name'] == 'Test Track'
        assert data['current_track_artist'] == 'Test Artist'
        assert data['current_track_image_url'] == 'https://example.com/art.jpg'

    def test_get_job_returns_null_live_fields_when_not_set(self, client, app):
        from backend.database import db
        from backend.database.models import SyncJob
        import uuid

        with app.app_context():
            job = SyncJob(
                id=str(uuid.uuid4()),
                user_id='test_user',
                job_type='sync',
                source_service='spotify',
                target_service='ytmusic',
                status='pending',
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id

        response = client.get(f'/api/jobs/{job_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['current_playlist_name'] is None
        assert data['current_track_name'] is None
        assert data['current_track_artist'] is None
        assert data['current_track_image_url'] is None

    def test_get_user_jobs_returns_empty_list(self, client):
        response = client.get('/api/jobs/user/test_user')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestSchedulerEndpoints:
    """Test scheduler endpoints"""
    
    def test_create_job_requires_fields(self, client):
        response = client.post('/api/scheduler/create', json={})
        assert response.status_code == 400
    
    def test_get_scheduled_jobs_returns_list(self, client):
        response = client.get('/api/scheduler/jobs/test_user')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
