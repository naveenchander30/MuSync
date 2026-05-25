import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5001'
const USER_ID = 'default_user'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const endpoints = {
  health: () => api.get('/api/health'),
  
  auth: {
    status: () => api.get(`/api/auth/status?user_id=${USER_ID}`),
    spotifyLogin: () => `${API_BASE}/auth/spotify/login?user_id=${USER_ID}`,
    ytmusicLogin: () => `${API_BASE}/auth/ytmusic/login?user_id=${USER_ID}`,
  },
  
  sync: {
    spotifyToYt: () => api.post('/api/sync/spotify-to-ytmusic', { user_id: USER_ID }),
    ytToSpotify: () => api.post('/api/sync/ytmusic-to-spotify', { user_id: USER_ID }),
  },
  
  jobs: {
    getById: (jobId) => api.get(`/api/jobs/${jobId}`),
    getByUser: () => api.get(`/api/jobs/user/${USER_ID}`),
  },
  
  scheduler: {
    create: (data) => api.post('/api/scheduler/create', { ...data, user_id: USER_ID }),
    getByUser: () => api.get(`/api/scheduler/jobs/${USER_ID}`),
    update: (jobId, data) => api.put(`/api/scheduler/jobs/${jobId}`, data),
    delete: (jobId) => api.delete(`/api/scheduler/jobs/${jobId}`),
  },
}

export { USER_ID, API_BASE }
