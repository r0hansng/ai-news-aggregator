import apiClient from '@/core/api/client';
import Cookies from 'js-cookie';

/**
 * ============================================================================
 * Auth Feature API — Authentication Service Layer
 * ============================================================================
 *
 * **Responsibility**: Implements authentication workflows (login, registration,
 * session initialization) with automatic token persistence to cookies.
 *
 * **Token Lifecycle**:
 * 1. User submits credentials → POST /api/v1/users/token
 * 2. Backend validates, returns access_token + refresh_token
 * 3. This layer persists both to cookies (7-day expiry)
 * 4. apiClient request interceptor automatically injects Bearer token
 * 5. When access_token expires (401), automatic refresh via refresh_token
 *
 * **Why Cookies for Token Storage?**
 * - Persists across page reloads (localStorage alternative would lose on crash).
 * - SameSite=Strict prevents CSRF token leakage.
 * - Browser automatically attaches to requests (no manual header injection).
 * - More secure than localStorage (resistant to certain XSS vectors).
 *
 * **Integration Flow**:
 * authApi.login() → sets cookies → apiClient injects headers → backend validates
 *
 * **Security Notes**:
 * - Refresh token never sent to frontend in future requests (only access token).
 * - Tokens expire independently: access (short-lived) vs refresh (long-lived).
 * - On logout, both tokens wiped via clearSession() in useAuth hook.
 */

export const authApi = {
  /**
   * Login with Email & Password
   *
   * **Endpoint**: POST /api/v1/users/token
   * **Body**: { username: email, password: password }
   * **Returns**: { access_token, refresh_token, user_id }
   *
   * **Side Effects**:
   * - Sets ai_news_access_token cookie (7-day expiry)
   * - Sets ai_news_refresh_token cookie (7-day expiry)
   * - Sets ai_news_user_id cookie for X-User-Id header injection
   *
   * **Complexity**: O(1) cookie write, O(1) network request
   *
   * @param email User email (used as username for OAuth2 flow)
   * @param password User password (never stored, only sent for auth)
   * @returns Backend response with tokens and user metadata
   * @throws AxiosError on invalid credentials or network failure
   */
  login: async (email: string, password: string): Promise<any> => {
    const response = await apiClient.post('/api/v1/users/token', {
      username: email,
      password: password
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    if (response.data.access_token) {
      Cookies.set('ai_news_access_token', response.data.access_token, { expires: 7 });
      Cookies.set('ai_news_refresh_token', response.data.refresh_token, { expires: 7 });
      Cookies.set('ai_news_user_id', response.data.user_id, { expires: 7 });
    }
    return response.data;
  },

  /**
   * Onboard New User with Profile & Preferences
   *
   * **Endpoint**: POST /api/v1/users/onboard
   * **Body**: { name, email, password, interests, youtube_channels, preferences }
   * **Returns**: { id, name, email, ... } (full user object)
   *
   * **Side Effects**:
   * - Creates user in database
   * - Sets ai_news_user_id cookie for subsequent requests
   * - Does NOT set access_token (user must login separately)
   * - TODO: Consider returning token from backend to auto-login
   *
   * **Flow**:
   * 1. Onboarding form → useOnboardingForm collects data
   * 2. Submits to authApi.onboard()
   * 3. Backend creates user, returns user object
   * 4. Frontend sets user ID cookie
   * 5. User must call authApi.login() to get tokens
   * 6. Redirect to /feed on successful login
   *
   * **Complexity**: O(1) network request, O(k) where k = array lengths
   *
   * @param data Full onboarding payload including interests and channels
   * @returns User object with id (used to set cookie)
   * @throws AxiosError on validation failure or email already registered
   */
  onboard: async (data: any): Promise<any> => {
    const response = await apiClient.post('/api/v1/users/onboard', data);
    if (response.data.id) {
       Cookies.set('ai_news_user_id', response.data.id, { expires: 7 });
    }
    return response.data;
  }
};
