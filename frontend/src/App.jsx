import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import CrawlForm from './components/CrawlForm';
import StatCards from './components/StatCards';
import PagesTable from './components/PagesTable';
import ContentsView from './components/ContentsView';
import NetworkGraph from './components/NetworkGraph';
import JsonViewer from './components/JsonViewer';
import DsaExplainer from './components/DsaExplainer';
import { Table2, Network, Code2, Download, Loader2, FileText } from 'lucide-react';

export default function App() {
  const [isDark, setIsDark] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [crawlData, setCrawlData] = useState(null);
  const [activeTab, setActiveTab] = useState('table');
  const [isExplainerOpen, setIsExplainerOpen] = useState(false);

  // Initialize Theme
  useEffect(() => {
    const saved = localStorage.getItem('webtrace_theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = saved ? saved === 'dark' : prefersDark;
    setIsDark(dark);
    if (dark) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }
  }, []);

  const handleToggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev;
      localStorage.setItem('webtrace_theme', next ? 'dark' : 'light');
      if (next) {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }
      return next;
    });
  };

  const handleStartCrawl = async (params) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      const data = await response.json();
      if (data.status !== 'success') {
        alert(`Crawl Error: ${data.message || 'Unknown error occurred'}`);
        return;
      }

      setCrawlData(data);
      // If quotes/items were found, user can explore table or content view
      setActiveTab('table');
    } catch (err) {
      alert(`Request Failed: ${err.message}. Make sure Python backend server is running!`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col cyber-grid-bg text-slate-100 transition-colors">
      
      {/* Navigation Header */}
      <Navbar 
        isDark={isDark} 
        onToggleTheme={handleToggleTheme} 
        onOpenExplainer={() => setIsExplainerOpen(true)} 
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Input Parameters Form */}
        <CrawlForm onStartCrawl={handleStartCrawl} isLoading={isLoading} />

        {/* Loading Spinner Indicator */}
        {isLoading && (
          <div className="bg-cyber-card/90 border border-cyber-border rounded-2xl p-10 text-center space-y-3 shadow-xl backdrop-blur-md transition animate-pulse">
            <div className="inline-block animate-spin text-cyan-400">
              <Loader2 className="w-8 h-8" />
            </div>
            <h3 className="text-sm font-semibold font-pixel text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-300">
              EXECUTING BFS CRAWL...
            </h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto font-sans">
              Processing FIFO Queue frontier, extracting page text/quotes, querying <code className="font-mono text-cyan-400">robots.txt</code>, and building Adjacency List.
            </p>
          </div>
        )}

        {/* Results Container */}
        {crawlData && (
          <div className="space-y-6">
            
            {/* Status Message Banner */}
            {crawlData.message && (
              <div className={`p-4 rounded-2xl border text-xs flex items-center gap-2.5 shadow-md ${
                crawlData.pages.length === 0 
                  ? 'bg-amber-950/40 border-amber-500/40 text-amber-300' 
                  : 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300'
              }`}>
                <span>{crawlData.message}</span>
              </div>
            )}

            {/* Stat Summary Cards */}
            <StatCards stats={crawlData.stats} />

            {/* Content Tabs Card */}
            <div className="bg-cyber-card/90 border border-cyber-border rounded-2xl shadow-xl overflow-hidden backdrop-blur-md transition">
              
              {/* Tab Header Bar */}
              <div className="border-b border-cyber-border/80 px-6 py-3 flex flex-wrap items-center justify-between gap-4 bg-cyber-bg/70">
                
                {/* Segmented Tab Switcher */}
                <div className="flex flex-wrap gap-4 text-xs font-medium">
                  
                  {/* Table Tab */}
                  <button 
                    onClick={() => setActiveTab('table')}
                    className={`py-2 border-b-2 flex items-center gap-2 transition ${
                      activeTab === 'table' 
                        ? 'border-cyan-400 text-cyan-300 font-semibold shadow-xs shadow-cyan-400/20' 
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Table2 className="w-4 h-4 text-cyan-400" />
                    <span>Crawled Pages Table</span>
                  </button>

                  {/* Extracted Contents Tab */}
                  <button 
                    onClick={() => setActiveTab('content')}
                    className={`py-2 border-b-2 flex items-center gap-2 transition ${
                      activeTab === 'content' 
                        ? 'border-cyan-400 text-cyan-300 font-semibold shadow-xs shadow-cyan-400/20' 
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <span>Extracted Contents</span>
                  </button>

                  {/* Visual Graph Tab */}
                  <button 
                    onClick={() => setActiveTab('graph')}
                    className={`py-2 border-b-2 flex items-center gap-2 transition ${
                      activeTab === 'graph' 
                        ? 'border-cyan-400 text-cyan-300 font-semibold shadow-xs shadow-cyan-400/20' 
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Network className="w-4 h-4 text-violet-400" />
                    <span>Visual Link Graph</span>
                  </button>

                  {/* JSON Adjacency List Tab */}
                  <button 
                    onClick={() => setActiveTab('json')}
                    className={`py-2 border-b-2 flex items-center gap-2 transition ${
                      activeTab === 'json' 
                        ? 'border-cyan-400 text-cyan-300 font-semibold shadow-xs shadow-cyan-400/20' 
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Code2 className="w-4 h-4 text-purple-400" />
                    <span>Adjacency List (JSON)</span>
                  </button>
                </div>

                {/* Export Action Pill Buttons */}
                <div className="flex items-center gap-2.5">
                  <a 
                    href="/api/download/csv" 
                    download="crawled_pages.csv"
                    className="px-4 py-1.5 bg-cyber-surface hover:bg-cyber-card text-cyan-300 text-xs font-semibold rounded-full border border-cyan-500/30 hover:border-cyan-400 shadow-sm flex items-center gap-1.5 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export CSV</span>
                  </a>

                  <a 
                    href="/api/download/json" 
                    download="link_graph.json"
                    className="px-4 py-1.5 bg-cyber-surface hover:bg-cyber-card text-cyan-300 text-xs font-semibold rounded-full border border-cyan-500/30 hover:border-cyan-400 shadow-sm flex items-center gap-1.5 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Export JSON</span>
                  </a>
                </div>

              </div>

              {/* Tab Views */}
              {activeTab === 'table' && <PagesTable pages={crawlData.pages} />}
              {activeTab === 'content' && <ContentsView pages={crawlData.pages} />}
              {activeTab === 'graph' && (
                <NetworkGraph 
                  graph={crawlData.graph} 
                  pages={crawlData.pages} 
                  isDark={isDark} 
                />
              )}
              {activeTab === 'json' && <JsonViewer graph={crawlData.graph} />}

            </div>

          </div>
        )}

      </main>

      {/* Clean Cyber Footer */}
      <footer className="border-t border-cyber-border/70 bg-[#0e1424]/90 py-4 text-center text-xs text-slate-400 transition-colors">
        <div className="max-w-7xl mx-auto px-4 flex items-center justify-between">
          <span className="font-pixel text-[11px] text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-300">
            WEBTRACE
          </span>
          <span className="font-mono text-[11px] text-slate-500">
            Domain-Restricted BFS Crawler
          </span>
        </div>
      </footer>

      {/* Educational Modal */}
      <DsaExplainer isOpen={isExplainerOpen} onClose={() => setIsExplainerOpen(false)} />

    </div>
  );
}
