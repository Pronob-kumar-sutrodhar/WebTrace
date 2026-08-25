import React from 'react';
import { X, Layers, Hash, Network, GitBranch } from 'lucide-react';

export default function DsaExplainer({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="bg-cyber-card border border-cyber-border rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto custom-scrollbar">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-cyber-border pb-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 text-white flex items-center justify-center border border-cyan-400/30">
              <Network className="w-4 h-4 text-cyan-200" />
            </div>
            <div>
              <h3 className="text-sm font-pixel text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-300">
                DSA CONCEPT GUIDE
              </h3>
              <p className="text-xs text-slate-400 font-sans mt-0.5">Core Algorithm & Data Structure Invariants</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-full text-slate-400 hover:text-cyan-300 hover:bg-cyber-surface transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pillars Grid */}
        <div className="space-y-3.5 text-xs leading-relaxed text-slate-300 font-sans">
          
          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-100 text-xs">
              <Layers className="w-4 h-4 text-violet-400" />
              <span>1. FIFO Queue (collections.deque) — Breadth-First Search</span>
            </div>
            <p className="text-slate-400">
              Controls crawl order in strict FIFO discipline (<code className="font-mono text-cyan-400">popleft</code> from front, <code className="font-mono text-cyan-400">append</code> to rear). Guarantees discovering the shortest click-distance path from the seed URL.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-100 text-xs">
              <Hash className="w-4 h-4 text-cyan-400" />
              <span>2. Visited Hash Set (set) — O(1) Duplicate & Cycle Prevention</span>
            </div>
            <p className="text-slate-400">
              Provides constant <code className="font-mono text-cyan-400">O(1)</code> average membership check. Links are hashed upon discovery to prune circular paths (<code className="font-mono">A → B → A</code>) and avoid redundant network requests.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-100 text-xs">
              <GitBranch className="w-4 h-4 text-purple-400" />
              <span>3. Adjacency List (LinkGraph) — O(|V| + |E|) Space Complexity</span>
            </div>
            <p className="text-slate-400">
              Stores website link connections as a dictionary mapping each page to its outgoing targets. Maximally memory-efficient for sparse web graphs where <code className="font-mono text-purple-300">|E| &lt;&lt; |V|²</code>.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-100 text-xs">
              <Network className="w-4 h-4 text-orange-400" />
              <span>4. Hash Map Caching & Domain Boundary Enforcement</span>
            </div>
            <p className="text-slate-400">
              Stores parsed <code className="font-mono text-orange-300">robots.txt</code> rules and per-domain request timestamps in Hash Maps, guaranteeing polite delays and ethical crawling.
            </p>
          </div>

        </div>

        {/* Footer */}
        <div className="pt-2 flex justify-end">
          <button 
            onClick={onClose}
            className="px-5 py-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-full transition shadow-lg shadow-violet-600/30 uppercase tracking-wider"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
