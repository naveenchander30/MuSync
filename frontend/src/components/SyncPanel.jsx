import { useState } from 'react'
import axios from 'axios'

export default function SyncPanel({ authStatus, syncStatus, apiBase }) {
  const [loading, setLoading] = useState(null)

  const syncActions = [
    {
      id: 'export-spotify',
      title: 'Export from Spotify',
      description: 'Save your Spotify playlists and liked songs to a local backup file',
      icon: '📤',
      gradient: 'from-primary/30 to-primary/10',
      service: 'spotify',
      endpoint: '/api/sync/export/spotify',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg'
    },
    {
      id: 'export-ytmusic',
      title: 'Export from YouTube Music',
      description: 'Save your YouTube Music playlists and liked songs to a local backup file',
      icon: '📤',
      gradient: 'from-red-500/30 to-red-500/10',
      service: 'ytmusic',
      endpoint: '/api/sync/export/ytmusic',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/6/6a/Youtube_Music_icon.svg'
    },
    {
      id: 'import-spotify',
      title: 'Import to Spotify',
      description: 'Restore your playlists and liked songs from backup to Spotify',
      icon: '📥',
      gradient: 'from-primary/30 to-primary/10',
      service: 'spotify',
      endpoint: '/api/sync/import/spotify',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg'
    },
    {
      id: 'import-ytmusic',
      title: 'Import to YouTube Music',
      description: 'Restore your playlists and liked songs from backup to YouTube Music',
      icon: '📥',
      gradient: 'from-red-500/30 to-red-500/10',
      service: 'ytmusic',
      endpoint: '/api/sync/import/ytmusic',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/6/6a/Youtube_Music_icon.svg'
    }
  ]

  const handleSync = async (action) => {
    if (syncStatus.is_running) {
      alert('A sync task is already running. Please wait for it to complete.')
      return
    }

    if (!authStatus[action.service]) {
      alert(`Please connect to ${action.service === 'spotify' ? 'Spotify' : 'YouTube Music'} first in the sidebar.`)
      return
    }

    setLoading(action.id)
    try {
      await axios.post(`${apiBase}${action.endpoint}`)
      // Success feedback is handled by real-time status updates
    } catch (error) {
      alert(`Failed to start sync: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-black p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-5xl font-black mb-3">
          <span className="text-gradient">Sync Control</span>
        </h1>
        <p className="text-xl text-gray-400">Export and import your music library across platforms</p>
      </div>

      {/* Sync Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        {syncActions.map((action, index) => {
          const isConnected = authStatus[action.service]
          const isDisabled = !isConnected || syncStatus.is_running || loading === action.id

          return (
            <button
              key={action.id}
              onClick={() => handleSync(action)}
              disabled={isDisabled}
              className={`card text-left relative overflow-hidden group ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${action.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              
              <div className="relative z-10 flex items-start gap-6">
                {/* Icon Section */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <img src={action.logo} alt={action.service} className="w-10 h-10" />
                  </div>
                </div>
                
                {/* Content Section */}
                <div className="flex-1 min-w-0">
                  <h3 className="text-2xl font-bold mb-2 group-hover:text-white transition-colors">{action.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed mb-4">{action.description}</p>
                  
                  {/* Status Indicators */}
                  {!isConnected && (
                    <div className="flex items-center gap-2 text-yellow-500 text-xs font-semibold bg-yellow-500/10 px-3 py-2 rounded-lg inline-flex">
                      <span className="animate-pulse">⚠️</span>
                      <span>Authentication Required</span>
                    </div>
                  )}
                  
                  {loading === action.id && (
                    <div className="flex items-center gap-2 text-primary text-sm font-semibold bg-primary/10 px-3 py-2 rounded-lg inline-flex">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                      <span>Starting sync...</span>
                    </div>
                  )}
                </div>

                {/* Action Icon */}
                <div className="text-5xl opacity-50 group-hover:opacity-100 group-hover:scale-110 transition-all">
                  {action.icon}
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Current Status Section */}
      {syncStatus.is_running && (
        <div className="card bg-gradient-to-br from-accent-blue/20 via-accent-purple/20 to-accent-pink/20 border-accent-blue/30 glow-primary animate-fade-in">
          <div className="flex items-center gap-6 mb-8">
            <div className="relative">
              <div className="w-6 h-6 bg-accent-blue rounded-full animate-pulse" />
              <div className="absolute inset-0 w-6 h-6 bg-accent-blue rounded-full animate-ping" />
            </div>
            <h3 className="text-3xl font-bold text-gradient-blue">
              Sync in Progress
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-black/30 rounded-2xl p-6 border border-white/10">
              <div className="text-gray-400 text-xs uppercase tracking-widest mb-3">Current Task</div>
              <div className="text-white font-bold text-xl">{syncStatus.current_task}</div>
            </div>
            
            <div className="bg-black/30 rounded-2xl p-6 border border-white/10">
              <div className="text-gray-400 text-xs uppercase tracking-widest mb-3">Playlist</div>
              <div className="text-white font-bold text-xl truncate">{syncStatus.current_playlist || 'Initializing...'}</div>
            </div>
            
            <div className="bg-black/30 rounded-2xl p-6 border border-primary/30">
              <div className="text-gray-400 text-xs uppercase tracking-widest mb-3">Successfully Added</div>
              <div className="text-primary font-black text-4xl">{syncStatus.added}</div>
            </div>
            
            <div className="bg-black/30 rounded-2xl p-6 border border-red-500/30">
              <div className="text-gray-400 text-xs uppercase tracking-widest mb-3">Failed</div>
              <div className="text-red-400 font-black text-4xl">{syncStatus.failed}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
