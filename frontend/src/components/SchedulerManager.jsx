import { useState, useEffect } from 'react'
import { endpoints } from '../api'

export default function SchedulerManager() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newJob, setNewJob] = useState({
    name: '',
    source_service: 'spotify',
    target_service: 'ytmusic',
    interval_minutes: 60,
  })

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await endpoints.scheduler.getByUser()
      setJobs(response.data)
    } catch (error) {
      console.error('Failed to load jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    try {
      await endpoints.scheduler.create(newJob)
      setShowForm(false)
      setNewJob({ name: '', source_service: 'spotify', target_service: 'ytmusic', interval_minutes: 60 })
      loadJobs()
    } catch (error) {
      alert(`Failed: ${error.response?.data?.error || error.message}`)
    }
  }

  const handleToggle = async (job) => {
    try {
      await endpoints.scheduler.update(job.id, { enabled: !job.enabled })
      loadJobs()
    } catch (error) {
      alert('Failed to update job')
    }
  }

  const handleDelete = async (jobId) => {
    if (!confirm('Delete this scheduled job?')) return
    try {
      await endpoints.scheduler.delete(jobId)
      loadJobs()
    } catch (error) {
      alert('Failed to delete job')
    }
  }

  if (loading) return <div className="p-8">Loading...</div>

  return (
    <div className="min-h-screen bg-black p-8 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-black mb-3">
          <span className="text-gradient">Scheduler</span>
        </h1>
        <p className="text-xl text-gray-400">Automate your sync operations</p>
      </div>

      <button
        onClick={() => setShowForm(!showForm)}
        className="mb-6 px-6 py-3 bg-primary/20 border border-primary/50 rounded-xl text-white font-medium hover:bg-primary/30 transition-all"
      >
        {showForm ? 'Cancel' : '+ New Schedule'}
      </button>

      {showForm && (
        <div className="card mb-6">
          <h2 className="text-2xl font-bold mb-6">Create Schedule</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Name</label>
              <input
                type="text"
                value={newJob.name}
                onChange={(e) => setNewJob({...newJob, name: e.target.value})}
                className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                placeholder="e.g., Daily Sync"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Source</label>
                <select
                  value={newJob.source_service}
                  onChange={(e) => setNewJob({...newJob, source_service: e.target.value})}
                  className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value="spotify">Spotify</option>
                  <option value="ytmusic">YouTube Music</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Target</label>
                <select
                  value={newJob.target_service}
                  onChange={(e) => setNewJob({...newJob, target_service: e.target.value})}
                  className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value="ytmusic">YouTube Music</option>
                  <option value="spotify">Spotify</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-2">Interval (minutes)</label>
              <input
                type="number"
                value={newJob.interval_minutes}
                onChange={(e) => setNewJob({...newJob, interval_minutes: parseInt(e.target.value)})}
                className="w-full p-3 bg-white/5 border border-white/10 rounded-xl text-white"
                min="1"
              />
            </div>
            
            <button
              onClick={handleCreate}
              className="w-full py-3 bg-primary rounded-xl text-white font-bold hover:bg-primary/80 transition-all"
            >
              Create Schedule
            </button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {jobs.length === 0 ? (
          <div className="card text-gray-400 text-center py-12">
            No scheduled jobs. Create one to automate your syncs!
          </div>
        ) : (
          jobs.map(job => (
            <div key={job.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`w-3 h-3 rounded-full ${job.enabled ? 'bg-green-500' : 'bg-gray-500'}`} />
                    <span className="text-white font-bold text-lg">{job.name}</span>
                  </div>
                  <div className="text-sm text-gray-400">
                    {job.source_service === 'spotify' ? 'Spotify' : 'YT Music'} → {job.target_service === 'spotify' ? 'Spotify' : 'YT Music'}
                    • Every {job.interval_minutes} minutes
                  </div>
                  {job.next_run && (
                    <div className="text-xs text-gray-500 mt-1">
                      Next run: {new Date(job.next_run).toLocaleString()}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleToggle(job)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      job.enabled
                        ? 'bg-red-500/20 text-red-500 hover:bg-red-500/30'
                        : 'bg-green-500/20 text-green-500 hover:bg-green-500/30'
                    }`}
                  >
                    {job.enabled ? 'Disable' : 'Enable'}
                  </button>
                  <button
                    onClick={() => handleDelete(job.id)}
                    className="px-4 py-2 rounded-lg text-sm font-medium bg-white/5 text-gray-400 hover:bg-red-500/20 hover:text-red-500 transition-all"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
