import { useState, useEffect } from 'react'
import { endpoints } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState({ total: 0, success: 0, failed: 0, running: 0 })
  const [recentJobs, setRecentJobs] = useState([])
  const [activeJob, setActiveJob] = useState(null)
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 3000)
    return () => clearInterval(interval)
  }, [filter])

  const loadData = async () => {
    try {
      const jobsRes = await endpoints.jobs.getByUser()
      const jobs = jobsRes.data
      
      const active = jobs.find(j => j.status === 'running' || j.status === 'pending')
      setActiveJob(active || null)

      const filtered = filter === 'all' 
        ? jobs 
        : jobs.filter(j => j.status === filter)
      
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-emerald-400'
      case 'failed': return 'text-red-400'
      case 'running': return 'text-blue-400'
      case 'pending': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusBg = (status) => {
    switch (status) {
      case 'success': return 'bg-emerald-500/10 border-emerald-500/30'
      case 'failed': return 'bg-red-500/10 border-red-500/30'
      case 'running': return 'bg-blue-500/10 border-blue-500/30'
      case 'pending': return 'bg-yellow-500/10 border-yellow-500/30'
      default: return 'bg-white/5 border-white/10'
    }
  }

  const formatDirection = (source, target) => {
    const s = source === 'spotify' ? 'Spotify' : 'YT Music'
    const t = target === 'spotify' ? 'Spotify' : 'YT Music'
    return `${s} → ${t}`
  }

  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return 'N/A'
    const diff = Date.now() - new Date(dateStr).getTime()
    const minutes = Math.floor(diff / 60000)
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  }

  const filterOptions = [
    { key: 'all', label: 'All', count: stats.total },
    { key: 'success', label: 'Success', count: stats.success },
    { key: 'failed', label: 'Failed', count: stats.failed },
    { key: 'running', label: 'Running', count: stats.running },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-5xl font-black mb-2">
            <span className="text-gradient">Dashboard</span>
          </h1>
          <p className="text-gray-400 text-lg">Monitor and manage your sync operations</p>
        </div>

        {activeJob && (
          <div className="mb-8 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 border border-blue-500/30 rounded-2xl p-6 animate-pulse-slow">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-4 h-4 bg-blue-400 rounded-full" />
                  <div className="absolute inset-0 w-4 h-4 bg-blue-400 rounded-full animate-ping opacity-50" />
                </div>
                <div>
                  <div className="text-blue-400 font-bold text-xl">Sync in Progress</div>
                  <div className="text-gray-400 text-sm">{formatDirection(activeJob.source_service, activeJob.target_service)}</div>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <div className="text-gray-400 text-xs uppercase tracking-wider">Progress</div>
                  <div className="text-white font-bold text-2xl">{activeJob.progress_percentage}%</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-400 text-xs uppercase tracking-wider">Tracks</div>
                  <div className="text-emerald-400 font-bold text-lg">+{activeJob.added_tracks || 0}</div>
                </div>
                <div className="w-48 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${activeJob.progress_percentage}%` }}
                  />
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-blue-500/20 flex items-center gap-4">
              {activeJob.current_track_image_url ? (
                <img
                  src={activeJob.current_track_image_url}
                  alt="Album art"
                  className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-lg">🎵</span>
                </div>
              )}
              <div className="min-w-0">
                {activeJob.current_playlist_name && (
                  <div className="text-gray-400 text-sm truncate">
                    Playlist: <span className="text-white">{activeJob.current_playlist_name}</span>
                  </div>
                )}
                {activeJob.current_track_name && (
                  <div className="text-gray-300 text-sm truncate mt-0.5">
                    <span className="text-blue-400">→</span> Now: <span className="text-white font-medium">{activeJob.current_track_name}</span>
                    {activeJob.current_track_artist && (
                      <span className="text-gray-400"> — {activeJob.current_track_artist}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <div className="bg-gradient-to-br from-white/5 to-white/2 border border-white/10 rounded-2xl p-6">
            <div className="text-gray-400 text-sm mb-1">Total Syncs</div>
            <div className="text-4xl font-black text-white">{stats.total}</div>
          </div>
          <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-500/2 border border-emerald-500/20 rounded-2xl p-6">
            <div className="text-emerald-400/70 text-sm mb-1">Successful</div>
            <div className="text-4xl font-black text-emerald-400">{stats.success}</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/10 to-red-500/2 border border-red-500/20 rounded-2xl p-6">
            <div className="text-red-400/70 text-sm mb-1">Failed</div>
            <div className="text-4xl font-black text-red-400">{stats.failed}</div>
          </div>
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/2 border border-blue-500/20 rounded-2xl p-6">
            <div className="text-blue-400/70 text-sm mb-1">Running</div>
            <div className="text-4xl font-black text-blue-400">{stats.running}</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 mb-6">
          {filterOptions.map(opt => (
            <button
              key={opt.key}
              onClick={() => setFilter(opt.key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                filter === opt.key
                  ? 'bg-white/10 text-white border border-white/20'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {opt.label}
              <span className="ml-2 text-xs opacity-60">{opt.count}</span>
            </button>
          ))}
        </div>

        {/* Job History */}
        <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
          <div className="p-6 border-b border-white/10">
            <h2 className="text-xl font-bold">Sync History</h2>
          </div>
          
          {recentJobs.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-6xl mb-4 opacity-20">📭</div>
              <div className="text-xl font-bold text-gray-500 mb-2">
                {filter === 'all' ? 'No sync jobs yet' : `No ${filter} jobs`}
              </div>
              <div className="text-gray-600">
                {filter === 'all' ? 'Start your first sync from the Sync tab' : 'Try a different filter'}
              </div>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {recentJobs.map(job => (
                <div
                  key={job.id}
                  className="p-6 hover:bg-white/5 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider border ${getStatusBg(job.status)} ${getStatusColor(job.status)}`}>
                        {job.status}
                      </div>
                      <div>
                        <div className="text-white font-semibold">
                          {formatDirection(job.source_service, job.target_service)}
                        </div>
                        <div className="text-gray-500 text-sm mt-0.5">
                          {job.added_tracks || 0} added • {job.failed_tracks || 0} failed • {job.total_tracks || 0} total
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-gray-400 text-sm">
                        {formatTimeAgo(job.started_at)}
                      </div>
                      {job.completed_at && (
                        <div className="text-gray-600 text-xs mt-0.5">
                          Duration: {Math.round((new Date(job.completed_at) - new Date(job.started_at)) / 1000)}s
                        </div>
                      )}
                      {job.error_message && (
                        <div className="text-red-400 text-xs mt-1 max-w-xs truncate" title={job.error_message}>
                          {job.error_message}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => endpoints.sync.spotifyToYt()}
            className="bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20 rounded-2xl p-6 text-left hover:border-green-500/40 transition-all group"
          >
            <div className="text-green-400 text-2xl mb-2">🔄</div>
            <div className="text-white font-bold mb-1">Quick Sync</div>
            <div className="text-gray-400 text-sm">Spotify → YT Music</div>
          </button>
          
          <button
            onClick={() => endpoints.sync.ytToSpotify()}
            className="bg-gradient-to-br from-red-500/10 to-transparent border border-red-500/20 rounded-2xl p-6 text-left hover:border-red-500/40 transition-all group"
          >
            <div className="text-red-400 text-2xl mb-2">🔄</div>
            <div className="text-white font-bold mb-1">Quick Sync</div>
            <div className="text-gray-400 text-sm">YT Music → Spotify</div>
          </button>
          
          <a
            href="/scheduler"
            className="bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20 rounded-2xl p-6 text-left hover:border-blue-500/40 transition-all group"
          >
            <div className="text-blue-400 text-2xl mb-2">⏰</div>
            <div className="text-white font-bold mb-1">Auto Sync</div>
            <div className="text-gray-400 text-sm">Set up scheduled syncs</div>
          </a>
        </div>
      </div>
    </div>
  )
}
