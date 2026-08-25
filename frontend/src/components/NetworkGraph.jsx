import React, { useEffect, useRef } from 'react';
import { Network as VisNetwork } from 'vis-network/standalone/esm/vis-network';

function shortenUrl(url) {
  try {
    const u = new URL(url);
    return u.pathname === '/' ? u.hostname : (u.pathname.length > 22 ? u.pathname.slice(0, 20) + '...' : u.pathname);
  } catch {
    return url.length > 22 ? url.slice(0, 20) + '...' : url;
  }
}

export default function NetworkGraph({ graph, pages, isDark }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    const depthMap = {};
    if (pages) {
      pages.forEach((p) => {
        depthMap[p.url] = p.depth;
      });
    }

    const nodesArray = [];
    const edgesArray = [];
    const addedNodes = new Set();

    const bgColor = isDark ? '#0b0f19' : '#f8fafc';
    const fontColor = isDark ? '#f1f5f9' : '#0f172a';
    const edgeColor = isDark ? '#2a3b5e' : '#cbd5e1';
    const edgeHighlight = isDark ? '#00f0ff' : '#7c3aed';

    Object.keys(graph).forEach((nodeUrl) => {
      if (!addedNodes.has(nodeUrl)) {
        addedNodes.add(nodeUrl);
        const depth = depthMap[nodeUrl] !== undefined ? depthMap[nodeUrl] : 2;
        let color = '#ff5722'; // Coral/Orange for Level 2+
        if (depth === 0) color = '#8b5cf6'; // Violet for Seed (Level 0)
        else if (depth === 1) color = '#00f0ff'; // Cyan for Level 1

        nodesArray.push({
          id: nodeUrl,
          label: shortenUrl(nodeUrl),
          title: `${nodeUrl} (Depth: ${depth})`,
          color: { 
            background: color, 
            border: isDark ? '#1e293b' : '#ffffff',
            highlight: { background: color, border: '#00f0ff' }
          },
          font: { color: fontColor, size: 11, face: 'JetBrains Mono, monospace' },
          shape: 'dot',
          size: depth === 0 ? 24 : 16,
        });
      }

      (graph[nodeUrl] || []).forEach((targetUrl) => {
        if (!addedNodes.has(targetUrl)) {
          addedNodes.add(targetUrl);
          const depth = depthMap[targetUrl] !== undefined ? depthMap[targetUrl] : 2;
          let color = '#ff5722';
          if (depth === 0) color = '#8b5cf6';
          else if (depth === 1) color = '#00f0ff';

          nodesArray.push({
            id: targetUrl,
            label: shortenUrl(targetUrl),
            title: `${targetUrl} (Depth: ${depth})`,
            color: { 
              background: color, 
              border: isDark ? '#1e293b' : '#ffffff',
              highlight: { background: color, border: '#00f0ff' }
            },
            font: { color: fontColor, size: 11, face: 'JetBrains Mono, monospace' },
            shape: 'dot',
            size: 16,
          });
        }

        edgesArray.push({
          from: nodeUrl,
          to: targetUrl,
          arrows: 'to',
          color: { color: edgeColor, highlight: edgeHighlight },
          smooth: { type: 'continuous' },
        });
      });
    });

    const data = {
      nodes: nodesArray,
      edges: edgesArray,
    };

    const options = {
      physics: {
        stabilization: true,
        barnesHut: { gravitationalConstant: -3000, springLength: 110 },
      },
      interaction: { hover: true, tooltipDelay: 100 },
    };

    if (networkRef.current) {
      networkRef.current.destroy();
    }

    networkRef.current = new VisNetwork(containerRef.current, data, options);

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [graph, pages, isDark]);

  return (
    <div className="p-6 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
        <p className="font-sans">Interactive directed graph topology of the crawled website.</p>
        <div className="flex items-center gap-4 font-mono text-[11px]">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-violet-500 inline-block shadow-sm shadow-violet-500/50"></span> Level 0 (Seed)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block shadow-sm shadow-cyan-400/50"></span> Level 1
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500 inline-block shadow-sm shadow-orange-500/50"></span> Level 2+
          </span>
        </div>
      </div>

      <div 
        ref={containerRef} 
        className="w-full h-[520px] rounded-2xl border border-cyber-border bg-[#0b0f19] shadow-inner"
      />
    </div>
  );
}
