import apiClient from '@/core/api/client';

/**
 * ============================================================================
 * Feed Feature API — Signal Ingestion & Curator Interface
 * ============================================================================
 *
 * **Purpose**: Handle fetching curated signal digests and submitting user
 * feedback to fine-tune the AI curator model.
 *
 * **Domain Model**:
 * - **Digest**: Curated batch of signals (1-10 items), ranked by relevance.
 * - **Signal**: Single content piece (article, video, research finding).
 * - **Relevance Score**: 0-100, determined by Curator Agent.
 *
 * **Caching Strategy**: Cache key = ['feed', limit].
 * - Ensures cache isolation: useFeed(10) cache ≠ useFeed(20) cache.
 * - Invalidated on: manual refresh, signal rating submission.
 *
 * **Performance Notes**:
 * - Limit typically 10 items (~2-3KB response).
 * - Polling interval: 60s (tunable in useFeed hook).
 * - Typical latency: 200-400ms from backend.
 *
 * **Integration Points**:
 * - useFeed hook: Automatic polling + cache invalidation.
 * - DigestCard component: Renders individual items.
 * - SettingsDrawer: Manual refresh trigger.
 */

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

export const feedApi = {
  /**
   * Fetch Latest Curated Signal Digest
   *
   * **Endpoint**: GET /api/v1/digests/latest?limit=10
   * **Cache Key**: ['feed', limit]
   * **Response**: { items: DigestItem[], count: number }
   *
   * **Behavior**:
   * - Returns most recently curated digest.
   * - Ranked by Curator Agent confidence.
   * - Each item includes relevance_score (0-100) + reasoning.
   *
   * **Limit Parameter**:
   * - 10 items: Recommended for Feed page (mobile-friendly, 3-4 screens).
   * - 20 items: For "load more" or power users.
   * - Larger limits increase response size (~200KB per 10 items).
   *
   * **Complexity**: O(1) network request, O(n) parsing where n = items.
   * **Typical Latency**: 200-300ms cold, 50-100ms warm (CDN cache).
   *
   * @param limit Number of signals to return (default: 10)
   * @returns Digest batch with ranked signals
   * @throws AxiosError on network failure or 401 (stale token)
   */
  getLatest: async (limit: number = 10): Promise<DigestFeedResponse> => {
    const response = await apiClient.get<DigestFeedResponse>('/api/v1/digests/latest', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Submit User Feedback on Signal Quality
   *
   * **Endpoint**: POST /api/v1/digests/{id}/feedback
   * **Body**: { rating: 'positive' | 'negative', comment?: string }
   * **Purpose**: Fine-tune Curator Agent model with explicit user ratings.
   *
   * **Ratings**:
   * - positive: User found signal useful/relevant → boost similar items.
   * - negative: Signal missed the mark → deprioritize similar sources/topics.
   *
   * **Comment Field** (optional):
   * - User can provide freeform feedback.
   * - Used for debugging curator failures.
   * - Logged for future analysis.
   *
   * **Flow** (from useFeed hook):
   * 1. User clicks Thumbs Up/Down on DigestCard.
   * 2. Optimistic update: feedback stored locally.
   * 3. submitFeedback(id, rating) called.
   * 4. Backend records feedback in audit log.
   * 5. Curator Agent uses feedback batch to retrain.
   *
   * **Complexity**: O(1) network request.
   * **Typical Latency**: ~100-200ms.
   *
   * @param digestId Unique identifier for the signal
   * @param rating Positive or negative feedback
   * @param comment Optional freeform user comment
   * @returns Acknowledgment from backend
   * @throws AxiosError on network failure
   */
  submitFeedback: async (digestId: string, rating: string, comment?: string): Promise<any> => {
    const response = await apiClient.post(`/api/v1/digests/${digestId}/feedback`, {
      rating,
      comment,
    });
    return response.data;
  },

  /**
   * Manually Trigger Backend Orchestration Engine
   *
   * **Endpoint**: POST /api/v1/orchestrate/refresh
   * **Purpose**: Force immediate re-run of signal collection + curation.
   * **Typical Use**: User clicks "Refresh" button in Feed.
   *
   * **What Happens**:
   * 1. Backend scrapes new signals from configured sources (YouTube, etc).
   * 2. Processes through Signal Processor pipeline.
   * 3. Curator Agent re-ranks existing + new signals.
   * 4. Updates digest table.
   * 5. Returns acknowledgment (refresh queued).
   *
   * **Propagation Delay**:
   * - Backend typically completes in 10-30s.
   * - useFeed hook waits 3s before refetching (allow background worker).
   * - User sees loading spinner during wait.
   *
   * **Complexity**: O(1) network request, O(k) backend processing.
   * **Typical Latency**: ~100ms API response + 10-30s processing.
   *
   * **Rate Limiting**: Backend may throttle rapid refreshes.
   * - Recommended: Show "refresh available in 30s" UI.
   *
   * @returns Acknowledgment from backend (refresh queued)
   * @throws AxiosError on network failure or rate limit
   */
  triggerRefresh: async (): Promise<any> => {
    const response = await apiClient.post('/api/v1/orchestrate/refresh');
    return response.data;
  }
};
