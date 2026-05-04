import apiClient from '../api-client';

export interface SignalsResponse {
  interests: string[];
  youtube_channels: string[];
  available_interests: string[];
  available_channels: Array<{ id: string; name: string }>;
}

export const signalsService = {
  /**
   * Fetches the user's current signals and available suggestions
   */
  getSignals: async (): Promise<SignalsResponse> => {
    const response = await apiClient.get<SignalsResponse>('/api/v1/signals/');
    return response.data;
  },

  /**
   * Adds a new interest topic
   */
  addInterest: async (topic: string): Promise<SignalsResponse> => {
    const response = await apiClient.post<SignalsResponse>('/api/v1/signals/interests', { topic });
    return response.data;
  },

  /**
   * Connects a new YouTube channel
   */
  addChannel: async (channelId: string): Promise<SignalsResponse> => {
    const response = await apiClient.post<SignalsResponse>('/api/v1/signals/youtube', { channel_id: channelId });
    return response.data;
  }
};
