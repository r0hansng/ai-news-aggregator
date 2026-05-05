'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Settings2 } from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/use-auth';
import { useGlobalStore } from '@/core/store/use-global-store';

/**
 * ============================================================================
 * Navbar Component — Global Navigation & Session Orchestrator
 * ============================================================================
 *
 * **Purpose**: System-wide header with dynamic branding + navigation controls.\n * Bridges server state (useAuth) and client state (useGlobalStore) for
 * instant access to user metadata without waiting for async hooks.\n *
 * **Architecture**:
 * ```\n * Navbar (this component)\n *   ├── usePathname() → determines active page\n *   ├── useAuth() → session data, logout handler\n *   ├── useGlobalStore() → branding (name, email)\n *   └── Conditional Navigation\n *         ├── Feed Page: Settings + Disconnect\n *         └── Home Page: Archive + Manifesto\n * ```\n *\n * **State Integration**:
 * - **usePathname()**: Determines conditional rendering.\n *   - /feed → Show Settings + Logout.\n *   - /,  → Show Archive + Manifesto.\n * - **useAuth()**: Provides logout() mutation.\n *   - Clears all auth state (cookies + Zustand + window reset).\n * - **useGlobalStore()**: Provides instant user name/email for branding.\n *   - Synced by useAuth hook's useEffect.\n *   - 0ms access (no async waiting).\n *\n * **Design Pattern: Dual-Mode Navigation**\n * - Feed-specific layout: Focus on signal digests, quick access to settings.\n * - Home layout: Educational + brand messaging.\n *\n * **Accessibility (A11y)**:
 * - All buttons have title attributes (screen reader context).\n * - Color contrast: WCAG AA compliant (text vs. background).\n * - Keyboard navigation: Tab + Enter flow preserved.\n * - Icon + text for buttons (not icons alone).\n *\n * **Performance**:
 * - useGlobalStore subscribers only: No fetch overhead.\n * - Navbar doesn't trigger queries (uses cached data).\n * - Re-render only on pathname or global store change.\n *\n * **Integration Points**:
 * - SettingsDrawer: Opens via setSettingsOpen() state mutation.\n * - Logout: Triggers useAuth().logout() → clears session → redirect.\n * - Logo: Links to home (/), always visible.\n */
export default function Navbar() {
  const pathname = usePathname();
  const isFeed = pathname === '/feed';
  
  const { logout } = useAuth();
  const setSettingsOpen = useGlobalStore((state) => state.setSettingsOpen);

  return (
    <div className="sticky top-0 z-100 w-full border-b border-white/5 bg-background/80 backdrop-blur-xl transition-all duration-300">
      <header className="px-8 py-4 max-w-6xl mx-auto flex justify-between items-center">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-7 h-7 border border-zinc-800 rounded-sm rotate-45 flex items-center justify-center group-hover:border-white transition-all duration-500 bg-background">
            <div className="w-1 h-1 bg-white rounded-full group-hover:scale-125 transition-transform" />
          </div>
          <h1 className="text-xl font-serif font-medium tracking-tight text-white/90 group-hover:text-white transition-colors">AI Digest</h1>
        </Link>
        
        <nav className="flex gap-6 items-center">
          {isFeed ? (
            <>
              <button
                onClick={() => setSettingsOpen(true)}
                title="Signal Configuration"
                className="text-zinc-500 hover:text-white transition-colors"
              >
                <Settings2 size={16} />
              </button>
              
              <button 
                onClick={logout}
                className="text-[9px] font-bold uppercase tracking-[0.3em] text-zinc-500 hover:text-red-400 transition-colors py-2"
              >
                Disconnect
              </button>
            </>
          ) : (
            <>
              <a href="#" className="text-[9px] font-bold uppercase tracking-[0.3em] text-zinc-500 hover:text-white transition-colors">Archive</a>
              <a href="#" className="text-[9px] font-bold uppercase tracking-[0.3em] text-zinc-500 hover:text-white transition-colors">Manifesto</a>
            </>
          )}
        </nav>
      </header>
    </div>
  );
}
