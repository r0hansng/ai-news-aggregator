'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { userService } from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const isFeed = pathname === '/feed';

  const handleLogout = () => {
    userService.logout();
    router.push('/');
  };

  return (
    <div className="sticky top-0 z-[100] w-full border-b border-white/[0.05] bg-background/80 backdrop-blur-xl transition-all duration-300">
      <header className="px-8 py-4 max-w-6xl mx-auto flex justify-between items-center">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-7 h-7 border border-zinc-800 rounded-sm rotate-45 flex items-center justify-center group-hover:border-white transition-all duration-500 bg-background">
            <div className="w-1 h-1 bg-white rounded-full group-hover:scale-125 transition-transform" />
          </div>
          <h1 className="text-xl font-serif font-medium tracking-tight text-white/90 group-hover:text-white transition-colors">AI Digest</h1>
        </Link>
        
        <nav className="flex gap-8 items-center">
          {isFeed ? (
            <button 
              onClick={handleLogout}
              className="text-[9px] font-bold uppercase tracking-[0.3em] text-zinc-500 hover:text-red-400 transition-colors py-2"
            >
              Disconnect
            </button>
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
