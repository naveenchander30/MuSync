import { useState, useEffect } from 'react'
import { endpoints } from '../api'

export default function Dashboard() {
  const [recentJobs, setRecentJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadJobs()
    const interval = setInterval(loadJobs, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadJobs = async () => {
    try {
      const response = await endpoints.jobs.getByUser()
      setRecentJobs(response.data.slice(0, 10))
    } catch (error) {
      console.error('Failed to load jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'failed': return 'text-red-500'
      case 'running': return 'text-blue-500'
      default: return 'text-gray-500'
    }
  }

  const formatDirection = (source, target) => {
    const shortSource = source === 'spotify' ? 'Spotify' : 'YT Music'
    const shortTarget = target === 'spotify' ? 'Spotify' : 'YT Music'
    return `${shortSource} → ${shortTarget}`
  }

  if (loading) {
    return <div className="p-8">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-black p-8 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-black mb-3">
          <span className="text-gradient">Dashboard</span>
        </h1>
        <p className="text-xl text-gray-400">Monitor your sync operations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="card">
          <div className="text-gray-400 text-sm mb-2">Total Syncs</div>
          <div className="text-4xl font-black text-white">{recentJobs.length}</div>
        </div>
        <div className="card">
          <div className="text-gray-400 text-sm mb-2">Successful</div>
          <div className="text-4xl font-black text-green-500">
            {recentJobs.filter(j => j.status === 'success').length}
          </div>
        </div>
        <div className="card">
          <div className="text-gray-400 text-sm mb-2">Failed</div>
          <div className="text-4xl font-black text-red-500">
            {recentJobs.filter(j => j.status === 'failed').length}
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Recent Sync Jobs</h2>
        {recentJobs.length === 0 ? (
          <div className="text-gray-400 text-center py-12">
            No sync jobs yet. Start your first sync!
          </div>
        ) : (
          <div className="space-y-4">
            {recentJobs.map(job => (
              <div
                key={job.id}
                className="bg-white/5 rounded-xl p-6 border border-white/10"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`font-semibold ${getStatusColor(job.status)}`}>
                        {job.status.toUpperCase()}
                      </span>
                      <span className="text-white font-medium">
                        {formatDirection(job.source_service, job.target_service)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400">
                      {job.added_tracks} added • {job.failed_tracks} failed
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">
                      {new Date(job.started_at).toLocaleDateString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(job.started_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
