import React from 'react';
import { Layers, CircleDot, ArrowRightLeft, Clock } from 'lucide-react';

export default function StatCards({ stats }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      
      {/* Pages Crawled */}
      <div className="relative overflow-hidden bg-cyber-card/90 border border-cyber-border rounded-2xl p-5 shadow-lg backdrop-blur-md transition hover:border-violet-500/50">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold tracking-wide uppercase text-slate-300">Pages Visited</span>
          <div className="w-7 h-7 rounded-lg bg-violet-950/60 border border-violet-500/30 flex items-center justify-center">
            <Layers className="w-3.5 h-3.5 text-violet-400" />
          </div>
        </div>
        <div className="text-2xl sm:text-3xl font-bold font-pixel text-transparent bg-clip-text bg-gradient-to-r from-violet-300 to-purple-400">
          {stats.total_crawled}
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Explored BFS vertices</p>
      </div>

      {/* Graph Vertices */}
      <div className="relative overflow-hidden bg-cyber-card/90 border border-cyber-border rounded-2xl p-5 shadow-lg backdrop-blur-md transition hover:border-cyan-500/50">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold tracking-wide uppercase text-slate-300">Graph Vertices</span>
          <div className="w-7 h-7 rounded-lg bg-cyan-950/60 border border-cyan-500/30 flex items-center justify-center">
            <CircleDot className="w-3.5 h-3.5 text-cyan-400" />
          </div>
        </div>
        <div className="text-2xl sm:text-3xl font-bold font-pixel text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-teal-400">
          {stats.graph_nodes}
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Unique discovered URLs</p>
      </div>

      {/* Directed Edges */}
      <div className="relative overflow-hidden bg-cyber-card/90 border border-cyber-border rounded-2xl p-5 shadow-lg backdrop-blur-md transition hover:border-purple-500/50">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold tracking-wide uppercase text-slate-300">Directed Edges</span>
          <div className="w-7 h-7 rounded-lg bg-purple-950/60 border border-purple-500/30 flex items-center justify-center">
            <ArrowRightLeft className="w-3.5 h-3.5 text-purple-400" />
          </div>
        </div>
        <div className="text-2xl sm:text-3xl font-bold font-pixel text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-pink-400">
          {stats.graph_edges}
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Internal links (|E|)</p>
      </div>

      {/* Crawl Duration */}
      <div className="relative overflow-hidden bg-cyber-card/90 border border-cyber-border rounded-2xl p-5 shadow-lg backdrop-blur-md transition hover:border-amber-500/50">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-semibold tracking-wide uppercase text-slate-300">Crawl Duration</span>
          <div className="w-7 h-7 rounded-lg bg-amber-950/60 border border-amber-500/30 flex items-center justify-center">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
          </div>
        </div>
        <div className="text-2xl sm:text-3xl font-bold font-pixel text-transparent bg-clip-text bg-gradient-to-r from-amber-300 to-orange-400">
          {stats.duration_seconds ? stats.duration_seconds.toFixed(2) : '0.00'}s
        </div>
        <p className="text-[11px] text-slate-400 mt-1">Total runtime</p>
      </div>

    </div>
  );
}
