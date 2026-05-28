from flask import Blueprint, request, jsonify
import threading
from datetime import datetime, timezone

from backend.database import db, User, SyncJob, ActivityLog
from backend.sync.orchestrator import SyncOrchestrator
from backend.auth.token_manager import TokenManager
from backend.scheduler.manager import SchedulerManager

api_bp = Blueprint('api', __name__, url_prefix='/api')


# Global scheduler instance
scheduler_manager = SchedulerManager()


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok", "service": "MuSync 2.0"})


@api_bp.route('/auth/status', methods=['GET'])
def auth_status():
    """Get authentication status"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    spotify_valid = TokenManager.is_token_valid(user_id, 'spotify')
    ytmusic_valid = TokenManager.is_token_valid(user_id, 'ytmusic')
    
    return jsonify({
        "user_id": user_id,
        "spotify": spotify_valid,
        "ytmusic": ytmusic_valid
    })


@api_bp.route('/sync/spotify-to-ytmusic', methods=['POST'])
def sync_spotify_to_ytmusic():
    """Start Spotify → YouTube Music sync"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    # Create sync job
    job = SyncJob(
        user_id=user_id,
        job_type='sync',
        source_service='spotify',
        target_service='ytmusic',
        status='pending',
        started_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.session.add(job)
    db.session.commit()
    
    # Start sync in background thread
    orchestrator = SyncOrchestrator(user_id)
    thread = threading.Thread(
        target=orchestrator.sync_spotify_to_ytmusic,
        kwargs={'job_id': job.id}
    )
    thread.start()
    
    return jsonify({
        "job_id": job.id,
        "status": "started",
        "message": "Sync started in background"
    })


@api_bp.route('/sync/ytmusic-to-spotify', methods=['POST'])
def sync_ytmusic_to_spotify():
    """Start YouTube Music → Spotify sync"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    job = SyncJob(
        user_id=user_id,
        job_type='sync',
        source_service='ytmusic',
        target_service='spotify',
        status='pending',
        started_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.session.add(job)
    db.session.commit()
    
    orchestrator = SyncOrchestrator(user_id)
    thread = threading.Thread(
        target=orchestrator.sync_ytmusic_to_spotify,
        kwargs={'job_id': job.id}
    )
    thread.start()
    
    return jsonify({
        "job_id": job.id,
        "status": "started",
        "message": "Sync started in background"
    })


@api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get sync job status"""
    job = db.session.get(SyncJob, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "id": job.id,
        "status": job.status,
        "job_type": job.job_type,
        "source_service": job.source_service,
        "target_service": job.target_service,
        "progress_percentage": job.progress_percentage,
        "total_playlists": job.total_playlists,
        "total_tracks": job.total_tracks,
        "added_tracks": job.added_tracks,
        "failed_tracks": job.failed_tracks,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "current_playlist_name": job.current_playlist_name,
        "current_track_name": job.current_track_name,
        "current_track_artist": job.current_track_artist,
        "current_track_image_url": job.current_track_image_url,
    })


@api_bp.route('/jobs/user/<user_id>', methods=['GET'])
def get_user_jobs(user_id):
    """Get all sync jobs for a user"""
    jobs = SyncJob.query.filter_by(user_id=user_id).order_by(
        SyncJob.created_at.desc()
    ).limit(50).all()
    
    return jsonify([{
        "id": job.id,
        "status": job.status,
        "job_type": job.job_type,
        "source_service": job.source_service,
        "target_service": job.target_service,
        "progress_percentage": job.progress_percentage,
        "added_tracks": job.added_tracks,
        "failed_tracks": job.failed_tracks,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None
    } for job in jobs])


@api_bp.route('/scheduler/create', methods=['POST'])
def create_scheduled_job():
    """Create a scheduled sync job"""
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    source = data.get('source_service')
    target = data.get('target_service')
    interval = data.get('interval_minutes', 60)
    
    if not all([user_id, name, source, target]):
        return jsonify({"error": "Missing required fields"}), 400
    
    scheduled_job = scheduler_manager.add_job(
        user_id=user_id,
        name=name,
        source_service=source,
        target_service=target,
        interval_minutes=interval
    )
    
    return jsonify({
        "job_id": scheduled_job.id,
        "name": scheduled_job.name,
        "interval_minutes": scheduled_job.schedule_interval_minutes,
        "enabled": scheduled_job.enabled,
        "next_run": scheduled_job.next_run.isoformat() if scheduled_job.next_run else None
    })


@api_bp.route('/scheduler/jobs/<user_id>', methods=['GET'])
def get_scheduled_jobs(user_id):
    """Get all scheduled jobs for a user"""
    jobs = scheduler_manager.get_user_jobs(user_id)
    
    return jsonify([{
        "id": job.id,
        "name": job.name,
        "source_service": job.source_service,
        "target_service": job.target_service,
        "interval_minutes": job.schedule_interval_minutes,
        "enabled": job.enabled,
        "last_run": job.last_run.isoformat() if job.last_run else None,
        "next_run": job.next_run.isoformat() if job.next_run else None
    } for job in jobs])


@api_bp.route('/scheduler/jobs/<job_id>', methods=['PUT'])
def update_scheduled_job(job_id):
    """Update a scheduled job"""
    data = request.get_json()
    enabled = data.get('enabled')
    interval = data.get('interval_minutes')
    
    updated_job = scheduler_manager.update_job(
        job_id=job_id,
        enabled=enabled,
        interval_minutes=interval
    )
    
    if not updated_job:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({
        "id": updated_job.id,
        "enabled": updated_job.enabled,
        "interval_minutes": updated_job.schedule_interval_minutes
    })


@api_bp.route('/scheduler/jobs/<job_id>', methods=['DELETE'])
def delete_scheduled_job(job_id):
    """Delete a scheduled job"""
    success = scheduler_manager.delete_job(job_id)
    
    if not success:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify({"message": "Job deleted"})
