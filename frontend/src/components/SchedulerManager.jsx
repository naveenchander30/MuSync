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

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-sm text-on-surface-variant">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="px-unit-8 py-unit-6 border-b border-outline-variant">
        <div className="flex items-center justify-between">
          <h1 className="text-headline-md">Scheduled Syncs</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-unit-4 py-unit-2 bg-white text-on-primary text-sm font-medium hover:bg-white/90 transition-colors"
          >
            Create Schedule
          </button>
        </div>
      </div>

      <div className="p-unit-8 max-w-3xl">
        {showForm && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="w-full max-w-md border border-outline-variant bg-black p-unit-6">
              <h2 className="text-sm font-medium mb-unit-6">Create Schedule</h2>
              <div className="space-y-unit-4">
                <div>
                  <div className="text-label-sm text-on-surface-variant uppercase mb-unit-1">Name</div>
                  <input
                    type="text"
                    value={newJob.name}
                    onChange={e => setNewJob({...newJob, name: e.target.value})}
                    className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
                    placeholder="e.g. Daily Sync"
                  />
                </div>
                <div className="grid grid-cols-2 gap-unit-4">
                  <div>
                    <div className="text-label-sm text-on-surface-variant uppercase mb-unit-1">Source</div>
                    <select
                      value={newJob.source_service}
                      onChange={e => setNewJob({...newJob, source_service: e.target.value})}
                      className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
                    >
                      <option value="spotify">Spotify</option>
                      <option value="ytmusic">YouTube Music</option>
                    </select>
                  </div>
                  <div>
                    <div className="text-label-sm text-on-surface-variant uppercase mb-unit-1">Target</div>
                    <select
                      value={newJob.target_service}
                      onChange={e => setNewJob({...newJob, target_service: e.target.value})}
                      className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
                    >
                      <option value="ytmusic">YouTube Music</option>
                      <option value="spotify">Spotify</option>
                    </select>
                  </div>
                </div>
                <div>
                  <div className="text-label-sm text-on-surface-variant uppercase mb-unit-1">Interval (minutes)</div>
                  <input
                    type="number"
                    value={newJob.interval_minutes}
                    onChange={e => setNewJob({...newJob, interval_minutes: parseInt(e.target.value)})}
                    className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
                    min="1"
                  />
                </div>
                <div className="flex gap-unit-2 pt-unit-4">
                  <button onClick={handleCreate} className="flex-1 py-unit-2 bg-white text-on-primary text-sm font-medium hover:bg-white/90 transition-colors">
                    Save
                  </button>
                  <button onClick={() => setShowForm(false)} className="flex-1 py-unit-2 border border-outline-variant text-sm text-on-surface-variant hover:text-white transition-colors">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-unit-3">
          {jobs.length === 0 ? (
            <div className="border border-outline-variant p-unit-8 text-center">
              <div className="text-sm text-on-surface-variant">No scheduled jobs</div>
              <div className="text-xs text-outline mt-unit-1">Create one to automate your syncs</div>
            </div>
          ) : (
            jobs.map(job => (
              <div key={job.id} className={`border border-outline-variant p-unit-4 ${job.enabled ? 'border-l-2 border-l-white' : ''}`}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-unit-2 mb-unit-1">
                      <div className={`w-1.5 h-1.5 ${job.enabled ? 'bg-success' : 'bg-outline'}`} />
                      <span className="text-sm font-medium">{job.name}</span>
                    </div>
                    <div className="text-xs text-on-surface-variant font-mono">
                      {job.source_service === 'spotify' ? 'spotify' : 'ytmusic'} → {job.target_service === 'spotify' ? 'spotify' : 'ytmusic'} · every {job.interval_minutes}m
                    </div>
                    {job.next_run && (
                      <div className="text-xs text-outline mt-unit-1">
                        Next run: {new Date(job.next_run).toLocaleString()}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-unit-3">
                    <button
                      onClick={() => handleToggle(job)}
                      className={`w-8 h-4 border transition-colors relative ${
                        job.enabled ? 'bg-white border-white' : 'border-outline-variant'
                      }`}
                    >
                      <div className={`absolute top-[1px] w-[14px] h-[14px] bg-black transition-all ${
                        job.enabled ? 'left-[17px]' : 'left-[1px]'
                      }`} />
                    </button>
                    <button onClick={() => handleDelete(job.id)} className="text-xs text-on-surface-variant hover:text-error transition-colors">
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
