import { useState } from 'react'
import { endpoints } from '../api'

export default function SyncPanel({ authStatus }) {
  const [syncing, setSyncing] = useState(null)
  const [source, setSource] = useState('spotify')
  const [target, setTarget] = useState('ytmusic')
  const [mode, setMode] = useState('full')

  const syncModes = [
    { id: 'full', label: 'Full Library' },
    { id: 'selected', label: 'Selected Playlists' },
    { id: 'incremental', label: 'Incremental' },
  ]

  const toggleOptions = [
    { id: 'liked', label: 'Include liked songs' },
    { id: 'metadata', label: 'Match by metadata' },
    { id: 'resolve', label: 'Auto-resolve conflicts' },
  ]

  const [toggles, setToggles] = useState({ liked: true, metadata: true, resolve: false })

  const handleSync = async () => {
    if (!authStatus[source]) {
      alert(`Please connect ${source === 'spotify' ? 'Spotify' : 'YouTube Music'} first`)
      return
    }
    setSyncing(`${source}-to-${target}`)
    try {
      const action = source === 'spotify' ? endpoints.sync.spotifyToYt : endpoints.sync.ytToSpotify
      await action()
      alert('Sync started! Check dashboard for progress.')
    } catch (error) {
      alert(`Failed: ${error.response?.data?.error || error.message}`)
    } finally {
      setSyncing(null)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      <div className="px-unit-8 py-unit-6 border-b border-outline-variant">
        <div className="flex items-center justify-between">
          <h1 className="text-headline-md">Sync Music</h1>
          <button
            onClick={handleSync}
            disabled={syncing !== null}
            className="px-unit-4 py-unit-2 bg-white text-on-primary text-sm font-medium hover:bg-white/90 transition-colors disabled:opacity-50"
          >
            {syncing ? 'Starting...' : 'Start New Sync'}
          </button>
        </div>
      </div>

      <div className="p-unit-8 max-w-2xl">
        <div className="space-y-unit-8">
          <div className="grid grid-cols-2 gap-unit-4">
            <div>
              <div className="text-label-sm text-on-surface-variant uppercase mb-unit-2">From</div>
              <select
                value={source}
                onChange={e => setSource(e.target.value)}
                className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
              >
                <option value="spotify">Spotify</option>
                <option value="ytmusic">YouTube Music</option>
              </select>
            </div>
            <div>
              <div className="text-label-sm text-on-surface-variant uppercase mb-unit-2">To</div>
              <select
                value={target}
                onChange={e => setTarget(e.target.value)}
                className="w-full bg-transparent text-white py-unit-2 border-b border-outline-variant focus:border-white outline-none text-sm"
              >
                <option value="ytmusic">YouTube Music</option>
                <option value="spotify">Spotify</option>
              </select>
            </div>
          </div>

          <div>
            <div className="text-label-sm text-on-surface-variant uppercase mb-unit-2">Sync Type</div>
            <div className="flex gap-unit-1">
              {syncModes.map(m => (
                <button
                  key={m.id}
                  onClick={() => setMode(m.id)}
                  className={`px-unit-3 py-unit-1 text-xs transition-colors ${
                    mode === m.id ? 'bg-white text-on-primary' : 'border border-outline-variant text-on-surface-variant hover:text-white'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="text-label-sm text-on-surface-variant uppercase mb-unit-2">Options</div>
            <div className="space-y-unit-2">
              {toggleOptions.map(opt => (
                <label key={opt.id} className="flex items-center justify-between py-unit-2 border-b border-outline-variant cursor-pointer">
                  <span className="text-sm">{opt.label}</span>
                  <button
                    onClick={() => setToggles(prev => ({ ...prev, [opt.id]: !prev[opt.id] }))}
                    className={`w-8 h-4 border transition-colors relative ${
                      toggles[opt.id] ? 'bg-white border-white' : 'border-outline-variant'
                    }`}
                  >
                    <div className={`absolute top-[1px] w-[14px] h-[14px] bg-black transition-all ${
                      toggles[opt.id] ? 'left-[17px]' : 'left-[1px]'
                    }`} />
                  </button>
                </label>
              ))}
            </div>
          </div>

          {syncing && (
            <div className="border border-outline-variant p-unit-4">
              <div className="flex items-center justify-between mb-unit-2">
                <div className="flex items-center gap-unit-2">
                  <div className="w-1.5 h-1.5 bg-primary" />
                  <span className="text-xs font-mono">Syncing tracks...</span>
                </div>
                <button className="text-xs text-error hover:text-white transition-colors">Cancel</button>
              </div>
              <div className="h-[1px] bg-outline-variant relative">
                <div className="h-full bg-primary transition-all absolute top-0 left-0" style={{ width: '17%' }} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
