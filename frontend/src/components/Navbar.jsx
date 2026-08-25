import React from 'react';
import { Network, Sun, Moon, BookOpen, Terminal } from 'lucide-react';

export default function Navbar({ isDark, onToggleTheme, onOpenExplainer }) {
  return (
    <header className="border-b border-cyber-border/70 bg-[#0e1424]/90 dark:bg-[#0b0f19]/90 backdrop-blur-md sticky top-0 z-50 transition-colors shadow-lg shadow-black/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo & Title in Press Start 2P Pixel Font */}
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 text-white flex items-center justify-center shadow-lg shadow-violet-500/25 border border-cyan-400/30">
            <Network className="w-5 h-5 text-cyan-200" />
          </div>
          <div>
            <span className="font-pixel text-xs sm:text-sm tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-violet-300 to-purple-400">
              WEBTRACE
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          
          {/* DSA Guide Pill Button */}
          <button
            onClick={onOpenExplainer}
            className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-1.5 rounded-full bg-cyber-surface/80 hover:bg-cyber-card text-cyan-300 border border-cyan-500/40 hover:border-cyan-400 transition shadow-sm shadow-cyan-500/10"
          >
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>DSA Guide</span>
          </button>

          {/* Light / Dark Mode Toggle Button */}
          <button 
            onClick={onToggleTheme}
            title={isDark ? "Switch to Light mode" : "Switch to Dark mode"}
            className="p-2 rounded-full text-zinc-400 hover:text-cyan-300 bg-cyber-surface hover:bg-cyber-card transition border border-cyber-border shadow-sm"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-cyan-400" />}
          </button>
        </div>

      </div>
    </header>
  );
}
