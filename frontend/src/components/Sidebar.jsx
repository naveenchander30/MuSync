import Auth from './Auth'
import Logo from './Logo'

export default function Sidebar({ currentPage, onNavigate, authStatus, onAuthChange }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' },
    { id: 'sync', label: 'Sync', icon: 'M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9m-9 9a9 9 0 0 1 9-9' },
    { id: 'scheduler', label: 'Scheduler', icon: 'M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' },
  ]

  return (
    <div className="w-60 bg-black border-r border-outline-variant flex flex-col flex-shrink-0">
      <div className="px-unit-4 py-unit-6 border-b border-outline-variant">
        <Logo />
      </div>

      <nav className="flex-1 py-unit-2">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`w-full flex items-center gap-unit-3 px-unit-4 py-unit-3 text-sm transition-colors ${
              currentPage === item.id
                ? 'text-white border-l-2 border-white bg-white/[0.02]'
                : 'text-on-surface-variant hover:text-white hover:bg-white/[0.02]'
            }`}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 flex-shrink-0">
              <path d={item.icon} />
            </svg>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="border-t border-outline-variant px-unit-4 py-unit-4">
        <div className="text-label-sm text-on-surface-variant uppercase tracking-widest mb-unit-3">Connections</div>
        <Auth authStatus={authStatus} onAuthChange={onAuthChange} />
      </div>
    </div>
  )
}
