'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, User, Settings, LogOut, ChevronRight } from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/use-auth';

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  profile: any;
}

export const SettingsDrawer = ({ isOpen, onClose, profile }: SettingsDrawerProps) => {
  const { logout } = useAuth();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[200]"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full max-w-md bg-zinc-950 border-l border-zinc-900 z-[201] p-8 shadow-2xl flex flex-col"
          >
            <div className="flex items-center justify-between mb-12">
              <div className="space-y-1">
                <h2 className="text-xl font-serif text-white">Signal Configuration</h2>
                <p className="text-xs uppercase tracking-[0.2em] text-zinc-600 font-bold">System Parameters</p>
              </div>
              <button 
                onClick={onClose}
                className="p-2 hover:bg-white/5 rounded-full transition-colors text-zinc-500"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 space-y-12 overflow-y-auto pr-4 scrollbar-hide">
              {/* User Profile Section */}
              <section className="space-y-6">
                <div className="flex items-center gap-4 p-4 bg-white/[0.02] border border-zinc-900 rounded-2xl">
                  <div className="w-12 h-12 bg-zinc-900 rounded-xl flex items-center justify-center text-zinc-500">
                    <User size={24} />
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{profile?.name || 'User Profile'}</h4>
                    <p className="text-xs text-zinc-500">{profile?.email}</p>
                  </div>
                </div>

                <div className="space-y-4">
                   <div className="group flex items-center justify-between p-4 hover:bg-white/[0.02] rounded-2xl transition-colors cursor-pointer border border-transparent hover:border-zinc-900">
                      <div className="flex items-center gap-4">
                        <Settings size={18} className="text-zinc-600" />
                        <span className="text-sm text-zinc-400">Professional Context</span>
                      </div>
                      <ChevronRight size={14} className="text-zinc-800" />
                   </div>
                </div>
              </section>

              {/* Signals Section */}
              <section className="space-y-4">
                <h3 className="text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-600">Signal Filters</h3>
                <div className="space-y-2">
                  {profile?.interests?.map((interest: string) => (
                    <div key={interest} className="px-4 py-3 bg-zinc-900/50 border border-zinc-900 rounded-xl text-sm text-zinc-400 flex items-center justify-between">
                      {interest}
                      <div className="w-1 h-1 bg-emerald-500 rounded-full" />
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <div className="pt-8 mt-auto border-t border-zinc-900">
              <button 
                onClick={logout}
                className="w-full flex items-center justify-center gap-3 py-4 text-zinc-500 hover:text-red-400 transition-colors text-xs font-bold uppercase tracking-widest bg-zinc-900/50 rounded-2xl"
              >
                <LogOut size={14} />
                Terminate Session
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
