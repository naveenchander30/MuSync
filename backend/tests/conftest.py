import pytest
import os
import tempfile
from backend.app import create_app
from backend.database import db


@pytest.fixture
def app():
    """Create and configure a test Flask app with SQLite"""
    db_fd, db_path = tempfile.mkstemp()
    
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['MASTER_PASSWORD'] = 'test_password'
    os.environ['SPOTIFY_CLIENT_ID'] = 'test_client_id'
    os.environ['SPOTIFY_CLIENT_SECRET'] = 'test_client_secret'
    os.environ['GOOGLE_OAUTH_CLIENT_ID'] = 'test_google_id'
    os.environ['GOOGLE_OAUTH_CLIENT_SECRET'] = 'test_google_secret'
    
    app = create_app()
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def default_user(app):
    """Create a default user for testing"""
    from backend.database.models import User
    
    with app.app_context():
        user = User(id='test_user', username='test_user')
        db.session.add(user)
        db.session.commit()
        return user
