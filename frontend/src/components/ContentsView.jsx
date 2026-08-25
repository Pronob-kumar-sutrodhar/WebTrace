import React, { useState, useMemo } from 'react';
import { 
  FileText, 
  Search, 
  ExternalLink, 
  FileDown, 
  Link2, 
  AlignLeft, 
  Copy, 
  Check, 
  FolderArchive 
} from 'lucide-react';

export default function ContentsView({ pages }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all'); // 'all', 'text', 'docs', 'urls'
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(key);
      setTimeout(() => setCopiedIndex(null), 2000);
    });
  };

  // Aggregate totals
  const totals = useMemo(() => {
    if (!pages) return { text: 0, docs: 0, urls: 0 };
    let text = 0;
    let docs = 0;
    let urls = 0;
    pages.forEach((p) => {
      text += p.text_blocks ? p.text_blocks.length : (p.extracted_data ? p.extracted_data.length : 0);
      docs += p.documents ? p.documents.length : 0;
      urls += p.all_urls ? p.all_urls.length : (p.outgoing_links ? p.outgoing_links.length : 0);
    });
    return { text, docs, urls };
  }, [pages]);

  // Filter pages and their contents based on search and category
  const filteredPages = useMemo(() => {
    if (!pages) return [];
    const q = searchQuery.toLowerCase();

    return pages.map((page) => {
      const textBlocks = page.text_blocks || page.extracted_data || [];
      const documents = page.documents || [];
      const allUrls = page.all_urls || page.outgoing_links || [];

      const filteredText = textBlocks.filter((t) => t.toLowerCase().includes(q));
      const filteredDocs = documents.filter(
        (d) => d.url.toLowerCase().includes(q) || (d.filename && d.filename.toLowerCase().includes(q))
      );
      const filteredUrls = allUrls.filter((u) => u.toLowerCase().includes(q));

      const hasMatchingContent = 
        filteredText.length > 0 || 
        filteredDocs.length > 0 || 
        filteredUrls.length > 0 || 
        page.title.toLowerCase().includes(q) || 
        page.url.toLowerCase().includes(q);

      return {
        ...page,
        filteredText,
        filteredDocs,
        filteredUrls,
        hasMatchingContent,
      };
    }).filter((p) => p.hasMatchingContent);
  }, [pages, searchQuery]);

  return (
    <div className="p-6 space-y-6">
      
      {/* Header with Title and Global Search */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-cyber-border pb-4">
        <div>
          <h3 className="text-sm font-pixel text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-300 flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            EXTRACTED CONTENTS
          </h3>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Retrieved <span className="font-semibold text-cyan-300">{totals.text}</span> text blocks,{' '}
            <span className="font-semibold text-amber-300">{totals.docs}</span> documents, and{' '}
            <span className="font-semibold text-violet-300">{totals.urls}</span> URLs across{' '}
            <span className="font-semibold text-slate-200">{pages ? pages.length : 0}</span> crawled pages.
          </p>
        </div>

        {/* Search Filter Input */}
        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-cyan-400">
            <Search className="w-3.5 h-3.5" />
          </div>
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search text, docs, or URLs..." 
            className="w-full pl-9 pr-3.5 py-1.5 bg-cyber-bg/90 border border-cyber-border focus:border-cyan-400 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-400 font-mono transition"
          />
        </div>
      </div>

      {/* Category Pills Bar */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={() => setCategoryFilter('all')}
          className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition ${
            categoryFilter === 'all'
              ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-600/30'
              : 'bg-cyber-surface hover:bg-cyber-card text-slate-300 border border-cyber-border'
          }`}
        >
          <span>All Contents</span>
        </button>

        <button
          onClick={() => setCategoryFilter('text')}
          className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition ${
            categoryFilter === 'text'
              ? 'bg-cyan-500 text-black shadow-md shadow-cyan-500/30'
              : 'bg-cyber-surface hover:bg-cyber-card text-slate-300 border border-cyber-border'
          }`}
        >
          <AlignLeft className="w-3 h-3" />
          <span>Text & Paragraphs ({totals.text})</span>
        </button>

        <button
          onClick={() => setCategoryFilter('docs')}
          className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition ${
            categoryFilter === 'docs'
              ? 'bg-amber-500 text-black shadow-md shadow-amber-500/30'
              : 'bg-cyber-surface hover:bg-cyber-card text-slate-300 border border-cyber-border'
          }`}
        >
          <FileDown className="w-3 h-3" />
          <span>Documents & Files ({totals.docs})</span>
        </button>

        <button
          onClick={() => setCategoryFilter('urls')}
          className={`px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition ${
            categoryFilter === 'urls'
              ? 'bg-purple-500 text-white shadow-md shadow-purple-500/30'
              : 'bg-cyber-surface hover:bg-cyber-card text-slate-300 border border-cyber-border'
          }`}
        >
          <Link2 className="w-3 h-3" />
          <span>Discovered URLs ({totals.urls})</span>
        </button>
      </div>

      {/* Pages Content List */}
      {filteredPages.length === 0 ? (
        <div className="p-10 text-center text-slate-400 font-sans text-xs bg-cyber-bg/40 rounded-2xl border border-cyber-border/60">
          <FileText className="w-8 h-8 text-slate-500 mx-auto mb-2 opacity-50" />
          <p>No content items found matching your filter query.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredPages.map((page, pIdx) => {
            let badgeColor = 'bg-violet-950/70 text-violet-300 border-violet-500/40';
            if (page.depth === 1) badgeColor = 'bg-cyan-950/70 text-cyan-300 border-cyan-500/40';
            else if (page.depth >= 2) badgeColor = 'bg-orange-950/70 text-orange-300 border-orange-500/40';

            const showText = categoryFilter === 'all' || categoryFilter === 'text';
            const showDocs = categoryFilter === 'all' || categoryFilter === 'docs';
            const showUrls = categoryFilter === 'all' || categoryFilter === 'urls';

            return (
              <div key={page.url + pIdx} className="bg-cyber-bg/60 border border-cyber-border/80 rounded-2xl p-5 shadow-lg space-y-4">
                
                {/* Page Source Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-cyber-border/40 pb-3">
                  <div className="flex items-center gap-2.5">
                    <span className={`inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-[10px] font-semibold border ${badgeColor}`}>
                      Level {page.depth}
                    </span>
                    <h4 className="font-sans font-semibold text-slate-100 text-sm">
                      {page.title}
                    </h4>
                  </div>

                  <a 
                    href={page.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline font-mono inline-flex items-center gap-1 max-w-sm truncate"
                  >
                    <span>{page.url}</span>
                    <ExternalLink className="w-3 h-3 shrink-0 opacity-75" />
                  </a>
                </div>

                {/* 1. Text & Headings Section */}
                {showText && page.filteredText && page.filteredText.length > 0 && (
                  <div className="space-y-2">
                    <span className="font-pixel text-[10px] text-cyan-400 uppercase tracking-wider block flex items-center gap-1.5">
                      <AlignLeft className="w-3 h-3" />
                      Extracted Text Content ({page.filteredText.length}):
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {page.filteredText.map((text, tIdx) => {
                        const copyKey = `t-${pIdx}-${tIdx}`;
                        return (
                          <div 
                            key={tIdx} 
                            className="relative overflow-hidden bg-cyber-surface/60 border border-cyber-border/60 hover:border-cyan-500/40 rounded-xl p-3.5 transition text-xs text-slate-200 leading-relaxed font-sans group flex justify-between gap-2"
                          >
                            <p className="text-slate-200">
                              {text}
                            </p>
                            <button
                              onClick={() => handleCopy(text, copyKey)}
                              title="Copy text block"
                              className="opacity-0 group-hover:opacity-100 p-1 rounded-md bg-cyber-card hover:bg-cyber-border text-slate-400 hover:text-cyan-300 transition shrink-0 self-start"
                            >
                              {copiedIndex === copyKey ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 2. Discovered Documents & Files Section */}
                {showDocs && page.filteredDocs && page.filteredDocs.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-cyber-border/30">
                    <span className="font-pixel text-[10px] text-amber-400 uppercase tracking-wider block flex items-center gap-1.5">
                      <FileDown className="w-3 h-3" />
                      Discovered Documents & Downloads ({page.filteredDocs.length}):
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                      {page.filteredDocs.map((doc, dIdx) => (
                        <a 
                          key={dIdx}
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 bg-amber-950/30 hover:bg-amber-950/50 border border-amber-500/30 hover:border-amber-400/60 rounded-xl transition text-xs text-amber-200 group"
                        >
                          <FolderArchive className="w-4 h-4 text-amber-400 shrink-0 group-hover:scale-110 transition" />
                          <div className="truncate flex-1">
                            <p className="font-semibold truncate">{doc.filename}</p>
                            <span className="text-[10px] text-amber-400/80 font-mono uppercase">{doc.type} File</span>
                          </div>
                          <ExternalLink className="w-3 h-3 text-amber-400 opacity-60 shrink-0" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {/* 3. Discovered URLs Section */}
                {showUrls && page.filteredUrls && page.filteredUrls.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-cyber-border/30">
                    <span className="font-pixel text-[10px] text-purple-400 uppercase tracking-wider block flex items-center gap-1.5">
                      <Link2 className="w-3 h-3" />
                      Discovered URLs on this page ({page.filteredUrls.length}):
                    </span>
                    <div className="max-h-48 overflow-y-auto custom-scrollbar bg-cyber-bg/90 border border-cyber-border/60 rounded-xl p-3 space-y-1.5">
                      {page.filteredUrls.map((url, uIdx) => (
                        <div key={uIdx} className="flex items-center justify-between text-xs font-mono py-0.5 hover:text-cyan-300">
                          <a 
                            href={url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="truncate text-slate-300 hover:text-cyan-400 flex items-center gap-1.5"
                          >
                            <span className="text-[10px] text-slate-500">#{uIdx + 1}</span>
                            <span className="truncate">{url}</span>
                          </a>
                          <ExternalLink className="w-3 h-3 text-slate-500 hover:text-cyan-400 shrink-0 ml-2" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
