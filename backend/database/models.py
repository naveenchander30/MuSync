from .connection import db
from datetime import datetime, timezone
import uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.utcnow)
    
    credentials = db.relationship('Credential', backref='user', cascade='all, delete-orphan')
    sync_jobs = db.relationship('SyncJob', backref='user', cascade='all, delete-orphan')
    scheduled_jobs = db.relationship('ScheduledJob', backref='user', cascade='all, delete-orphan')
    playlist_snapshots = db.relationship('PlaylistSnapshot', backref='user', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', cascade='all, delete-orphan')


class Credential(db.Model):
    __tablename__ = 'credentials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    refresh_token_encrypted = db.Column(db.Text, nullable=False)
    access_token_expiry = db.Column(db.DateTime)
    scope = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.utcnow)
    last_refreshed_at = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'service', name='uq_user_service'),
    )


class SyncJob(db.Model):
    __tablename__ = 'sync_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    source_service = db.Column(db.String(50), nullable=False)
    target_service = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = db.Column(db.DateTime)
    total_playlists = db.Column(db.Integer, default=0)
    total_tracks = db.Column(db.Integer, default=0)
    added_tracks = db.Column(db.Integer, default=0)
    failed_tracks = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    progress_percentage = db.Column(db.Integer, default=0)
    current_playlist_name = db.Column(db.String(255), nullable=True)
    current_track_name = db.Column(db.String(255), nullable=True)
    current_track_artist = db.Column(db.String(255), nullable=True)
    current_track_image_url = db.Column(db.Text, nullable=True)
    checkpoint_data = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    failed_track_records = db.relationship('FailedTrack', backref='sync_job', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='sync_job')


class FailedTrack(db.Model):
    __tablename__ = 'failed_tracks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sync_job_id = db.Column(db.String(36), db.ForeignKey('sync_jobs.id'), nullable=False)
    track_name = db.Column(db.String(255), nullable=False)
    artist_names = db.Column(db.Text, nullable=False)
    reason = db.Column(db.String(255))
    attempt_count = db.Column(db.Integer, default=1)
    last_attempted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class PlaylistSnapshot(db.Model):
    __tablename__ = 'playlist_snapshots'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    playlist_id = db.Column(db.String(255), nullable=False)
    playlist_name = db.Column(db.String(255), nullable=False)
    tracks = db.Column(db.JSON, default=list)
    synced_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'service', 'playlist_id', name='uq_user_service_playlist'),
    )


class ScheduledJob(db.Model):
    __tablename__ = 'scheduled_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    source_service = db.Column(db.String(50), nullable=False)
    target_service = db.Column(db.String(50), nullable=False)
    sync_direction = db.Column(db.String(50))
    schedule_interval_minutes = db.Column(db.Integer, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    __table_args__ = (
        db.Index('idx_user_created_at', 'user_id', 'created_at'),
        db.Index('idx_sync_job', 'sync_job_id'),
    )
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    sync_job_id = db.Column(db.String(36), db.ForeignKey('sync_jobs.id'))
    log_level = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
