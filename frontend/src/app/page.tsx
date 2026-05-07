/**
 * @file Home Page Component
 * @module app/page
 * @description The entry point of the AI News Aggregator. Handles landing page
 * rendering and session-based redirection to the feed.
 */

'use client';

import dynamic from 'next/dynamic';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import Navbar from '@/shared/components/layout/Navbar';

/**
 * OnboardingForm - Dynamic Import
 * @description We use dynamic loading for the onboarding form to reduce the
 * initial bundle size and ensure hydration consistency for client-side state.
 */
const OnboardingForm = dynamic(() => import('@/features/onboarding/components/OnboardingForm'), {
  loading: () => <div className="h-[400px] flex items-center justify-center text-zinc-600 animate-pulse uppercase tracking-widest text-[10px] font-bold">Loading System...</div>,
  ssr: false
});

/**
 * Home Component
 * @returns {JSX.Element} The landing page UI with onboarding entry.
 */
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirection Logic: If a user session is detected in the cookies,
    // bypass the onboarding landing page and navigate directly to the feed.
    const userId = Cookies.get('ai_news_user_id');
    if (userId) {
      router.push('/feed');
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background selection:bg-white/5 selection:text-white">
      <Navbar />

      <main className="px-8 py-16 max-w-6xl mx-auto min-h-[calc(100vh-200px)] flex items-center">
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-24 items-center w-full">
          <div className="lg:col-span-6 space-y-12">
            <div className="space-y-6">
              <h2 className="text-5xl md:text-7xl font-serif leading-[1.1] text-white">
                Quiet intelligence <br />
                for a noisy world.
              </h2>
              <p className="text-zinc-500 leading-relaxed font-serif text-xl max-w-lg">
                A technical lens for the AI era. We synthesize the global research stream into a singular, high-integrity signal tailored to your expertise.
              </p>
            </div>
          </div>

          <div className="lg:col-span-6 bg-white/[0.01] p-12 border border-zinc-900 rounded-3xl shadow-2xl relative overflow-hidden">
            <div className="mb-12">
              <h3 className="text-xs uppercase tracking-[0.4em] font-bold text-zinc-600 mb-4">Initialize Configuration</h3>
              <p className="text-sm text-zinc-400 font-serif">Specify your parameters below.</p>
            </div>
            <OnboardingForm />
          </div>
        </section>
      </main>

      <footer className="px-8 py-20 max-w-6xl mx-auto border-t border-zinc-900 flex justify-between items-center text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-600">
        <p>© 2026 AI Digest System.</p>
      </footer>
    </div>
  );
}
