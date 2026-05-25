import { useState } from 'react'
import { endpoints } from '../api'

export default function SyncPanel({ authStatus }) {
  const [syncing, setSyncing] = useState(null)

  const syncActions = [
    {
      id: 'spotify-to-yt',
      title: 'Spotify → YouTube Music',
      description: 'Sync your Spotify playlists to YouTube Music',
      source: 'spotify',
      target: 'ytmusic',
      gradient: 'from-green-500/30 to-green-500/10',
      action: endpoints.sync.spotifyToYt,
    },
    {
      id: 'yt-to-spotify',
      title: 'YouTube Music → Spotify',
      description: 'Sync your YouTube Music playlists to Spotify',
      source: 'ytmusic',
      target: 'spotify',
      gradient: 'from-red-500/30 to-red-500/10',
      action: endpoints.sync.ytToSpotify,
    },
  ]

  const handleSync = async (action) => {
    if (!authStatus[action.source]) {
      alert(`Please connect ${action.source === 'spotify' ? 'Spotify' : 'YouTube Music'} first`)
      return
    }

    setSyncing(action.id)
    try {
      await action.action()
      alert('Sync started! Check dashboard for progress.')
    } catch (error) {
      alert(`Failed: ${error.response?.data?.error || error.message}`)
    } finally {
      setSyncing(null)
    }
  }

  return (
    <div className="min-h-screen bg-black p-8 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-black mb-3">
          <span className="text-gradient">Sync Control</span>
        </h1>
        <p className="text-xl text-gray-400">Sync your music between platforms</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {syncActions.map((action, index) => {
          const canSync = authStatus[action.source] && syncing !== action.id
          
          return (
            <button
              key={action.id}
              onClick={() => handleSync(action)}
              disabled={!canSync}
              className={`card text-left relative overflow-hidden group ${
                !canSync ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${action.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <h3 className="text-2xl font-bold mb-3">{action.title}</h3>
                <p className="text-gray-400 text-sm mb-4">{action.description}</p>
                
                {!authStatus[action.source] && (
                  <div className="flex items-center gap-2 text-yellow-500 text-xs font-semibold bg-yellow-500/10 px-3 py-2 rounded-lg inline-flex">
                    <span>⚠️</span>
                    <span>Authentication Required</span>
                  </div>
                )}
                
                {syncing === action.id && (
                  <div className="flex items-center gap-2 text-blue-500 text-sm font-semibold bg-blue-500/10 px-3 py-2 rounded-lg inline-flex">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    <span>Starting sync...</span>
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
