import React, { useState, useMemo } from 'react';
import { Search, ExternalLink, ChevronDown, ChevronRight, Quote } from 'lucide-react';

export default function PagesTable({ pages }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [depthFilter, setDepthFilter] = useState('all');
  const [expandedRows, setExpandedRows] = useState(new Set());

  const toggleRow = (url) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(url)) next.delete(url);
      else next.add(url);
      return next;
    });
  };

  const filteredPages = useMemo(() => {
    if (!pages) return [];
    return pages.filter((page) => {
      const q = searchQuery.toLowerCase();
      const matchesQuery = 
        page.url.toLowerCase().includes(q) || 
        page.title.toLowerCase().includes(q) ||
        (page.snippet && page.snippet.toLowerCase().includes(q));

      const matchesDepth = 
        depthFilter === 'all'
          ? true
          : depthFilter === '2'
            ? page.depth >= 2
            : page.depth === Number(depthFilter);

      return matchesQuery && matchesDepth;
    });
  }, [pages, searchQuery, depthFilter]);

  return (
    <div className="p-6 space-y-4">
      
      {/* Search & Filter Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="relative flex-1 max-w-sm">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-cyan-400">
            <Search className="w-3.5 h-3.5" />
          </div>
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter crawled URLs, titles, or quotes..." 
            className="w-full pl-9 pr-3.5 py-2 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-400/50 font-mono transition"
          />
        </div>
        
        <div className="flex items-center gap-2 text-xs text-slate-300">
          <span className="font-medium text-slate-400">Filter Level:</span>
          <select 
            value={depthFilter}
            onChange={(e) => setDepthFilter(e.target.value)}
            className="bg-cyber-bg border border-cyber-border focus:border-cyan-400 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-cyan-400 font-mono"
          >
            <option value="all">All Levels</option>
            <option value="0">Level 0 (Seed)</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2+</option>
          </select>
        </div>
      </div>

      {/* Table with Expandable Content */}
      <div className="overflow-x-auto rounded-2xl border border-cyber-border/80 bg-cyber-bg/60">
        <table className="w-full text-left text-xs">
          <thead className="bg-cyber-card/90 text-slate-300 font-semibold border-b border-cyber-border uppercase tracking-wider text-[10px]">
            <tr>
              <th scope="col" className="px-3 py-3 w-8 text-center"></th>
              <th scope="col" className="px-3 py-3 w-10 text-center">#</th>
              <th scope="col" className="px-4 py-3 w-28 whitespace-nowrap">Depth</th>
              <th scope="col" className="px-4 py-3">Page Title & Content Preview</th>
              <th scope="col" className="px-4 py-3">URL</th>
              <th scope="col" className="px-4 py-3">Parent URL</th>
              <th scope="col" className="px-4 py-3 text-right whitespace-nowrap">Outgoing Links</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cyber-border/40 font-mono">
            {filteredPages.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-4 py-8 text-center text-slate-400 font-sans text-xs">
                  No matching pages found.
                </td>
              </tr>
            ) : (
              filteredPages.map((page, idx) => {
                const isExpanded = expandedRows.has(page.url);
                const hasItems = page.extracted_data && page.extracted_data.length > 0;

                let badgeClass = 'bg-violet-950/70 text-violet-300 border-violet-500/40 shadow-xs shadow-violet-500/10';
                if (page.depth === 1) {
                  badgeClass = 'bg-cyan-950/70 text-cyan-300 border-cyan-500/40 shadow-xs shadow-cyan-500/10';
                } else if (page.depth >= 2) {
                  badgeClass = 'bg-orange-950/70 text-orange-300 border-orange-500/40 shadow-xs shadow-orange-500/10';
                }

                return (
                  <React.Fragment key={page.url + idx}>
                    <tr className="hover:bg-cyber-cardHover/80 transition text-slate-200 cursor-pointer" onClick={() => toggleRow(page.url)}>
                      
                      {/* Expand Toggle */}
                      <td className="px-3 py-3 text-center text-slate-400">
                        {hasItems ? (
                          isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                        ) : null}
                      </td>

                      <td className="px-3 py-3 text-center text-slate-500 font-sans">{idx + 1}</td>
                      
                      {/* Depth Level Badge */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`inline-flex items-center justify-center px-2.5 py-1 rounded-full text-[11px] font-semibold border ${badgeClass}`}>
                          Level {page.depth}
                        </span>
                      </td>

                      {/* Title & Preview */}
                      <td className="px-4 py-3 font-sans max-w-xs">
                        <div className="font-medium text-slate-100 truncate" title={page.title}>
                          {page.title}
                        </div>
                        {page.snippet && (
                          <p className="text-[11px] text-slate-400 line-clamp-1 italic mt-0.5" title={page.snippet}>
                            "{page.snippet}"
                          </p>
                        )}
                        {hasItems && (
                          <span className="inline-flex items-center gap-1 text-[10px] text-cyan-400 font-mono mt-1">
                            <Quote className="w-2.5 h-2.5" />
                            {page.extracted_data.length} item{page.extracted_data.length > 1 ? 's' : ''} extracted
                          </span>
                        )}
                      </td>

                      {/* URL Link */}
                      <td className="px-4 py-3 text-cyan-400 hover:text-cyan-300 hover:underline max-w-sm truncate" onClick={(e) => e.stopPropagation()}>
                        <a href={page.url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5">
                          <span>{page.url}</span>
                          <ExternalLink className="w-3 h-3 opacity-70 shrink-0" />
                        </a>
                      </td>

                      {/* Parent URL */}
                      <td className="px-4 py-3 text-slate-400 max-w-xs truncate font-sans text-xs" title={page.parent_url || '—'}>
                        {page.parent_url || '—'}
                      </td>

                      {/* Outgoing Links */}
                      <td className="px-4 py-3 text-right font-bold text-slate-100 font-sans text-sm">
                        {page.outgoing_count}
                      </td>
                    </tr>

                    {/* Expanded Content Sub-row */}
                    {isExpanded && hasItems && (
                      <tr className="bg-cyber-surface/40">
                        <td colSpan="7" className="p-4 pl-12">
                          <div className="space-y-2">
                            <span className="font-pixel text-[10px] text-cyan-400 uppercase tracking-wider block">
                              Extracted Quotes & Content from this page ({page.extracted_data.length}):
                            </span>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                              {page.extracted_data.map((item, qIdx) => (
                                <div key={qIdx} className="bg-cyber-bg/80 border border-cyber-border/60 rounded-xl p-3 text-xs text-slate-200 font-sans italic">
                                  "{item}"
                                </div>
                              ))}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
