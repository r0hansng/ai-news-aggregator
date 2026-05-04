import apiClient from '../api-client';

export interface UserOnboardData {
  name: string;
  email: string;
  password: string;
  title?: string;
  background?: string;
  expertise_level?: string;
  interests?: string[];
  youtube_channels?: string[];
  preferences?: Record<string, any>;
}

export interface UserResponse {
  id: string;
  name: string;
  email: string;
  email_updates_enabled: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: UserResponse;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
  };
}

export const userService = {
  /**
   * Onboards a new user and stores their session tokens
   */
  onboard: async (data: UserOnboardData): Promise<UserResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/users/onboard', data);
    
    const { user, tokens } = response.data;
    
    // Persist session
    if (user.id) {
      localStorage.setItem('ai_news_user_id', user.id);
      localStorage.setItem('ai_news_access_token', tokens.access_token);
      localStorage.setItem('ai_news_refresh_token', tokens.refresh_token);
    }
    
    return user;
  },

  /**
   * Login an existing user and stores their session tokens
   */
  login: async (email: string, password: string): Promise<UserResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/users/login', { email, password });
    
    const { user, tokens } = response.data;
    
    // Persist session
    if (user.id) {
      localStorage.setItem('ai_news_user_id', user.id);
      localStorage.setItem('ai_news_access_token', tokens.access_token);
      localStorage.setItem('ai_news_refresh_token', tokens.refresh_token);
    }
    
    return user;
  },

  /**
   * Clears the current user session
   */
  logout: () => {
    localStorage.removeItem('ai_news_user_id');
    localStorage.removeItem('ai_news_access_token');
    localStorage.removeItem('ai_news_refresh_token');
  },

  /**
   * Fetches the current user profile
   */
  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/api/v1/users/me');
    return response.data;
  },

  /**
   * Updates the user's preference for receiving email updates
   */
  updateEmailPreference: async (enabled: boolean): Promise<UserResponse> => {
    const response = await apiClient.post<UserResponse>(`/api/v1/users/preferences/email?enabled=${enabled}`);
    return response.data;
  },

  /**
   * Manually triggers a digest email
   */
  triggerManualDigest: async (): Promise<{ message: string }> => {
    const response = await apiClient.post<{ message: string }>('/api/v1/users/send-digest');
    return response.data;
  }
};
