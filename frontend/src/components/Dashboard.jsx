import { useState, useEffect } from 'react'
import { endpoints } from '../api'

function useDashboardData() {
  const [stats, setStats] = useState({ total: 0, success: 0, failed: 0, running: 0 })
  const [recentJobs, setRecentJobs] = useState([])
  const [activeJob, setActiveJob] = useState(null)
  const [imgError, setImgError] = useState(false)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  const loadData = async () => {
    try {
      const jobsRes = await endpoints.jobs.getByUser()
      const jobs = jobsRes.data
      const active = jobs.find(j => j.status === 'running' || j.status === 'pending')
      setActiveJob(active || null)
      setImgError(false)
      const filtered = filter === 'all' ? jobs : jobs.filter(j => j.status === filter)
      setRecentJobs(filtered.slice(0, 20))
      setStats({
        total: jobs.length,
        success: jobs.filter(j => j.status === 'success').length,
        failed: jobs.filter(j => j.status === 'failed').length,
        running: jobs.filter(j => j.status === 'running').length,
      })
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 3000)
    return () => clearInterval(interval)
  }, [filter])

  return { stats, recentJobs, activeJob, imgError, setImgError, filter, setFilter, loading }
}

const statusConfig = {
  success: { label: 'Success', dot: 'bg-success', text: 'text-success' },
  failed: { label: 'Failed', dot: 'bg-error', text: 'text-error' },
  running: { label: 'Syncing', dot: 'bg-primary', text: 'text-primary' },
  pending: { label: 'Pending', dot: 'bg-warning', text: 'text-warning' },
}

function formatDirection(source, target) {
  const s = source === 'spotify' ? 'Spotify' : 'YT Music'
  const t = target === 'spotify' ? 'Spotify' : 'YT Music'
  return `${s} → ${t}`
}

function formatTimeAgo(dateStr) {
  if (!dateStr) return 'N/A'
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

function ActiveJobBanner({ activeJob, imgError, setImgError }) {
  if (!activeJob) return null
  return (
    <div className="border border-outline-variant p-unit-4 mb-unit-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-unit-3">
          <div className="w-2 h-2 bg-primary" />
          <div>
            <div className="text-sm font-medium">Sync in Progress</div>
            <div className="text-xs text-on-surface-variant">{formatDirection(activeJob.source_service, activeJob.target_service)}</div>
          </div>
        </div>
        <div className="flex items-center gap-unit-6">
          <div className="text-right">
            <div className="text-label-xs text-on-surface-variant uppercase">Progress</div>
            <div className="text-sm font-bold">{activeJob.progress_percentage}%</div>
          </div>
          <div className="text-right">
            <div className="text-label-xs text-on-surface-variant uppercase">Tracks</div>
            <div className="text-sm font-bold text-success">+{activeJob.added_tracks || 0}</div>
          </div>
          <div className="w-48 h-[1px] bg-outline-variant relative">
            <div className="h-full bg-primary transition-all duration-500 absolute top-0 left-0" style={{ width: `${activeJob.progress_percentage}%` }} />
          </div>
        </div>
      </div>
      <div className="mt-unit-3 pt-unit-3 border-t border-outline-variant flex items-center gap-unit-3">
        {activeJob.current_track_image_url && !imgError ? (
          <img src={activeJob.current_track_image_url} alt="Album art" loading="lazy" onError={() => setImgError(true)} className="w-10 h-10 object-cover flex-shrink-0" />
        ) : (
          <div className="w-10 h-10 border border-outline-variant flex items-center justify-center flex-shrink-0">
            <span className="text-lg">♪</span>
          </div>
        )}
        <div className="min-w-0">
          {activeJob.current_playlist_name && (
            <div className="text-xs text-on-surface-variant truncate">Playlist: <span className="text-white">{activeJob.current_playlist_name}</span></div>
          )}
          {activeJob.current_track_name && (
            <div className="text-xs text-on-surface-variant truncate mt-[2px]">
              <span className="text-primary">→</span> Now: <span className="text-white font-medium">{activeJob.current_track_name}</span>
              {activeJob.current_track_artist && <span className="text-on-surface-variant"> — {activeJob.current_track_artist}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, accent }) {
  return (
    <div className="border border-outline-variant p-unit-4">
      <div className="text-label-sm text-on-surface-variant uppercase mb-unit-1">{label}</div>
      <div className={`text-headline-md ${accent || 'text-white'}`}>{value}</div>
    </div>
  )
}

export default function Dashboard() {
  const { stats, recentJobs, activeJob, imgError, setImgError, filter, setFilter, loading } = useDashboardData()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-6 h-6 border border-outline-variant border-t-primary mx-auto mb-unit-3" />
          <p className="text-sm text-on-surface-variant">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="px-unit-8 py-unit-6 border-b border-outline-variant">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-headline-md">Dashboard</h1>
          </div>
          <div className="flex items-center gap-unit-4">
            <button className="w-8 h-8 border border-outline-variant flex items-center justify-center hover:border-white/30 transition-colors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
            </button>
            <div className="w-8 h-8 border border-outline-variant flex items-center justify-center">
              <span className="text-xs font-medium">U</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-unit-8">
        <ActiveJobBanner activeJob={activeJob} imgError={imgError} setImgError={setImgError} />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-unit-4 mb-unit-8">
          <StatCard label="Total Syncs" value={stats.total} />
          <StatCard label="Successful" value={stats.success} accent="text-success" />
          <StatCard label="Failed" value={stats.failed} accent="text-error" />
          <StatCard label="Running" value={stats.running} accent="text-primary" />
        </div>

        <div className="border border-outline-variant">
          <div className="flex items-center justify-between px-unit-4 py-unit-3 border-b border-outline-variant">
            <h2 className="text-sm font-medium">Sync History</h2>
            <div className="flex items-center gap-unit-1">
              {['all', 'success', 'failed', 'running'].map(key => (
                <button
                  key={key}
                  onClick={() => setFilter(key)}
                  className={`px-unit-2 py-unit-1 text-xs transition-colors ${
                    filter === key ? 'text-white bg-white/[0.05]' : 'text-on-surface-variant hover:text-white'
                  }`}
                >
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {recentJobs.length === 0 ? (
            <div className="text-center py-unit-16">
              <div className="text-label-sm text-on-surface-variant mb-unit-1">No sync jobs yet</div>
              <div className="text-xs text-outline">Start your first sync from the Sync tab</div>
            </div>
          ) : (
            <div>
              {recentJobs.map(job => {
                const status = statusConfig[job.status] || statusConfig.pending
                return (
                  <div key={job.id} className="flex items-center justify-between px-unit-4 py-unit-3 border-b border-outline-variant last:border-b-0 hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center gap-unit-4">
                      <div className={`${status.dot} w-1.5 h-1.5`} />
                      <div>
                        <div className="text-sm font-medium">{formatDirection(job.source_service, job.target_service)}</div>
                        <div className="text-xs text-on-surface-variant">{job.added_tracks || 0} added · {job.failed_tracks || 0} failed · {job.total_tracks || 0} total</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-on-surface-variant">{formatTimeAgo(job.started_at)}</div>
                      {job.completed_at && (
                        <div className="text-xs text-outline">{Math.round((new Date(job.completed_at) - new Date(job.started_at)) / 1000)}s</div>
                      )}
                      {job.error_message && (
                        <div className="text-xs text-error max-w-[200px] truncate">{job.error_message}</div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
