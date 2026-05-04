'use client';

import OnboardingForm from '@/components/OnboardingForm';

export default function Home() {
  return (
    <div className="min-h-screen bg-background selection:bg-white/5 selection:text-white">
      {/* Header */}
      <header className="px-8 py-12 max-w-6xl mx-auto flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 border border-zinc-800 rounded-sm rotate-45 flex items-center justify-center">
            <div className="w-1.5 h-1.5 bg-white rounded-full" />
          </div>
          <h1 className="text-2xl font-serif font-medium tracking-tight">AI Digest</h1>
        </div>
        <nav className="flex gap-10 text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-500">
          <a href="#" className="hover:text-white transition-colors">Archive</a>
          <a href="#" className="hover:text-white transition-colors">Manifesto</a>
        </nav>
      </header>

      <main className="px-8 py-16 max-w-6xl mx-auto">
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-24 items-start">
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
