import { useState, useEffect } from "react";
import axios from "axios";
import LandingPage from "./components/LandingPage";
import Dashboard from "./components/Dashboard";
import Sidebar from "./components/Sidebar";
import SyncPanel from "./components/SyncPanel";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5001";

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [authStatus, setAuthStatus] = useState({
    spotify: false,
    ytmusic: false,
  });
  const [syncStatus, setSyncStatus] = useState({
    is_running: false,
    current_task: null,
    current_playlist: null,
    added: 0,
    failed: 0,
    logs: [],
  });

  // Poll auth status
  useEffect(() => {
    if (showLanding) return;

    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/auth/status`);
        setAuthStatus(response.data);
      } catch (error) {
        console.error("Failed to check auth status:", error);
      }
    };

    checkAuth();
    const interval = setInterval(checkAuth, 5000);
    return () => clearInterval(interval);
  }, [showLanding]);

  // Poll sync status
  useEffect(() => {
    if (showLanding) return;

    const checkStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/status`);
        setSyncStatus(response.data);
      } catch (error) {
        console.error("Failed to check sync status:", error);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 1000);
    return () => clearInterval(interval);
  }, [showLanding]);

  if (showLanding) {
    return <LandingPage onGetStarted={() => setShowLanding(false)} />;
  }

  return (
    <div className="flex h-screen bg-black">
      <Sidebar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        authStatus={authStatus}
      />
      <div className="flex-1 overflow-auto">
        {currentPage === "dashboard" && <Dashboard syncStatus={syncStatus} />}
        {currentPage === "sync" && (
          <SyncPanel
            authStatus={authStatus}
            syncStatus={syncStatus}
            apiBase={API_BASE}
          />
        )}
      </div>
    </div>
  );
}

export default App;
