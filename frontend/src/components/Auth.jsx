import { endpoints } from '../api'

export default function Auth({ authStatus, onAuthChange }) {
  const handleConnectSpotify = () => {
    window.location.href = endpoints.auth.spotifyLogin()
  }

  const handleConnectYTMusic = () => {
    window.location.href = endpoints.auth.ytmusicLogin()
  }

  return (
    <div className="space-y-unit-2">
      <button
        onClick={handleConnectSpotify}
        className={`w-full px-unit-3 py-unit-3 border transition-colors text-left ${
          authStatus.spotify
            ? 'border-white/30 bg-white/[0.03]'
            : 'border-outline-variant hover:border-white/30'
        }`}
      >
        <div className="flex items-center gap-unit-2">
          <div className={`w-2 h-2 ${authStatus.spotify ? 'bg-success' : 'bg-outline'}`} />
          <span className="text-xs font-medium">
            {authStatus.spotify ? 'Spotify Connected' : 'Connect Spotify'}
          </span>
        </div>
      </button>

      <button
        onClick={handleConnectYTMusic}
        className={`w-full px-unit-3 py-unit-3 border transition-colors text-left ${
          authStatus.ytmusic
            ? 'border-white/30 bg-white/[0.03]'
            : 'border-outline-variant hover:border-white/30'
        }`}
      >
        <div className="flex items-center gap-unit-2">
          <div className={`w-2 h-2 ${authStatus.ytmusic ? 'bg-success' : 'bg-outline'}`} />
          <span className="text-xs font-medium">
            {authStatus.ytmusic ? 'YT Music Connected' : 'Connect YT Music'}
          </span>
        </div>
      </button>
    </div>
  )
}
