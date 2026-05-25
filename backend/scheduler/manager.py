from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from backend.database import db, ScheduledJob, SyncJob
from backend.sync.orchestrator import SyncOrchestrator


class SchedulerManager:
    """Manage scheduled sync jobs using APScheduler"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    
    def initialize_jobs(self):
        """Load and schedule all enabled jobs from database"""
        enabled_jobs = ScheduledJob.query.filter_by(enabled=True).all()
        
        for scheduled_job in enabled_jobs:
            self._schedule_job(scheduled_job)
    
    def _schedule_job(self, scheduled_job: ScheduledJob):
        """Schedule a single job"""
        trigger = IntervalTrigger(minutes=scheduled_job.schedule_interval_minutes)
        
        self.scheduler.add_job(
            func=self._run_sync_job,
            trigger=trigger,
            id=scheduled_job.job_id,
            args=[scheduled_job.id],
            replace_existing=True,
            next_run_time=datetime.utcnow() + timedelta(minutes=scheduled_job.schedule_interval_minutes)
        )
        
        # Update next_run in database
        scheduled_job.next_run = datetime.utcnow() + timedelta(minutes=scheduled_job.schedule_interval_minutes)
        db.session.commit()
    
    def _run_sync_job(self, scheduled_job_id: str):
        """Execute a scheduled sync job"""
        scheduled_job = ScheduledJob.query.get(scheduled_job_id)
        if not scheduled_job:
            return
        
        # Update last_run
        scheduled_job.last_run = datetime.utcnow()
        scheduled_job.next_run = datetime.utcnow() + timedelta(minutes=scheduled_job.schedule_interval_minutes)
        db.session.commit()
        
        # Create sync job
        sync_job = SyncJob(
            user_id=scheduled_job.user_id,
            job_type='scheduled_sync',
            source_service=scheduled_job.source_service,
            target_service=scheduled_job.target_service,
            status='running',
            started_at=datetime.utcnow()
        )
        db.session.add(sync_job)
        db.session.commit()
        
        # Run sync
        orchestrator = SyncOrchestrator(scheduled_job.user_id)
        
        if scheduled_job.source_service == 'spotify':
            orchestrator.sync_spotify_to_ytmusic(job_id=sync_job.id)
        else:
            orchestrator.sync_ytmusic_to_spotify(job_id=sync_job.id)
    
    def add_job(self, user_id: str, name: str, source_service: str,
                target_service: str, interval_minutes: int = 60) -> ScheduledJob:
        """Add a new scheduled job"""
        import uuid
        
        scheduled_job = ScheduledJob(
            user_id=user_id,
            job_id=f"job_{uuid.uuid4().hex[:12]}",
            name=name,
            source_service=source_service,
            target_service=target_service,
            schedule_interval_minutes=interval_minutes,
            enabled=True
        )
        
        db.session.add(scheduled_job)
        db.session.commit()
        
        # Schedule in APScheduler
        self._schedule_job(scheduled_job)
        
        return scheduled_job
    
    def update_job(self, job_id: str, enabled: bool = None, interval_minutes: int = None):
        """Update an existing scheduled job"""
        scheduled_job = ScheduledJob.query.get(job_id)
        if not scheduled_job:
            return None
        
        if enabled is not None:
            scheduled_job.enabled = enabled
            
            if enabled:
                # Re-enable: schedule the job
                self._schedule_job(scheduled_job)
            else:
                # Disable: remove from scheduler
                self.scheduler.remove_job(scheduled_job.job_id)
        
        if interval_minutes is not None:
            scheduled_job.schedule_interval_minutes = interval_minutes
            
            # Reschedule with new interval
            if scheduled_job.enabled:
                self.scheduler.reschedule_job(
                    scheduled_job.job_id,
                    trigger=IntervalTrigger(minutes=interval_minutes)
                )
        
        db.session.commit()
        return scheduled_job
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a scheduled job"""
        scheduled_job = ScheduledJob.query.get(job_id)
        if not scheduled_job:
            return False
        
        # Remove from APScheduler
        try:
            self.scheduler.remove_job(scheduled_job.job_id)
        except:
            pass
        
        # Remove from database
        db.session.delete(scheduled_job)
        db.session.commit()
        
        return True
    
    def get_user_jobs(self, user_id: str):
        """Get all scheduled jobs for a user"""
        return ScheduledJob.query.filter_by(user_id=user_id).all()
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
        except Exception:
            pass
