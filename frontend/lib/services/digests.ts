import apiClient from '../api-client';

export interface DigestItem {
  id: string;
  title: string;
  summary: string;
  url: string;
  article_type: string;
  published_at: string;
  relevance_score?: number;
  rank?: number;
  reasoning?: string;
}

export interface DigestFeedResponse {
  items: DigestItem[];
  count: number;
}

export const digestService = {
  /**
   * Fetches the latest personalized AI news feed
   */
  getLatest: async (limit: number = 10): Promise<DigestFeedResponse> => {
    const response = await apiClient.get<DigestFeedResponse>('/api/v1/digests/latest', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Submits user feedback for an article to improve future ranking
   */
  submitFeedback: async (digestId: string, rating: string, comment?: string): Promise<any> => {
    const response = await apiClient.post(`/api/v1/digests/${digestId}/feedback`, {
      rating,
      comment,
    });
    return response.data;
  },

  /**
   * Triggers a manual background refresh of the intelligence engine
   */
  triggerRefresh: async (): Promise<any> => {
    const response = await apiClient.post('/api/v1/orchestrate/refresh');
    return response.data;
  }
};
