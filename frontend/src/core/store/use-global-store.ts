import { create } from 'zustand';

/**
 * ============================================================================
 * Global UI & Orchestration Store (Zustand)
 * ============================================================================
 *
 * **Architecture Philosophy**:
 * - **Minimal Scope**: Store only lightweight, cross-feature UI state.
 * - **Not for Server Data**: Use React Query (useAuth, useFeed) for server state.
 * - **Synchronous Access**: Zustand provides instant state without hook overhead.
 *
 * **What BELONGS in this store**:
 * - Visibility toggles: Settings drawer, mobile menu, modals.
 * - Global loading states: Full-page spinners, blocking operations.
 * - UI metadata: Active tab, sidebar collapsed state.
 * - Lightweight user branding: name, email (for navbar display).
 *
 * **What DOES NOT belong**:
 * - User profile data → Use useAuth hook (synced from backend via React Query).
 * - Signal feeds → Use useFeed hook (large dataset, polling required).
 * - Form state → Use react-hook-form (feature-scoped).
 * - Session tokens → Use cookies (secure storage, automatic refresh).
 *
 * **Integration Pattern**:
 * Zustand (client state) + React Query (server state) + Cookies (session).
 * ```
 * Client State (Zustand)  ← UI toggles, immediate feedback
 *        ↓
 * Server State (React Query) ← Data from backend, auto-synced
 *        ↓
 * Session (Cookies)  ← Auth tokens, persist across tabs
 * ```
 *
 * **Performance**:
 * - Zustand re-renders only subscribers affected by the state change.
 * - O(1) state access (direct object lookup vs. async React Query hooks).
 * - Memory: ~1KB per global state property (negligible).
 *
 * **Why Zustand over Redux?**
 * - No boilerplate (actions, reducers, middleware).
 * - Smaller bundle: ~2KB gzipped (vs Redux ~12KB).
 * - Scales to ~10-20 global props before complexity demands refactor.
 */
interface GlobalState {
  /**
   * Settings Drawer Visibility
   *
   * **Controlled by**: SettingsDrawer component, Navbar (open/close button).
   * **Subscribers**: SettingsDrawer (visible when true), Navbar (button state).
   * **Responsibility**: UI orchestration only; settings data lives in useAuth.
   */
  isSettingsOpen: boolean;
  setSettingsOpen: (open: boolean) => void;

  /**
   * Cached User Session Metadata
   *
   * **Purpose**: High-speed access to user branding (name, email, avatar).
   * **Source of Truth**: useAuth hook (synced from backend on login).
   * **Why Cache Here?**: Navbar must be instant; React Query hooks take ~100ms.
   * **Fallback**: useGlobalStore provides synchronous access.
   *
   * **Sync Strategy**:
   * 1. User logs in → useAuth hook fetches /me.
   * 2. useEffect in useAuth → setSession() updates Zustand.
   * 3. Navbar re-renders with fresh name (instant).
   * 4. Session cleared on logout.
   */
  user: {
    id: string | null;
    name: string | null;
    email: string | null;
  };
  setSession: (user: GlobalState['user']) => void;
  clearSession: () => void;
}

export const useGlobalStore = create<GlobalState>((set) => ({
  isSettingsOpen: false,
  setSettingsOpen: (open) => set({ isSettingsOpen: open }),

  user: {
    id: null,
    name: null,
    email: null,
  },
  setSession: (user) => set({ user }),
  clearSession: () => set({ user: { id: null, name: null, email: null } }),
}));
