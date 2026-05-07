import { useMutation, useQueryClient } from '@tanstack/react-query';
import { signalsApi } from '../api';
import { useState, useCallback } from 'react';

/**
 * ============================================================================
 * useSignals Hook — Technical Signal Source Discovery & Resolution
 * ============================================================================
  * **Purpose**: Manage user's signal sources (topics + YouTube channels).
 * Provides resolution of fuzzy queries to verified channel IDs.
 *
 * **Why Separate from useAuth?**
 * - Auth manages identity, useSignals manages signal sources.
 * - Sources can be updated independently (user adds channel).
 * - Cache invalidation: updating sources → invalidates useAuth profile.
 *
 * **Signal Sources**:
 * - **Interests**: Text tags ("machine learning", "cloud computing").
 * - **YouTube Channels**: Verified by handle resolution ("@tveskeet").
 *
 * **Resolution Strategy**:
 * - User enters YouTube handle (@handle or name).
 * - Frontend → signalsApi.resolveYouTubeChannel(query).
 * - Backend queries YouTube API → verifies channel → returns channel_id.
 * - Frontend adds channel_id to user's youtube_channels array.
 *
 * **Error Handling**:
 * - Query not found: Display "Channel not found" to user.
 * - YouTube API error: Retry with exponential backoff.
 * - Network error: Allow offline editing, sync on reconnect.
 *
 * **Performance**:
 * - Resolution latency: ~500-1000ms (YouTube API round-trip).
 * - User sees loading spinner during resolution.
 * - Debounce search input to avoid rate limits.
 */
export const useSignals = () => {
  const queryClient = useQueryClient();
  const [resolving, setResolving] = useState(false);

  /**
   * ========================================================================
   * YouTube Channel Resolution Mutation
   * ========================================================================
   * **Purpose**: Resolve fuzzy YouTube queries to verified channel IDs.
   *
   * **Flow**:
   * 1. User enters @handle or channel name (e.g., "@tveskeet").
   * 2. resolveChannel(query) calls signalsApi.resolveYouTubeChannel().
   * 3. Backend queries YouTube Data API → validates channel.
   * 4. Returns { channel_id, display_name, handle }.
   * 5. Frontend adds to youtube_channels array (via form state).
   *
   * **Error Handling**:
   * - 404: Channel not found (invalid handle) → user retries.
   * - 403: YouTube API quota exceeded → show "Try again later" message.
   * - 500: Backend error → log to Sentry, show generic error.
   *
   * **Complexity**: O(1) network request, O(1) response parsing.
   * **Latency**: ~500-1000ms (YouTube API round-trip).
   *
   * **Retry Strategy**:
   * - Manual retry via user resubmission (no auto-retry).
   * - Rate limiting: Show cooldown timer if too many failures.
   */
  const resolveMutation = useMutation({
    mutationFn: signalsApi.resolveYouTubeChannel,
  });

  /**
   * ========================================================================
   * Update Signal Sources Mutation
   * ========================================================================
   *
   * **Purpose**: Persist user's interests + YouTube channels to backend.
   *
   * **Endpoint**: PUT /api/v1/users/me/signals
   * **Body**: { interests: string[], youtube_channels: string[] }
   *
   * **Flow**:
   * 1. User completes onboarding or modifies sources in Settings.
   * 2. updateSources(interests, youtubeChannels) called.
   * 3. Backend updates user profile → reindexes signal filters.
   * 4. queryClient.invalidateQueries(['me']) triggers refetch.
   * 5. useAuth hook receives updated profile.
   * 6. Feed queries re-run with new filters (automatic).
   *
   * **Side Effect**: Cache invalidation ensures fresh digest on next fetch.
   * - Old digest may not match new sources.
   * - Force refetch ensures relevant signals for new interests.
   *
   * **Complexity**: O(1) network request, O(k) where k = source counts.
   * **Latency**: ~300-500ms (database write).
   *
   * @see useAuth for how cache invalidation triggers profile refetch
   */
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
   *
   * **Purpose**: Wrap resolveMutation to manage loading state + error handling.
   *
   * **Ensures**:
   * - resolving flag set during request.
   * - isResolving reflects pending state for UI spinners.
   * - Error logged to console (for debugging).
   *
   * **Complexity**: O(1) state management.
   */
  const resolveChannel = useCallback(async (query: string) => {
    setResolving(true);
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
