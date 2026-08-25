import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function JsonViewer({ graph }) {
  const [copied, setCopied] = useState(false);

  const jsonString = JSON.stringify(graph || {}, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="p-6 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-400 font-mono">
          Adjacency List Mapping: <code className="text-cyan-400">dict[str, list[str]]</code>
        </span>
        
        <button
          onClick={handleCopy}
          className="px-3 py-1.5 bg-cyber-surface hover:bg-cyber-card text-cyan-300 text-xs rounded-full border border-cyan-500/30 hover:border-cyan-400 flex items-center gap-1.5 transition shadow-sm font-semibold"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-cyan-400" />}
          <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
        </button>
      </div>

      <pre className="bg-[#0b0f19] text-cyan-300 p-4 rounded-2xl text-xs font-mono overflow-x-auto max-h-[500px] border border-cyber-border custom-scrollbar shadow-inner">
        {jsonString}
      </pre>
    </div>
  );
}
