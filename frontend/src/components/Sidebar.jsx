import Auth from './Auth'

export default function Sidebar({ currentPage, onNavigate, authStatus, onAuthChange }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'sync', label: 'Sync', icon: '🔄' },
    { id: 'scheduler', label: 'Scheduler', icon: '⏰' },
  ]

  return (
    <div className="w-80 bg-dark-100 border-r border-white/10 flex flex-col">
      <div className="p-8 border-b border-white/10">
        <h1 className="text-3xl font-black text-gradient">MuSync</h1>
        <p className="text-gray-500 text-sm mt-1">v2.0</p>
      </div>
      
      <nav className="flex-1 p-4">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl mb-2 transition-all ${
              currentPage === item.id
                ? 'bg-white/10 text-white'
                : 'text-gray-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            <span className="text-2xl">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="p-6 border-t border-white/10">
        <h3 className="text-sm text-gray-500 uppercase tracking-widest mb-4 font-semibold">Connections</h3>
        <Auth authStatus={authStatus} onAuthChange={onAuthChange} />
      </div>
    </div>
  )
}
