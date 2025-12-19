const AUTH_SERVER = import.meta.env.VITE_AUTH_SERVER || 'https://musync-k60r.onrender.com'

export default function Sidebar({ currentPage, onNavigate, authStatus }) {
  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'sync', icon: '🔄', label: 'Sync' },
  ]

  const handleAuth = (service) => {
    const url = `${AUTH_SERVER}/${service}/login`
    window.open(url, '_blank')
  }

  return (
    <div className="w-72 bg-gradient-to-b from-dark-100 to-dark-300 border-r border-white/10 flex flex-col shadow-2xl">
      {/* Header */}
      <div className="p-8 border-b border-white/10">
        <div className="flex items-center gap-3 mb-3">
          <div className="text-4xl">🎵</div>
          <h1 className="text-3xl font-black text-gradient">
            MuSync
          </h1>
        </div>
        <p className="text-gray-500 text-sm uppercase tracking-widest font-semibold">Music Synchronizer</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-6">
        <div className="space-y-3">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-4 px-6 py-4 rounded-2xl transition-all duration-300 font-semibold text-lg ${
                currentPage === item.id
                  ? 'bg-primary text-white shadow-lg shadow-primary/30'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <span className="text-2xl">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Auth Status */}
      <div className="p-6 border-t border-white/10 bg-gradient-to-b from-transparent to-black/50">
        <h3 className="text-xs uppercase tracking-widest text-gray-500 font-bold mb-4">
          Connections
        </h3>
        <div className="space-y-3">
          {/* Spotify */}
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <img 
                  src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" 
                  alt="Spotify" 
                  className="w-6 h-6"
                />
                <span className="font-semibold">Spotify</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                authStatus.spotify ? 'bg-primary shadow-lg shadow-primary/50 animate-pulse' : 'bg-gray-600'
              }`} />
            </div>
            {!authStatus.spotify && (
              <button
                onClick={() => handleAuth('spotify')}
                className="w-full bg-primary/10 hover:bg-primary/20 text-primary text-sm font-semibold py-2 rounded-lg transition-all"
              >
                Connect
              </button>
            )}
          </div>

          {/* YouTube Music */}
          <div className="bg-white/5 rounded-2xl p-4 border border-white/10 hover:border-white/20 transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <img 
                  src="https://upload.wikimedia.org/wikipedia/commons/6/6a/Youtube_Music_icon.svg" 
                  alt="YouTube Music" 
                  className="w-6 h-6"
                />
                <span className="font-semibold">YT Music</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${
                authStatus.ytmusic ? 'bg-primary shadow-lg shadow-primary/50 animate-pulse' : 'bg-gray-600'
              }`} />
            </div>
            {!authStatus.ytmusic && (
              <button
                onClick={() => handleAuth('ytmusic')}
                className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-500 text-sm font-semibold py-2 rounded-lg transition-all"
              >
                Connect
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-white/10">
        <p className="text-xs text-gray-600 text-center">v2.0 • Modern Edition</p>
      </div>
    </div>
  )
}
