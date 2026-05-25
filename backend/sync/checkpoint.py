from backend.database import db, SyncJob
import json


class CheckpointManager:
    """Handle sync job checkpoints for resuming failed syncs"""
    
    @staticmethod
    def save_checkpoint(job_id: str, checkpoint_data: dict):
        """Save checkpoint data to database"""
        job = SyncJob.query.get(job_id)
        if job:
            job.checkpoint_data = checkpoint_data
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def load_checkpoint(job_id: str) -> dict:
        """Load checkpoint data from database"""
        job = SyncJob.query.get(job_id)
        if job:
            return job.checkpoint_data or {}
        return {}
    
    @staticmethod
    def clear_checkpoint(job_id: str):
        """Clear checkpoint data after successful sync"""
        job = SyncJob.query.get(job_id)
        if job:
            job.checkpoint_data = {}
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def create_checkpoint_from_job(job: SyncJob) -> dict:
        """Create checkpoint data from current job state"""
        return {
            "total_playlists": job.total_playlists,
            "total_tracks": job.total_tracks,
            "added_tracks": job.added_tracks,
            "failed_tracks": job.failed_tracks,
            "progress_percentage": job.progress_percentage,
        }
