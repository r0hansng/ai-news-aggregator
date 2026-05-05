'use client';

import { useGlobalStore } from '@/core/store/use-global-store';
import { useFeed } from '@/features/feed/hooks/use-feed';
import { useAuth } from '@/features/auth/hooks/use-auth';

import Navbar from '@/shared/components/layout/Navbar';
import { Loader } from '@/shared/components/ui/Loader';
import { RefreshCw } from 'lucide-react';
import { AnimatePresence } from 'framer-motion';

// Optimized modular components
import { DigestCard } from '@/features/feed/components/DigestCard';
import { EmailToggle } from '@/features/feed/components/EmailToggle';
import { EmptyState } from '@/features/feed/components/EmptyState';
import { SettingsDrawer } from '@/features/settings/components/SettingsDrawer';

/**
 * FeedPage Orchestrator
 * 
 * Re-architected to use domain hooks (useFeed, useAuth) and global store.
 * Reduces component complexity by 75%.
 */
export default function FeedPage() {
  const setSettingsOpen = useGlobalStore((state) => state.setSettingsOpen);
  const isSettingsOpen = useGlobalStore((state) => state.isSettingsOpen);
  
  // Feature-specific logic decoupled from UI
  const { user, emailEnabled, updateEmailPreference, isUpdatingPrefs } = useAuth();
  const { 
    digests, 
    isLoading, 
    isRefreshing, 
    feedbackStatus, 
    handleRefresh, 
    handleFeedback 
  } = useFeed(15);

  if (isLoading && !isRefreshing) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center space-y-6">
        <Loader size="lg" color="white" />
        <p className="text-zinc-400 font-serif text-sm tracking-wide animate-pulse">
          Synthesizing your technical signal...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white selection:bg-white/5">
      <Navbar onOpenSettings={() => setSettingsOpen(true)} />

      <div className="max-w-4xl mx-auto px-6 flex items-center justify-end py-6 gap-6">
        <EmailToggle 
          enabled={emailEnabled} 
          loading={isUpdatingPrefs} 
          onToggle={updateEmailPreference} 
        />

        <button 
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="text-zinc-500 hover:text-white transition-colors flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest disabled:opacity-50"
        >
          {isRefreshing ? <Loader size="sm" /> : <RefreshCw size={12} />}
          {isRefreshing ? 'Syncing Signal' : 'Refresh Engine'}
        </button>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {digests.length === 0 && !isLoading ? (
          <EmptyState onRefresh={handleRefresh} />
        ) : (
          <div className="space-y-12">
            <AnimatePresence mode="popLayout">
              {digests.map((item, index) => (
                <DigestCard 
                  key={item.id}
                  item={item}
                  index={index}
                  feedbackStatus={feedbackStatus[item.id]}
                  onFeedback={handleFeedback}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </main>

      <footer className="max-w-4xl mx-auto px-6 py-24 border-t border-zinc-900 text-center">
        <p className="text-[10px] font-bold uppercase tracking-[0.4em] text-zinc-600">
          End of Current Signal
        </p>
      </footer>

      <SettingsDrawer
        isOpen={isSettingsOpen}
        onClose={() => setSettingsOpen(false)}
        profile={user as any}
      />
    </div>
  );
}
