import React, { useState } from 'react';
import { Compass, Globe, Play, Cpu } from 'lucide-react';

export default function CrawlForm({ onStartCrawl, isLoading }) {
  const [seedUrl, setSeedUrl] = useState('https://example.com/');
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(10);
  const [delay, setDelay] = useState(0.5);
  const [respectRobots, setRespectRobots] = useState(true);
  const [dryRun, setDryRun] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!seedUrl) return;
    onStartCrawl({
      seed: seedUrl,
      max_depth: Number(maxDepth),
      max_pages: Number(maxPages),
      delay: Number(delay),
      respect_robots: respectRobots,
      dry_run: dryRun,
    });
  };

  const handlePreset = (url) => {
    setSeedUrl(url);
  };

  return (
    <section className="relative overflow-hidden bg-cyber-card/90 border border-cyber-border rounded-2xl p-6 shadow-xl backdrop-blur-md transition-all">
      
      {/* Decorative Circuit Board Accents */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-violet-500/10 to-cyan-500/10 rounded-full blur-2xl pointer-events-none" />
      <div className="absolute top-4 right-4 flex items-center gap-1.5 opacity-40 text-cyan-400 font-pixel text-[9px] pointer-events-none">
        <span>+</span><span>+</span><span>+</span>
      </div>

      <div className="mb-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-pixel text-[11px] text-cyan-400 tracking-wide uppercase flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-violet-400" />
              CRAWL CONTROLLER
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Define domain seed and exploration constraints for Breadth-First Search.
          </p>
        </div>
        
        {/* Quick Presets with Cyan Pill Style */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400 font-medium text-xs">Presets:</span>
          <button 
            type="button" 
            onClick={() => handlePreset('https://example.com/')} 
            className="px-3 py-1 rounded-full bg-cyan-950/40 hover:bg-cyan-900/60 text-cyan-300 font-mono text-[11px] transition border border-cyan-500/30 hover:border-cyan-400 shadow-sm"
          >
            example.com
          </button>
          <button 
            type="button" 
            onClick={() => handlePreset('https://quotes.toscrape.com/')} 
            className="px-3 py-1 rounded-full bg-cyan-950/40 hover:bg-cyan-900/60 text-cyan-300 font-mono text-[11px] transition border border-cyan-500/30 hover:border-cyan-400 shadow-sm"
          >
            quotes.toscrape.com
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
          
          {/* Target Seed URL */}
          <div className="md:col-span-6">
            <label htmlFor="seedUrl" className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Seed URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-cyan-400">
                <Globe className="w-4 h-4" />
              </div>
              <input 
                type="url" 
                id="seedUrl" 
                required 
                placeholder="https://example.com/" 
                value={seedUrl}
                onChange={(e) => setSeedUrl(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-sm text-slate-100 placeholder-slate-500 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-400/50 transition shadow-inner"
              />
            </div>
          </div>

          {/* Max Depth */}
          <div className="md:col-span-2">
            <label htmlFor="maxDepth" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Max Depth</span>
              <span className="text-[10px] text-cyan-400 font-mono">Hops</span>
            </label>
            <input 
              type="number" 
              id="maxDepth" 
              min="0" 
              max="5" 
              value={maxDepth}
              onChange={(e) => setMaxDepth(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-sm text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-400/50 transition shadow-inner"
            />
          </div>

          {/* Max Pages */}
          <div className="md:col-span-2">
            <label htmlFor="maxPages" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Max Pages</span>
              <span className="text-[10px] text-cyan-400 font-mono">|V| Limit</span>
            </label>
            <input 
              type="number" 
              id="maxPages" 
              min="1" 
              max="50" 
              value={maxPages}
              onChange={(e) => setMaxPages(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-sm text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-400/50 transition shadow-inner"
            />
          </div>

          {/* Politeness Delay */}
          <div className="md:col-span-2">
            <label htmlFor="delay" className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Delay</span>
              <span className="text-[10px] text-cyan-400 font-mono">Seconds</span>
            </label>
            <input 
              type="number" 
              id="delay" 
              min="0" 
              step="0.1" 
              value={delay}
              onChange={(e) => setDelay(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-sm text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-cyan-400/50 transition shadow-inner"
            />
          </div>

        </div>

        {/* Toggles & Submit Pill Button */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-cyber-border/60">
          <div className="flex items-center space-x-6">
            <label className="flex items-center space-x-2 text-xs font-medium text-slate-300 cursor-pointer select-none">
              <input 
                type="checkbox" 
                checked={respectRobots}
                onChange={(e) => setRespectRobots(e.target.checked)}
                className="rounded border-cyber-border text-violet-600 focus:ring-violet-500 bg-cyber-bg"
              />
              <span>Respect <code className="text-[11px] font-mono bg-cyber-surface px-1.5 py-0.5 rounded text-cyan-300 border border-cyber-border">robots.txt</code></span>
            </label>
            <label className="flex items-center space-x-2 text-xs font-medium text-slate-300 cursor-pointer select-none">
              <input 
                type="checkbox" 
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
                className="rounded border-cyber-border text-violet-600 focus:ring-violet-500 bg-cyber-bg"
              />
              <span>Dry-Run Mode</span>
            </label>
          </div>

          {/* Vibrant Cyber Violet Pill Button (from design image) */}
          <button 
            type="submit" 
            disabled={isLoading}
            className="px-6 py-2.5 bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-full shadow-lg shadow-violet-600/30 hover:shadow-violet-600/50 transition flex items-center gap-2.5 disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider"
          >
            <Play className="w-3.5 h-3.5 fill-current text-white" />
            <span>{isLoading ? 'Crawling...' : 'Start BFS Crawl'}</span>
          </button>
        </div>
      </form>
    </section>
  );
}
