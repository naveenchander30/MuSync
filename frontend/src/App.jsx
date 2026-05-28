import { useState, useEffect } from 'react'
import { endpoints, USER_ID } from './api'
import Dashboard from './components/Dashboard'
import Sidebar from './components/Sidebar'
import SyncPanel from './components/SyncPanel'
import SchedulerManager from './components/SchedulerManager'
import LandingPage from './components/LandingPage'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [showLanding, setShowLanding] = useState(true)
  const [authStatus, setAuthStatus] = useState({
    spotify: false,
    ytmusic: false,
  })

  const checkAuth = async () => {
    try {
      const response = await endpoints.auth.status()
      const status = response.data
      setAuthStatus(status)
      if (status.spotify || status.ytmusic) {
        setShowLanding(false)
      }
    } catch (error) {
      console.error('Failed to check auth status:', error)
    }
  }

  useEffect(() => {
    checkAuth()
    const interval = setInterval(checkAuth, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const authSuccess = params.get('auth')
    const userId = params.get('user_id')
    if (authSuccess && userId === USER_ID) {
      window.history.replaceState({}, document.title, '/')
      checkAuth()
    }
  }, [])

  if (showLanding) {
    return <LandingPage onGetStarted={() => setShowLanding(false)} />
  }

  return (
    <div className="flex h-screen bg-black">
      <Sidebar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        authStatus={authStatus}
      />
      <div className="flex-1 overflow-auto">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'sync' && <SyncPanel authStatus={authStatus} />}
        {currentPage === 'scheduler' && <SchedulerManager />}
      </div>
    </div>
  )
}

export default App
