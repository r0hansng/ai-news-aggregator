'use client';

import { motion } from 'framer-motion';
import { ExternalLink, ThumbsUp, ThumbsDown, Youtube, Globe, Cpu } from 'lucide-react';

/**
 * ============================================================================
 * DigestCard — High-Fidelity Signal Visualization Component
 * ============================================================================\n *
 * **Purpose**: Render individual AI-curated signals with rich metadata,\n * visual ranking, and instant feedback controls.\n *
 * **Responsibilities**:
 * 1. **Metadata Visualization**: Display curator confidence, source, rank.\n * 2. **Visual Hierarchy**: Title > Summary > Source (scanning order).\n * 3. **Interaction State**: Optimistic feedback UI (Thumbs +/-).\n * 4. **Animation**: Smooth stagger on mount (prevent jarring layout shift).\n *\n * **Design Rationale**:
 * - **Glass-morphism Card**: bg-zinc-900/40 + border creates depth without distraction.\n * - **Rank Watermark** (#1, #2, etc.): Low-opacity, communicates ranking visually.\n * - **Source Icon**: YouTube (red) vs. Tech (CPU icon) vs. Web → instant categorization.\n * - **Hover Effects**: Subtle bg-opacity change + group-hover animations.\n *\n * **Animation Strategy** (Framer Motion):\n * - **Why Animations?**\n *   - Stream hydration can be jarring (10 items appear instantly).\n *   - Staggered entrance (delay = index * 50ms) spreads load visually.\n *   - Smooth opacity + transform: perceived performance boost.\n *   - No janky layouts: animation completes before user reads.\n *\n * - **Stagger Pattern**:\n *   ```tsx\n *   initial={{ opacity: 0, y: 20 }}           // Start off-screen\n *   animate={{ opacity: 1, y: 0 }}            // End in-place\n *   transition={{ delay: index * 0.05, duration: 0.5 }}  // Stagger + easing\n *   ```\n *   - Delay increases by 50ms per item (index 0 → 0ms, index 1 → 50ms, etc).\n *   - 10 items total: 0-500ms animation window (imperceptible to user).\n *   - All items animated before any readably content (good UX).\n *\n * **Architecture Pattern: Controlled Component**:
 * - Props-only: feedbackStatus + onFeedback callback.\n * - No internal mutations or API calls.\n * - Parent (useFeed) manages state + persistence.\n * - Card only renders optimistic UI.\n *\n * **Accessibility**:
 * - Title is semantic `<h3>` (screen readers).\n * - Button accessible: keyboard + screen reader support.\n * - Color + icon for feedback (not icon alone).\n *\n * **Performance**:
 * - O(1) render per item.\n * - Framer Motion: GPU-accelerated transforms (60fps).\n * - List rendering: React.memo recommended if list > 50 items.\n */

interface DigestItem {
  id: string;
  title: string;
  content: string;
  summary: string;
  url: string;
  rank_score: number;
  source_type: string;
  source_name: string;
  created_at: string;
}

interface DigestCardProps {
  item: DigestItem;
  index: number;
  feedbackStatus?: string;
  onFeedback: (id: string, rating: string) => void;
}

export const DigestCard = ({ item, index, feedbackStatus, onFeedback }: DigestCardProps) => {
  /**
   * ========================================================================
   * Source Icon Orchestration — Visual Signal Classification
   * ========================================================================
   *
   * **Purpose**: Immediate visual categorization of signal origin.\n   *\n   * **Mapping**:
   * - YouTube (red): Video content, creator-generated.\n   * - OpenAI/Anthropic (gray CPU): Model-derived insights, research findings.\n   * - Default (gray globe): Web articles, documentation.\n   *\n   * **Design**: Small icon (14px) in muted container → doesn't distract.\n   *\n   * **Rationale**: Users can scan source at a glance (scan + validate strategy).\n   */
  const getSourceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'youtube': return <Youtube size={14} className="text-red-500" />;
      case 'openai':
      case 'anthropic': return <Cpu size={14} className="text-zinc-400" />;
      default: return <Globe size={14} className="text-zinc-400" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.5 }}
      className="group relative bg-zinc-900/40 border border-zinc-800/50 rounded-3xl p-8 hover:bg-zinc-900/60 transition-all duration-500 overflow-hidden"
    >
      {/* Background rank-score watermark for subtle visual depth */}
      <div className="absolute top-4 right-8 text-[80px] font-black text-white/2 select-none pointer-events-none">
        #{index + 1}
      </div>

      <div className="relative z-10 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-zinc-800/50 rounded-xl">
              {getSourceIcon(item.source_type)}
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">
                {item.source_name}
              </p>
              <p className="text-[8px] uppercase tracking-widest text-zinc-600">
                {new Date(item.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onFeedback(item.id, 'positive')}
              className={`p-2 rounded-lg transition-colors ${feedbackStatus === 'positive' ? 'bg-white text-black' : 'text-zinc-500 hover:bg-zinc-800'}`}
            >
              <ThumbsUp size={14} />
            </button>
            <button
              onClick={() => onFeedback(item.id, 'negative')}
              className={`p-2 rounded-lg transition-colors ${feedbackStatus === 'negative' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:bg-zinc-800'}`}
            >
              <ThumbsDown size={14} />
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-xl md:text-2xl font-serif leading-tight text-zinc-100 group-hover:text-white transition-colors">
            {item.title}
          </h3>
          <p className="text-zinc-400 font-serif leading-relaxed line-clamp-3 text-sm md:text-base">
            {item.summary}
          </p>
        </div>

        <div className="pt-6 flex items-center justify-between border-t border-zinc-800/50">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
              <span className="text-[8px] font-bold uppercase tracking-widest text-zinc-400">Signal Strength</span>
              <span className="text-[10px] font-mono text-white">{(item.rank_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-zinc-400 hover:text-white transition-colors"
          >
            Source Original <ExternalLink size={12} />
          </a>
        </div>
      </div>
    </motion.div>
  );
};
