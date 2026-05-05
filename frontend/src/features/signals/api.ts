import apiClient from '@/core/api/client';

/**
 * ============================================================================
 * Signals Feature API — Signal Source Discovery & Resolution
 * ============================================================================
 *\n * **Purpose**: Handle discovery and resolution of technical signal sources\n * (YouTube channels, tech publications) and user preference updates.\n *\n * **Domain Model**:
 * - **Signal Source**: Origin of tech signals (YouTube channel, blog feed).\n * - **Resolution**: Converting user input (handle) → verified channel ID.\n * - **User Preferences**: Configured interests + channel subscriptions.\n *\n * **Integration Points**:\n * - useSignals hook: Uses these endpoints for source discovery.\n * - useAuth: Cache invalidation when sources update.\n * - Onboarding flow: Initial source setup during registration.\n */

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
   *\n   * **Purpose**: Convert user-friendly handle (@tveskeet) to verified YouTube\n   * channel_id (UCxxx...xyz). Essential for backend to scrape channel.\n   *\n   * **Endpoint**: GET /api/v1/signals/youtube/resolve?query={handle}\n   * **Params**: { query: '@handle' or 'channel name' }\n   * **Response**: { channel_id, display_name, handle }\n   *\n   * **Flow**:
   * 1. User enters @handle in Onboarding or Settings.\n   * 2. Query sent to backend.\n   * 3. Backend queries YouTube Data API → searches channels.\n   * 4. Validates channel is public + has content.\n   * 5. Returns verified channel_id + display info.\n   * 6. Frontend stores in user's youtube_channels array.\n   *\n   * **Error Handling**:
   * - 404: No matching channel found → user retries with different query.\n   * - 403: YouTube API quota exceeded → show \"Try again later\".\n   * - 429: Rate limited → backoff + retry (exponential).\n   *\n   * **Complexity**: O(1) API call, O(k) YouTube API processing.\n   * **Latency**: ~500-1000ms (YouTube API round-trip).\n   * **Retry Strategy**: Manual (user resubmits query), no auto-retry.\n   *\n   * @param query YouTube handle (with @) or channel name\n   * @returns Verified channel info { channel_id, display_name, handle }\n   * @throws AxiosError on invalid query or API failure\n   *\n   * @example\n   * const channel = await signalsApi.resolveYouTubeChannel('@tveskeet');\n   * // Returns: { channel_id: 'UC...', display_name: 'Theo', handle: '@tveskeet' }\n   */
  resolveYouTubeChannel: async (query: string): Promise<ChannelInfo> => {\n    const response = await apiClient.get<ChannelInfo>('/api/v1/signals/youtube/resolve', {\n      params: { query },\n    });\n    return response.data;\n  },

  /**
   * ========================================================================
   * Update User's Signal Sources
   * ========================================================================
   *\n   * **Endpoint**: PUT /api/v1/users/me/signals\n   * **Body**: { interests: string[], youtube_channels: string[] }\n   * **Purpose**: Persist user's preferred signal sources to backend.\n   *\n   * **Called By**:
   * - Onboarding: After user selects interests + channels (step 3-4).\n   * - Settings: When user modifies sources (add/remove channels).\n   *\n   * **Side Effects**:
   * - Backend reindexes signal filters.\n   * - All user's future digests filtered by these sources.\n   * - Cache invalidation: triggers useAuth refetch.\n   * - Feed digests may change based on new sources.\n   *\n   * **Data Transformation**:
   * - Interests: Array of strings (\"machine learning\", \"react\").\n   * - YouTube channels: Array of verified channel_ids (from resolution).\n   *\n   * **Complexity**: O(1) network request, O(k) backend reindexing.\n   * **Latency**: ~300-500ms (database write + reindex).\n   *\n   * @param interests User's tech topics of interest\n   * @param youtubeChannels Array of verified YouTube channel_ids\n   * @returns Backend acknowledgment\n   * @throws AxiosError on network failure or validation error\n   *\n   * @example\n   * await signalsApi.updateSources(\n   *   ['machine-learning', 'web-development'],\n   *   ['UC123...', 'UC456...']\n   * );\n   */
  updateSources: async (interests: string[], youtubeChannels: string[]): Promise<any> => {\n    const response = await apiClient.put('/api/v1/users/me/signals', {\n      interests,\n      youtube_channels: youtubeChannels\n    });\n    return response.data;\n  }\n};
