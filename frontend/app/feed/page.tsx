'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { digestService, userService, DigestItem } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import Navbar from '@/components/Navbar';
import { Loader } from '@/components/ui/Loader';
import { RefreshCw, ExternalLink, MessageSquare, Check, X, Shield, Clock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function FeedPage() {
  const router = useRouter();
  const [digests, setDigests] = useState<DigestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [feedbackStatus, setFeedbackStatus] = useState<Record<string, string>>({});
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  const fetchFeed = async () => {
    try {
      setLoading(true);
      const data = await digestService.getLatest(10);
      setDigests(data.items);
      
      // Fetch user profile to get email preference
      try {
        const user = await userService.getMe();
        setEmailEnabled(user.email_updates_enabled);
      } catch (e) {
        console.error('Failed to fetch user preferences:', e);
      }
    } catch (error) {
      console.error('Failed to fetch feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEmail = async (enabled: boolean) => {
    setEmailLoading(true);
    try {
      await userService.updateEmailPreference(enabled);
      setEmailEnabled(enabled);
    } catch (error) {
      console.error('Failed to update email preference:', error);
    } finally {
      setEmailLoading(false);
    }
  };

  useEffect(() => {
    // Check if user is onboarded
    const userId = localStorage.getItem('ai_news_user_id');
    if (!userId) {
      router.push('/');
      return;
    }
    fetchFeed();
  }, [router]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await digestService.triggerRefresh();
      // Wait a bit then fetch
      setTimeout(fetchFeed, 3000);
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleFeedback = async (id: string, rating: string) => {
    try {
      await digestService.submitFeedback(id, rating);
      setFeedbackStatus({ ...feedbackStatus, [id]: rating });
    } catch (error) {
      console.error('Feedback failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center space-y-6">
        <Loader size="lg" color="white" />
        <p className="text-zinc-400 font-serif text-sm tracking-wide animate-pulse">Synthesizing your technical signal...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white selection:bg-white/5">
      <Navbar />

      <div className="max-w-4xl mx-auto px-6 flex items-center justify-end py-6">
        <div className="flex items-center gap-4 border-r border-zinc-800 pr-6 mr-6">
          <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Email Updates</span>
          <button 
            onClick={() => handleToggleEmail(!emailEnabled)}
            disabled={emailLoading}
            className={`relative w-8 h-4 rounded-full transition-colors ${emailEnabled ? 'bg-emerald-500/50' : 'bg-zinc-800'}`}
          >
            <motion.div 
              animate={{ x: emailEnabled ? 18 : 2 }}
              initial={false}
              className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full ${emailEnabled ? 'bg-emerald-400' : 'bg-zinc-500'}`}
            />
          </button>
          {emailEnabled && (
            <button 
              onClick={() => userService.triggerManualDigest()}
              className="text-[9px] font-bold uppercase tracking-tighter text-zinc-600 hover:text-emerald-400 transition-colors ml-1"
            >
              Send Test
            </button>
          )}
        </div>

        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className={`text-zinc-500 hover:text-white transition-colors flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest`}
        >
          {refreshing ? <Loader size="sm" /> : <RefreshCw size={12} />}
          {refreshing ? 'Syncing Signal' : 'Refresh Engine'}
        </button>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {digests.length === 0 ? (
          <div className="text-center py-32 space-y-6">
            <div className="w-16 h-16 bg-white/[0.02] border border-zinc-900 rounded-2xl mx-auto flex items-center justify-center text-zinc-700">
              <Clock size={32} />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-serif">Signal Initializing</h3>
              <p className="text-zinc-500 max-w-sm mx-auto">Your feed is being calibrated. Click refresh to trigger the background scraping engine.</p>
            </div>
            <Button onClick={handleRefresh} variant="secondary" className="px-8">
              Trigger Engine Refresh
            </Button>
          </div>
        ) : (
          <div className="space-y-12">
            <AnimatePresence>
              {digests.map((item, index) => (
                <motion.article 
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="group relative"
                >
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
                    {/* Rank & Score */}
                    <div className="md:col-span-1 pt-1 hidden md:block">
                      <div className="text-[10px] font-bold text-zinc-600 uppercase tracking-tighter mb-1">Rank</div>
                      <div className="text-2xl font-serif text-white/40 group-hover:text-white transition-colors">
                        {String(index + 1).padStart(2, '0')}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="md:col-span-11 space-y-6">
                      <div className="space-y-3">
                        <div className="flex items-center gap-3">
                          <span className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-[9px] font-bold uppercase tracking-widest text-zinc-400">
                            {item.article_type}
                          </span>
                          <span className="text-[10px] text-zinc-600 font-medium">
                            {new Date(item.published_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                          </span>
                        </div>
                        <h2 className="text-2xl md:text-3xl font-serif leading-tight text-zinc-100 group-hover:text-white transition-colors">
                          <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-3">
                            {item.title}
                            <ExternalLink size={16} className="opacity-0 group-hover:opacity-100 transition-opacity text-zinc-600" />
                          </a>
                        </h2>
                        <p className="text-zinc-500 font-serif text-lg leading-relaxed line-clamp-3">
                          {item.summary}
                        </p>
                      </div>

                      {/* AI Curation Context */}
                      {item.reasoning && (
                        <div className="bg-white/[0.02] border border-zinc-900 rounded-2xl p-5 space-y-3">
                          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">
                            <Shield size={12} className="text-emerald-500/50" />
                            Curator Reasoning
                          </div>
                          <p className="text-zinc-400 text-sm leading-relaxed italic">
                            "{item.reasoning}"
                          </p>
                          <div className="flex items-center gap-4 pt-2">
                             <div className="flex-1 h-[1px] bg-zinc-900" />
                             <div className="flex items-center gap-2">
                               <button 
                                 onClick={() => handleFeedback(item.id, 'relevant')}
                                 className={`p-2 rounded-lg transition-colors ${feedbackStatus[item.id] === 'relevant' ? 'bg-emerald-500/10 text-emerald-400' : 'hover:bg-white/5 text-zinc-600 hover:text-emerald-400'}`}
                               >
                                 <Check size={16} />
                               </button>
                               <button 
                                 onClick={() => handleFeedback(item.id, 'irrelevant')}
                                 className={`p-2 rounded-lg transition-colors ${feedbackStatus[item.id] === 'irrelevant' ? 'bg-red-500/10 text-red-400' : 'hover:bg-white/5 text-zinc-600 hover:text-red-400'}`}
                               >
                                 <X size={16} />
                               </button>
                             </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.article>
              ))}
            </AnimatePresence>
          </div>
        )}
      </main>

      <footer className="max-w-4xl mx-auto px-6 py-24 border-t border-zinc-900 text-center">
        <p className="text-[10px] font-bold uppercase tracking-[0.4em] text-zinc-600">End of Current Signal</p>
      </footer>
    </div>
  );
}
