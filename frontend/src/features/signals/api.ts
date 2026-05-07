import apiClient from '@/core/api/client';

/**
 * ============================================================================
 * Signals Feature API — Signal Source Discovery & Resolution
 * ============================================================================
  * **Purpose**: Handle discovery and resolution of technical signal sources
 * (YouTube channels, tech publications) and user preference updates.
 *
 * **Domain Model**:
 * - **Signal Source**: Origin of tech signals (YouTube channel, blog feed).
 * - **Resolution**: Converting user input (handle) → verified channel ID.
 * - **User Preferences**: Configured interests + channel subscriptions.
 *
 * **Integration Points**:
 * - useSignals hook: Uses these endpoints for source discovery.
 * - useAuth: Cache invalidation when sources update.
 * - Onboarding flow: Initial source setup during registration.
 */

export interface ChannelInfo {
  channel_id: string;
  display_name: string;
  handle: string;
}

export const signalsApi = {
  /**
   * ========================================================================
   * Resolve YouTube Channel Handle to Channel ID
   * ========================================================================
      *
   * **Purpose**: Convert user-friendly handle (@tveskeet) to verified YouTube
   * channel_id (UCxxx...xyz). Essential for backend to scrape channel.
   *
   * **Endpoint**: GET /api/v1/signals/youtube/resolve?query={handle}
   * **Params**: { query: '@handle' or 'channel name' }
   * **Response**: { channel_id, display_name, handle }
   *
   * **Flow**:
   * 1. User enters @handle in Onboarding or Settings.
   * 2. Query sent to backend.
   * 3. Backend queries YouTube Data API → searches channels.
   * 4. Validates channel is public + has content.
   * 5. Returns verified channel_id + display info.
   * 6. Frontend stores in user's youtube_channels array.
   *
   * **Error Handling**:
   * - 404: No matching channel found → user retries with different query.
   * - 403: YouTube API quota exceeded → show "Try again later".
   * - 429: Rate limited → backoff + retry (exponential).
   *
   * **Complexity**: O(1) API call, O(k) YouTube API processing.
   * **Latency**: ~500-1000ms (YouTube API round-trip).
   * **Retry Strategy**: Manual (user resubmits query), no auto-retry.
   *
   * @param query YouTube handle (with @) or channel name
   * @returns Verified channel info { channel_id, display_name, handle }
   * @throws AxiosError on invalid query or API failure
   *
   * @example
   * const channel = await signalsApi.resolveYouTubeChannel('@tveskeet');
   * // Returns: { channel_id: 'UC...', display_name: 'Theo', handle: '@tveskeet' }
   */
  resolveYouTubeChannel: async (query: string): Promise<ChannelInfo> => {
    const response = await apiClient.get<ChannelInfo>('/api/v1/signals/youtube/resolve', {
      params: { query },
    });
    return response.data;
  },

  /**
   * ========================================================================
   * Update User's Signal Sources
   * ========================================================================
      *
   * **Endpoint**: PUT /api/v1/users/me/signals
   * **Body**: { interests: string[], youtube_channels: string[] }
   * **Purpose**: Persist user's preferred signal sources to backend.
   *
   * **Called By**:
   * - Onboarding: After user selects interests + channels (step 3-4).
   * - Settings: When user modifies sources (add/remove channels).
   *
   * **Side Effects**:
   * - Backend reindexes signal filters.
   * - All user's future digests filtered by these sources.
   * - Cache invalidation: triggers useAuth refetch.
   * - Feed digests may change based on new sources.
   *
   * **Data Transformation**:
   * - Interests: Array of strings ("machine learning", "react").
   * - YouTube channels: Array of verified channel_ids (from resolution).
   *
   * **Complexity**: O(1) network request, O(k) backend reindexing.
   * **Latency**: ~300-500ms (database write + reindex).
   *
   * @param interests User's tech topics of interest
   * @param youtubeChannels Array of verified YouTube channel_ids
   * @returns Backend acknowledgment
   * @throws AxiosError on network failure or validation error
   *
   * @example
   * await signalsApi.updateSources(
   *   ['machine-learning', 'web-development'],
   *   ['UC123...', 'UC456...']
   * );
   */
  updateSources: async (interests: string[], youtubeChannels: string[]): Promise<any> => {
    const response = await apiClient.put('/api/v1/users/me/signals', {
      interests,
      youtube_channels: youtubeChannels
    });
    return response.data;
  }
};
