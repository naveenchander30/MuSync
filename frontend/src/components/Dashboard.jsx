export default function Dashboard({ syncStatus }) {
  const stats = [
    {
      label: 'Tracks Added',
      value: syncStatus.added,
      color: 'text-primary',
      icon: '✓',
      bgGradient: 'from-primary/20 to-primary/5'
    },
    {
      label: 'Tracks Failed',
      value: syncStatus.failed,
      color: 'text-red-400',
      icon: '✗',
      bgGradient: 'from-red-500/20 to-red-500/5'
    },
    {
      label: 'Current Status',
      value: syncStatus.current_playlist || 'Idle',
      color: 'text-accent-blue',
      icon: '♫',
      bgGradient: 'from-accent-blue/20 to-accent-purple/5',
      isText: true
    }
  ]

  return (
    <div className="min-h-screen bg-black p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-5xl font-black mb-3">
          <span className="text-gradient">Dashboard</span>
        </h1>
        <p className="text-xl text-gray-400">Monitor your music synchronization in real-time</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {stats.map((stat, index) => (
          <div
            key={index}
            className={`bg-gradient-to-br ${stat.bgGradient} border border-white/10 rounded-3xl p-8 transition-all duration-500 hover:scale-105 hover:border-white/20 group animate-slide-up`}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`text-4xl ${stat.color} font-bold group-hover:scale-110 transition-transform`}>
                {stat.icon}
              </div>
              <div className={`text-5xl font-black ${stat.color} ${stat.isText ? 'text-xl' : ''}`}>
                {stat.value}
              </div>
            </div>
            <div className="text-sm uppercase tracking-widest text-gray-500 font-semibold">
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Status Banner */}
      {syncStatus.is_running && (
        <div className="bg-gradient-to-r from-accent-blue/20 via-accent-purple/20 to-accent-pink/20 border border-accent-blue/30 rounded-3xl p-8 mb-12 glow-primary animate-fade-in">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="w-6 h-6 bg-accent-blue rounded-full animate-pulse" />
              <div className="absolute inset-0 w-6 h-6 bg-accent-blue rounded-full animate-ping" />
            </div>
            <div className="flex-1">
              <div className="text-accent-blue font-bold text-2xl mb-1">Sync in Progress</div>
              <div className="text-gray-400">{syncStatus.current_task}</div>
            </div>
            <div className="text-right space-y-2">
              <div className="text-primary font-mono text-xl">+{syncStatus.added}</div>
              <div className="text-red-400 font-mono text-xl">-{syncStatus.failed}</div>
            </div>
          </div>
        </div>
      )}

      {/* Activity Logs */}
      <div className="bg-gradient-to-br from-dark-100 to-dark-200 border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
        <div className="p-8 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gradient mb-2">Activity Logs</h2>
              <p className="text-gray-400">Real-time sync operation logs</p>
            </div>
            <div className="bg-white/5 px-4 py-2 rounded-full">
              <span className="text-sm text-gray-400">{syncStatus.logs.length} entries</span>
            </div>
          </div>
        </div>
        
        <div className="p-8 max-h-[500px] overflow-y-auto custom-scrollbar">
          {syncStatus.logs.length > 0 ? (
            <div className="space-y-3">
              {syncStatus.logs.slice().reverse().map((log, index) => (
                <div 
                  key={index} 
                  className="font-mono text-sm text-gray-400 hover:text-gray-200 transition-all p-4 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 group"
                >
                  <span className="text-primary mr-3 group-hover:scale-125 inline-block transition-transform">▸</span>
                  {log}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="text-8xl mb-6 opacity-20 animate-float">📝</div>
              <div className="text-2xl font-bold text-gray-500 mb-2">No activity yet</div>
              <div className="text-gray-600">Start a sync task to see real-time updates here</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
