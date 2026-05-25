import { endpoints } from '../api'

export default function Auth({ authStatus, onAuthChange }) {
  const handleConnectSpotify = () => {
    window.location.href = endpoints.auth.spotifyLogin()
  }

  const handleConnectYTMusic = () => {
    window.location.href = endpoints.auth.ytmusicLogin()
  }

  return (
    <div className="space-y-4">
      <button
        onClick={handleConnectSpotify}
        className={`w-full p-4 rounded-xl transition-all ${
          authStatus.spotify
            ? 'bg-green-500/20 border border-green-500/50'
            : 'bg-white/5 border border-white/10 hover:bg-white/10'
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="font-medium">
            {authStatus.spotify ? 'Spotify Connected' : 'Connect Spotify'}
          </span>
        </div>
      </button>

      <button
        onClick={handleConnectYTMusic}
        className={`w-full p-4 rounded-xl transition-all ${
          authStatus.ytmusic
            ? 'bg-red-500/20 border border-red-500/50'
            : 'bg-white/5 border border-white/10 hover:bg-white/10'
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="font-medium">
            {authStatus.ytmusic ? 'YouTube Music Connected' : 'Connect YouTube Music'}
          </span>
        </div>
      </button>
    </div>
  )
}
