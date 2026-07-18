import axios from 'axios';

const api = axios.create({
  // VITE_API_BASE_URL should be set for production deployments (e.g. https://api.yourdomain.com/api/v1).
  // For local dev, the Vite proxy rewrites /api -> http://127.0.0.1:8000, so the default is fine.
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 120000, // Increased to 120s to support long-running eval endpoints
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('adminToken');
      // If we are on the admin page, reload to trigger login
      if (window.location.pathname.startsWith('/admin')) {
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
