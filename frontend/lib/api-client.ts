import axios from 'axios';

/**
 * Professional Axios instance configuration.
 */
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor: Injects tokens and User ID.
 */
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const userId = localStorage.getItem('ai_news_user_id');
      const accessToken = localStorage.getItem('ai_news_access_token');
      
      if (userId) {
        config.headers['X-User-Id'] = userId;
      }
      if (accessToken) {
        config.headers['Authorization'] = `Bearer ${accessToken}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor: Handles token rotation on 401.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized and ensure we don't loop
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('ai_news_refresh_token');
        if (refreshToken) {
          // Attempt to refresh
          const response = await axios.post(`${apiClient.defaults.baseURL}/api/v1/users/refresh`, {
            refresh_token: refreshToken
          });
          
          if (response.data.access_token) {
            // Store new tokens
            localStorage.setItem('ai_news_access_token', response.data.access_token);
            localStorage.setItem('ai_news_refresh_token', response.data.refresh_token);
            
            // Retry original request
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Refresh failed, clear everything
        localStorage.removeItem('ai_news_user_id');
        localStorage.removeItem('ai_news_access_token');
        localStorage.removeItem('ai_news_refresh_token');
        if (typeof window !== 'undefined') {
          window.location.href = '/';
        }
      }
    }

    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
