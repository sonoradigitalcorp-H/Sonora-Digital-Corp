'use client';

import { useState } from 'react';
import useSWR, { mutate } from 'swr';
import { FileText, FileSpreadsheet, FileImage, File, Download, Upload, Plus, Search, Filter, Eye, Loader2, AlertCircle, CheckCircle, Clock, X } from 'lucide-react';

const fetcher = (url: string) => fetch(url).then(r => r.json());

const categoryColors: Record<string, string> = {
  contract: 'text-red-500 bg-red-500/10',
  presentation: 'text-purple-500 bg-purple-500/10',
  analysis: 'text-blue-500 bg-blue-500/10',
  research: 'text-cyan-500 bg-cyan-500/10',
  legal: 'text-amber-500 bg-amber-500/10',
  financial: 'text-emerald-500 bg-emerald-500/10',
  compliance: 'text-orange-500 bg-orange-500/10',
  general: 'text-muted-foreground bg-muted',
};

const typeIcons: Record<string, any> = {
  pdf: FileText, xlsx: FileSpreadsheet, docx: FileText, pptx: FileImage,
};

export function DocumentsHub({ warRoomId }: { warRoomId: string }) {
  const [search, setSearch] = useState('');
  const [viewingDoc, setViewingDoc] = useState<any>(null);
  const [showGenerate, setShowGenerate] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [genType, setGenType] = useState('proposal');

  const { data, error, isLoading } = useSWR(`/api/v1/war-rooms/${warRoomId}/documents`, fetcher, { refreshInterval: 10000 });
  const docs = data?.documents ?? [];

  const filtered = docs.filter((d: any) =>
    d.name.toLowerCase().includes(search.toLowerCase())
  );

  const generateDoc = async () => {
    setGenerating(true);
    const names: Record<string, string> = {
      proposal: 'Signing Proposal',
      brief: 'Executive Brief',
      analysis: 'Market Analysis',
      contract: 'Contract Draft',
    };
    await fetch(`/api/v1/war-rooms/${warRoomId}/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: `${names[genType] || 'Document'}.pdf`, type: 'pdf', category: genType === 'contract' ? 'legal' : genType === 'analysis' ? 'analysis' : 'presentation' }),
    });
    setGenerating(false);
    setShowGenerate(false);
    mutate(`/api/v1/war-rooms/${warRoomId}/documents`);
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Document Hub</h1>
          <p className="text-muted-foreground mt-1">Contracts, PDFs, presentations, and more</p>
        </div>
        <button onClick={() => setShowGenerate(true)} className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all">
          <Plus className="h-4 w-4" /> Generate Document
        </button>
      </div>

      {error && <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500"><AlertCircle className="h-4 w-4" /><span className="text-sm">Failed to load documents</span></div>}

      {/* Search & Filter */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input type="text" placeholder="Search documents..." value={search} onChange={e => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg font-medium">No documents yet</p>
          <p className="text-sm mt-1">Generate your first document to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((doc: any) => {
            const Icon = typeIcons[doc.type] || File;
            const catColor = categoryColors[doc.category] || categoryColors.general;
            return (
              <div key={doc.id} className="rounded-xl border bg-card p-4 hover:shadow-md hover:border-primary/30 transition-all cursor-pointer group" onClick={() => setViewingDoc(doc)}>
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${catColor}`}><Icon className="h-5 w-5" /></div>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${doc.status === 'final' ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'}`}>{doc.status}</span>
                </div>
                <h3 className="text-sm font-medium line-clamp-2">{doc.name}</h3>
                <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
                  <span>{doc.size}</span>
                  <span>{doc.updated}</span>
                </div>
                <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors"><Eye className="h-3 w-3" /> View</button>
                  <button className="flex items-center gap-1 text-xs px-2 py-1 rounded bg-accent hover:bg-accent/80 transition-colors"><Download className="h-3 w-3" /> Download</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* PDF Viewer Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setViewingDoc(null)}>
          <div className="rounded-xl border bg-card w-full max-w-3xl max-h-[80vh] mx-4 shadow-2xl flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-primary" />
                <div>
                  <h3 className="font-semibold text-sm">{viewingDoc.name}</h3>
                  <p className="text-xs text-muted-foreground">{viewingDoc.category} · {viewingDoc.size} · by {viewingDoc.author}</p>
                </div>
              </div>
              <button onClick={() => setViewingDoc(null)} className="p-1 rounded-lg hover:bg-accent transition-colors">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-muted/30">
              <div className="rounded-lg border bg-card p-8 max-w-2xl mx-auto min-h-[400px] shadow-sm">
                <div className="text-center py-12">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-primary/30" />
                  <h2 className="text-xl font-bold mb-2">{viewingDoc.name.replace('.pdf', '').replace('.docx', '').replace('.xlsx', '')}</h2>
                  <p className="text-sm text-muted-foreground mb-6">Generated by {viewingDoc.author} · {viewingDoc.updated}</p>
                  <div className="flex items-center justify-center gap-4">
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">
                      <Download className="h-4 w-4" /> Download PDF
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-card text-sm font-medium hover:bg-accent">
                      <Eye className="h-4 w-4" /> Print
                    </button>
                  </div>
                  <div className="mt-8 text-left text-sm text-muted-foreground space-y-2 border-t pt-6">
                    <p><strong>Status:</strong> {viewingDoc.status === 'final' ? '✅ Final' : '📝 Draft'}</p>
                    <p><strong>Category:</strong> {viewingDoc.category}</p>
                    <p><strong>File size:</strong> {viewingDoc.size}</p>
                    <p><strong>Last updated:</strong> {viewingDoc.updated}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Generate Document Modal */}
      {showGenerate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => !generating && setShowGenerate(false)}>
          <div className="rounded-xl border bg-card p-6 max-w-md w-full mx-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-4">Generate Document</h3>
            <div className="space-y-3">
              {[
                { id: 'proposal', label: 'Signing Proposal', desc: 'Full signing recommendation package' },
                { id: 'brief', label: 'Executive Brief', desc: 'AI-generated executive summary' },
                { id: 'analysis', label: 'Market Analysis', desc: 'Market intelligence report' },
                { id: 'contract', label: 'Contract Draft', desc: 'Legal contract draft' },
              ].map(opt => (
                <button
                  key={opt.id}
                  onClick={() => setGenType(opt.id)}
                  className={`w-full text-left p-3 rounded-lg border transition-all ${genType === opt.id ? 'border-primary bg-primary/5' : 'hover:bg-accent'}`}
                >
                  <p className="text-sm font-medium">{opt.label}</p>
                  <p className="text-xs text-muted-foreground">{opt.desc}</p>
                </button>
              ))}
            </div>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button onClick={() => setShowGenerate(false)} disabled={generating} className="px-4 py-2 rounded-lg border bg-card text-sm hover:bg-accent transition-colors disabled:opacity-50">Cancel</button>
              <button onClick={generateDoc} disabled={generating} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-all disabled:opacity-50">
                {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                {generating ? 'Generating...' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
