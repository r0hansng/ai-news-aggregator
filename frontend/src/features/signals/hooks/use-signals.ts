import { useMutation, useQueryClient } from '@tanstack/react-query';
import { signalsApi } from '../api';
import { useState, useCallback } from 'react';

/**
 * ============================================================================
 * useSignals Hook — Technical Signal Source Discovery & Resolution
 * ============================================================================
 *\n * **Purpose**: Manage user's signal sources (topics + YouTube channels).\n * Provides resolution of fuzzy queries to verified channel IDs.\n *\n * **Why Separate from useAuth?**
 * - Auth manages identity, useSignals manages signal sources.\n * - Sources can be updated independently (user adds channel).\n * - Cache invalidation: updating sources → invalidates useAuth profile.\n *\n * **Signal Sources**:
 * - **Interests**: Text tags (\"machine learning\", \"cloud computing\").\n * - **YouTube Channels**: Verified by handle resolution (\"@tveskeet\").\n *\n * **Resolution Strategy**:
 * - User enters YouTube handle (@handle or name).\n * - Frontend → signalsApi.resolveYouTubeChannel(query).\n * - Backend queries YouTube API → verifies channel → returns channel_id.\n * - Frontend adds channel_id to user's youtube_channels array.\n *\n * **Error Handling**:
 * - Query not found: Display \"Channel not found\" to user.\n * - YouTube API error: Retry with exponential backoff.\n * - Network error: Allow offline editing, sync on reconnect.\n *\n * **Performance**:
 * - Resolution latency: ~500-1000ms (YouTube API round-trip).\n * - User sees loading spinner during resolution.\n * - Debounce search input to avoid rate limits.\n */
export const useSignals = () => {\n  const queryClient = useQueryClient();
  const [resolving, setResolving] = useState(false);

  /**\n   * ========================================================================
   * YouTube Channel Resolution Mutation
   * ========================================================================
   *\n   * **Purpose**: Resolve fuzzy YouTube queries to verified channel IDs.\n   *\n   * **Flow**:
   * 1. User enters @handle or channel name (e.g., \"@tveskeet\").\n   * 2. resolveChannel(query) calls signalsApi.resolveYouTubeChannel().\n   * 3. Backend queries YouTube Data API → validates channel.\n   * 4. Returns { channel_id, display_name, handle }.\n   * 5. Frontend adds to youtube_channels array (via form state).\n   *\n   * **Error Handling**:
   * - 404: Channel not found (invalid handle) → user retries.\n   * - 403: YouTube API quota exceeded → show \"Try again later\" message.\n   * - 500: Backend error → log to Sentry, show generic error.\n   *\n   * **Complexity**: O(1) network request, O(1) response parsing.\n   * **Latency**: ~500-1000ms (YouTube API round-trip).\n   *\n   * **Retry Strategy**:
   * - Manual retry via user resubmission (no auto-retry).\n   * - Rate limiting: Show cooldown timer if too many failures.\n   */
  const resolveMutation = useMutation({
    mutationFn: signalsApi.resolveYouTubeChannel,
  });

  /**
   * ========================================================================\n   * Update Signal Sources Mutation
   * ========================================================================
   *\n   * **Purpose**: Persist user's interests + YouTube channels to backend.\n   *\n   * **Endpoint**: PUT /api/v1/users/me/signals\n   * **Body**: { interests: string[], youtube_channels: string[] }\n   *\n   * **Flow**:
   * 1. User completes onboarding or modifies sources in Settings.\n   * 2. updateSources(interests, youtubeChannels) called.\n   * 3. Backend updates user profile → reindexes signal filters.\n   * 4. queryClient.invalidateQueries(['me']) triggers refetch.\n   * 5. useAuth hook receives updated profile.\n   * 6. Feed queries re-run with new filters (automatic).\n   *\n   * **Side Effect**: Cache invalidation ensures fresh digest on next fetch.\n   * - Old digest may not match new sources.\n   * - Force refetch ensures relevant signals for new interests.\n   *\n   * **Complexity**: O(1) network request, O(k) where k = source counts.\n   * **Latency**: ~300-500ms (database write).\n   *\n   * @see useAuth for how cache invalidation triggers profile refetch\n   */
  const updateSourcesMutation = useMutation({
    mutationFn: ({ interests, youtubeChannels }: { interests: string[], youtubeChannels: string[] }) => 
      signalsApi.updateSources(interests, youtubeChannels),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me'] });
    }
  });

  /**
   * ========================================================================
   * Async Resolution Handler
   * ========================================================================
   *\n   * **Purpose**: Wrap resolveMutation to manage loading state + error handling.\n   *\n   * **Ensures**:
   * - resolving flag set during request.\n   * - isResolving reflects pending state for UI spinners.\n   * - Error logged to console (for debugging).\n   *\n   * **Complexity**: O(1) state management.\n   */
  const resolveChannel = useCallback(async (query: string) => {\n    setResolving(true);
    try {
      return await resolveMutation.mutateAsync(query);
    } finally {
      setResolving(false);
    }
  }, [resolveMutation]);

  return {
    resolveChannel,
    isResolving: resolving || resolveMutation.isPending,
    updateSources: updateSourcesMutation.mutate,
    isUpdating: updateSourcesMutation.isPending,
  };
};
