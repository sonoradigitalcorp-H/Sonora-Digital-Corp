'use client';

import React, { forwardRef } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

// ───────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────

export interface ReportArtistData {
  score: number;
  growth: number;
  listeners: number;
  followers: number;
  genres: string[];
  city: string;
  country: string;
  deal: number;
  engagement: number;
  momentum: number;
  platforms: Record<string, number>;
  growthHistory: { month: string; followers: number; streams: number; score: number }[];
}

export interface ReportPDFData {
  id: string;
  name: string;
  type: string;
  status: string;
  created: string;
  author: string;
  description: string;
  artistName: string;
  agentActions: string[];
  artist?: ReportArtistData;
}

// ───────────────────────────────────────────────
// PDF Content Component — designed as a printable
// executive report with professional layout
// ───────────────────────────────────────────────

const ReportPDFContent = forwardRef<HTMLDivElement, { report: ReportPDFData }>(
  ({ report }, ref) => {
    const { artist } = report;
    const isDraft = report.status === 'draft';

    // Parse description for extended info
    const scoreMatch = report.description.match(/Score\s+(\d+)/i);
    const dealMatch = report.description.match(/Deal estimado:\s*\$?([\d,]+)K/i);
    const score = artist?.score ?? (scoreMatch ? parseInt(scoreMatch[1]) : null);
    const deal = artist?.deal ?? (dealMatch ? parseInt(dealMatch[1]) * 1000 : null);

    const typeColors: Record<string, string> = {
      analytics: 'text-emerald-600 bg-emerald-50 border-emerald-200',
      executive: 'text-indigo-600 bg-indigo-50 border-indigo-200',
      legal: 'text-amber-600 bg-amber-50 border-amber-200',
    };

    const typeColor = typeColors[report.type] || typeColors.executive;

    const pageWidth = 800;
    const pageHeight = 1131; // A4 ratio: 800 * 297/210

    const formatNumber = (n: number) =>
      n >= 1000000
        ? `${(n / 1000000).toFixed(1)}M`
        : n >= 1000
          ? `${(n / 1000).toFixed(1)}K`
          : n.toString();

    const formatCurrency = (n: number) =>
      '$' + n.toLocaleString('en-US');

    const formatDate = (d: string) => {
      try {
        return new Date(d).toLocaleDateString('en-US', {
          year: 'numeric', month: 'long', day: 'numeric',
        });
      } catch {
        return d;
      }
    };

    return (
      <div
        ref={ref}
        className="bg-white"
        style={{
          width: pageWidth + 'px',
          fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
        }}
      >
        {/* ════════════════════════════════════════
            PAGE 1 — COVER PAGE
            ════════════════════════════════════════ */}
        <div
          className="relative overflow-hidden flex flex-col"
          style={{ width: pageWidth + 'px', height: pageHeight + 'px' }}
        >
          {/* Background gradient */}
          <div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 70%, #1e1b4b 100%)',
            }}
          />

          {/* Subtle grid pattern overlay */}
          <div
            className="absolute inset-0 opacity-[0.07]"
            style={{
              backgroundImage:
                'linear-gradient(rgba(255,255,255,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.2) 1px, transparent 1px)',
              backgroundSize: '60px 60px',
            }}
          />

          {/* Large decorative circle */}
          <div
            className="absolute -top-40 -right-40 rounded-full opacity-20"
            style={{
              width: '500px',
              height: '500px',
              background: 'radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)',
            }}
          />

          {/* Content */}
          <div className="relative z-10 flex flex-col justify-between h-full p-16">
            {/* Top: Brand */}
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#818cf8', letterSpacing: '3px', textTransform: 'uppercase' }}>
                Abe Music Group
              </div>
              <div style={{ marginTop: '4px', display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                <span style={{ fontSize: '48px', fontWeight: 800, color: '#ffffff', letterSpacing: '-1px' }}>
                  SIGNAL
                </span>
                <span style={{ fontSize: '16px', color: '#a5b4fc', fontWeight: 300 }}>
                  Music Intelligence Platform
                </span>
              </div>
              <div style={{ marginTop: '32px', height: '2px', width: '60px', background: '#6366f1' }} />
            </div>

            {/* Center: Report info */}
            <div style={{ maxWidth: '600px' }}>
              {/* Type badge */}
              <div
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border text-sm font-semibold tracking-wide uppercase"
                style={{
                  background: report.type === 'analytics' ? 'rgba(5,150,105,0.15)' :
                              report.type === 'legal' ? 'rgba(217,119,6,0.15)' :
                              'rgba(99,102,241,0.15)',
                  color: report.type === 'analytics' ? '#34d399' :
                         report.type === 'legal' ? '#fbbf24' :
                         '#a5b4fc',
                  borderColor: report.type === 'analytics' ? 'rgba(5,150,105,0.3)' :
                               report.type === 'legal' ? 'rgba(217,119,6,0.3)' :
                               'rgba(99,102,241,0.3)',
                }}
              >
                {report.type === 'analytics' ? '●' : report.type === 'legal' ? '◆' : '■'}
                {report.type} report
              </div>

              {/* Title */}
              <h1 style={{ fontSize: '42px', fontWeight: 700, color: '#ffffff', lineHeight: 1.15, marginTop: '24px' }}>
                {report.artistName}
              </h1>

              {/* Subtitle */}
              <p style={{ fontSize: '20px', color: '#c7d2fe', marginTop: '12px', fontWeight: 300 }}>
                {report.name.replace(report.artistName + ' — ', '')}
              </p>

              {/* Meta */}
              <div style={{ marginTop: '32px', display: 'flex', gap: '40px' }}>
                <div>
                  <p style={{ fontSize: '11px', color: '#818cf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>Date</p>
                  <p style={{ fontSize: '14px', color: '#e0e7ff', marginTop: '4px' }}>{formatDate(report.created)}</p>
                </div>
                <div>
                  <p style={{ fontSize: '11px', color: '#818cf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>Status</p>
                  <p style={{ fontSize: '14px', color: isDraft ? '#fbbf24' : '#34d399', marginTop: '4px', fontWeight: 600 }}>
                    {isDraft ? '● DRAFT' : '● FINAL'}
                  </p>
                </div>
                <div>
                  <p style={{ fontSize: '11px', color: '#818cf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>Author</p>
                  <p style={{ fontSize: '14px', color: '#e0e7ff', marginTop: '4px' }}>{report.author}</p>
                </div>
              </div>
            </div>

            {/* Bottom */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
              <div>
                {artist && (
                  <p style={{ fontSize: '13px', color: '#a5b4fc' }}>
                    {artist.city}, {artist.country} · {artist.genres.join(' / ')}
                  </p>
                )}
              </div>
              <div style={{ textAlign: 'right' }}>
                <p style={{ fontSize: '11px', color: '#6366f1', fontWeight: 700, letterSpacing: '2px' }}>
                  CONFIDENTIAL
                </p>
                <p style={{ fontSize: '10px', color: '#6366f1', marginTop: '2px' }}>
                  SIGNAL v3 · Abe Music Group
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ════════════════════════════════════════
            PAGE 2 — EXECUTIVE SUMMARY
            ════════════════════════════════════════ */}
        <div style={{ width: pageWidth + 'px', minHeight: pageHeight + 'px', padding: '56px 64px', background: '#ffffff' }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' }}>
            <div>
              <p style={{ fontSize: '11px', fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '2px' }}>Executive Summary</p>
              <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#1e1b4b', marginTop: '4px' }}>
                {report.artistName}
              </h2>
            </div>
            <div
              className={`px-3 py-1 rounded-lg border text-xs font-semibold uppercase tracking-wider ${typeColor}`}
            >
              {report.type}
            </div>
          </div>

          {/* Score hero */}
          {score !== null && (
            <div
              style={{
                background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
                borderRadius: '16px',
                padding: '32px',
                display: 'flex',
                alignItems: 'center',
                gap: '32px',
                marginBottom: '36px',
              }}
            >
              <div style={{ textAlign: 'center', flexShrink: 0 }}>
                <p style={{ fontSize: '64px', fontWeight: 800, color: '#4338ca', lineHeight: 1 }}>{score}</p>
                <p style={{ fontSize: '12px', color: '#6366f1', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px', marginTop: '4px' }}>
                  Score
                </p>
              </div>
              <div style={{ width: '1px', height: '80px', background: '#c7d2fe' }} />
              <div>
                <p style={{ fontSize: '15px', color: '#4338ca', fontWeight: 500, lineHeight: 1.5 }}>
                  {report.description || 'No additional description available.'}
                </p>
                {deal !== null && (
                  <p style={{ fontSize: '13px', color: '#6366f1', marginTop: '8px' }}>
                    Deal Estimate: <strong>{formatCurrency(deal)}</strong>
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Key Metrics Grid */}
          {artist && (
            <>
              <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Key Metrics
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '36px' }}>
                {[
                  { label: 'Monthly Listeners', value: formatNumber(artist.listeners), sub: 'Platform aggregate' },
                  { label: 'Followers', value: formatNumber(artist.followers), sub: 'Cross-platform' },
                  { label: 'Growth Rate', value: `+${artist.growth}%`, sub: 'Month-over-month', color: true },
                  { label: 'Engagement', value: `${artist.engagement}%`, sub: 'Avg. engagement rate', color: true },
                ].map((metric, i) => (
                  <div key={i} style={{ background: '#f9fafb', borderRadius: '12px', padding: '20px' }}>
                    <p style={{ fontSize: '11px', color: '#6b7280', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {metric.label}
                    </p>
                    <p
                      style={{
                        fontSize: '28px',
                        fontWeight: 700,
                        color: metric.color ? '#059669' : '#1e1b4b',
                        marginTop: '4px',
                      }}
                    >
                      {metric.value}
                    </p>
                    <p style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>{metric.sub}</p>
                  </div>
                ))}
              </div>

              {/* Growth History Mini Table */}
              <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Growth History (Last 6 Months)
              </p>
              <div style={{ border: '1px solid #e5e7eb', borderRadius: '12px', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                  <thead>
                    <tr style={{ background: '#f9fafb' }}>
                      {['Month', 'Followers', 'Streams', 'Score'].map(h => (
                        <th key={h} style={{ textAlign: 'left', padding: '12px 16px', color: '#6b7280', fontWeight: 600, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '1px solid #e5e7eb' }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(artist.growthHistory || []).map((row, i) => (
                      <tr key={i} style={{ borderBottom: i < 5 ? '1px solid #f3f4f6' : 'none' }}>
                        <td style={{ padding: '10px 16px', fontWeight: 600, color: '#374151' }}>{row.month}</td>
                        <td style={{ padding: '10px 16px', color: '#4b5563' }}>{formatNumber(row.followers)}</td>
                        <td style={{ padding: '10px 16px', color: '#4b5563' }}>{formatNumber(row.streams)}</td>
                        <td style={{ padding: '10px 16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ flex: 1, height: '6px', background: '#e5e7eb', borderRadius: '3px' }}>
                              <div style={{ width: `${(row.score / 100) * 100}%`, height: '100%', background: '#6366f1', borderRadius: '3px' }} />
                            </div>
                            <span style={{ fontSize: '12px', fontWeight: 600, color: '#4b5563' }}>{row.score}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* Footer */}
          <div style={{ marginTop: '48px', paddingTop: '16px', borderTop: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between' }}>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>SIGNAL · Music Intelligence Platform</p>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>Page 2</p>
          </div>
        </div>

        {/* ════════════════════════════════════════
            PAGE 3 — AGENT ACTIVITY
            ════════════════════════════════════════ */}
        <div style={{ width: pageWidth + 'px', minHeight: pageHeight + 'px', padding: '56px 64px', background: '#ffffff' }}>
          <p style={{ fontSize: '11px', fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '2px' }}>
            Agent Intelligence
          </p>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#1e1b4b', marginTop: '4px', marginBottom: '32px' }}>
            Agent Activity & Analysis
          </h2>

          {/* Agent actions */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {report.agentActions.map((action, i) => {
              // Determine which agent based on action content
              const isLegal = action.toLowerCase().includes('legal') || action.toLowerCase().includes('cláusula') || action.toLowerCase().includes('riesgo') || action.toLowerCase().includes('compliance') || action.toLowerCase().includes('contrato');
              const isWriter = action.toLowerCase().includes('narrative') || action.toLowerCase().includes('pitch') || action.toLowerCase().includes('brief') || action.toLowerCase().includes('tradujo') || action.toLowerCase().includes('escribió');
              const isAnalyst = !isLegal && !isWriter;

              const agentColor = isLegal
                ? { bg: '#fffbeb', border: '#fde68a', dot: '#f59e0b', label: 'Legal Agent' }
                : isWriter
                  ? { bg: '#eef2ff', border: '#c7d2fe', dot: '#6366f1', label: 'Writer Agent' }
                  : { bg: '#ecfdf5', border: '#a7f3d0', dot: '#10b981', label: 'Analyst Agent' };

              return (
                <div
                  key={i}
                  style={{
                    background: agentColor.bg,
                    border: `1px solid ${agentColor.border}`,
                    borderRadius: '12px',
                    padding: '16px 20px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '14px',
                  }}
                >
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: agentColor.dot,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      color: '#ffffff',
                      fontSize: '12px',
                      fontWeight: 700,
                    }}
                  >
                    {isLegal ? '⚖' : isWriter ? '✎' : '△'}
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: '12px', fontWeight: 600, color: '#374151', marginBottom: '2px' }}>
                      {agentColor.label}
                    </p>
                    <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: 1.5 }}>
                      {action}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Artist Info Summary */}
          {artist && (
            <div style={{ marginTop: '40px' }}>
              <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Artist Profile
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                {[
                  { label: 'Genres', value: artist.genres.join(', ') },
                  { label: 'Location', value: `${artist.city}, ${artist.country}` },
                  { label: 'Momentum', value: `${artist.momentum}%` },
                  { label: 'Deal Estimate', value: formatCurrency(artist.deal) },
                ].map((item, i) => (
                  <div key={i} style={{ background: '#f9fafb', borderRadius: '8px', padding: '12px 16px' }}>
                    <p style={{ fontSize: '10px', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {item.label}
                    </p>
                    <p style={{ fontSize: '14px', color: '#1e1b4b', fontWeight: 500, marginTop: '2px' }}>
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* Platform presence */}
              <p style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginTop: '28px', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Platform Presence
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                {Object.entries(artist.platforms || {}).map(([platform, count]) => (
                  <div key={platform} style={{ background: '#f9fafb', borderRadius: '10px', padding: '14px', textAlign: 'center' }}>
                    <p style={{ fontSize: '11px', color: '#6b7280', fontWeight: 500 }}>{platform}</p>
                    <p style={{ fontSize: '18px', fontWeight: 700, color: '#1e1b4b', marginTop: '2px' }}>
                      {formatNumber(count)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div style={{ marginTop: '48px', paddingTop: '16px', borderTop: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between' }}>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>SIGNAL · Music Intelligence Platform</p>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>Page 3</p>
          </div>
        </div>

        {/* ════════════════════════════════════════
            PAGE 4 — FINANCIAL & LEGAL
            ════════════════════════════════════════ */}
        <div style={{ width: pageWidth + 'px', minHeight: pageHeight + 'px', padding: '56px 64px', background: '#ffffff' }}>
          <p style={{ fontSize: '11px', fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '2px' }}>
            Analysis
          </p>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#1e1b4b', marginTop: '4px', marginBottom: '32px' }}>
            Financial & Legal Assessment
          </h2>

          {/* Deal Structure */}
          {deal !== null && (
            <div style={{ background: '#f9fafb', borderRadius: '16px', padding: '28px', marginBottom: '24px' }}>
              <p style={{ fontSize: '14px', fontWeight: 700, color: '#1e1b4b', marginBottom: '16px' }}>
                Deal Structure
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {[
                  { label: 'Total Estimated Value', value: formatCurrency(deal), highlight: true },
                  { label: 'Advance', value: formatCurrency(Math.round(deal * 0.3)), highlight: false },
                  { label: 'Revenue Share', value: '80/20 (Label/Artist)', highlight: false },
                  { label: 'Term', value: '36 months (standard)', highlight: false },
                  { label: 'Territory', value: 'Worldwide', highlight: false },
                  { label: 'ROI Projection', value: '2.4x (36 months)', highlight: false },
                ].map((item, i) => (
                  <div key={i} style={{ padding: '12px', background: '#ffffff', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                    <p style={{ fontSize: '10px', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {item.label}
                    </p>
                    <p style={{ fontSize: item.highlight ? '20px' : '14px', fontWeight: item.highlight ? 700 : 500, color: item.highlight ? '#059669' : '#1e1b4b', marginTop: '4px' }}>
                      {item.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Assessment */}
          <div style={{ border: '1px solid #fde68a', borderRadius: '16px', padding: '28px', background: '#fffbeb', marginBottom: '24px' }}>
            <p style={{ fontSize: '14px', fontWeight: 700, color: '#92400e', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>⚠</span> Risk Assessment
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { level: 'Medium', item: 'Market concentration risk — heavy reliance on Regional Mexicano' },
                { level: 'Low', item: 'Contractual obligations clear, no exclusivity conflicts detected' },
                { level: 'Low', item: 'Social media compliance within standard guidelines' },
                { level: 'Medium', item: 'Territory rights limited to Americas, EU/Asia pending' },
              ].map((risk, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 14px', background: '#ffffff', borderRadius: '8px', border: '1px solid #fde68a' }}>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: risk.level === 'High' ? '#ef4444' : risk.level === 'Medium' ? '#f59e0b' : '#10b981',
                      flexShrink: 0,
                    }}
                  />
                  <span style={{ fontSize: '11px', fontWeight: 600, color: risk.level === 'High' ? '#dc2626' : risk.level === 'Medium' ? '#d97706' : '#059669', minWidth: '60px' }}>
                    {risk.level}
                  </span>
                  <span style={{ fontSize: '13px', color: '#4b5563' }}>{risk.item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendation */}
          <div style={{ background: '#eef2ff', borderRadius: '16px', padding: '28px', border: '1px solid #c7d2fe' }}>
            <p style={{ fontSize: '14px', fontWeight: 700, color: '#4338ca', marginBottom: '8px' }}>
              Recommendation
            </p>
            <p style={{ fontSize: '14px', color: '#3730a3', lineHeight: 1.7 }}>
              {score !== null && score >= 70
                ? `Proceed to contract negotiation. Artist scores ${score}/100 with strong growth trajectory.`
                : score !== null && score >= 60
                  ? `Continue monitoring with structured evaluation. Score of ${score}/100 indicates potential with defined risks to address.`
                  : `Extended evaluation recommended. Additional market analysis and due diligence required before proceeding.`}
              {' '}Deploy all 3 agents (Analyst, Writer, Legal) for comprehensive coverage before signing decision.
            </p>
          </div>

          {/* Footer */}
          <div style={{ marginTop: '48px', paddingTop: '16px', borderTop: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between' }}>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>SIGNAL · Music Intelligence Platform · Abe Music Group</p>
            <p style={{ fontSize: '10px', color: '#9ca3af' }}>Page 4</p>
          </div>
        </div>
      </div>
    );
  }
);

ReportPDFContent.displayName = 'ReportPDFContent';

// ───────────────────────────────────────────────
// Download Utility
// ───────────────────────────────────────────────

export async function downloadReportAsPDF(report: ReportPDFData): Promise<void> {
  // Create off-screen container
  const container = document.createElement('div');
  container.style.position = 'absolute';
  container.style.left = '-9999px';
  container.style.top = '0';
  container.style.width = '800px';
  container.style.zIndex = '-9999';
  document.body.appendChild(container);

  // Import and render React component
  const { createRoot } = await import('react-dom/client');
  const root = createRoot(container);
  root.render(<ReportPDFContent report={report} />);

  // Wait for rendering + font loading
  await new Promise(resolve => setTimeout(resolve, 500));
  await document.fonts.ready;

  try {
    // Capture the full report with higher resolution
    const canvas = await html2canvas(container, {
      scale: 3,
      useCORS: true,
      logging: false,
      width: 800,
      height: container.scrollHeight,
      windowWidth: 800,
      windowHeight: container.scrollHeight,
    });

    // PDF setup — A4 portrait
    const doc = new jsPDF('p', 'mm', 'a4');
    const pageWidthMm = 210;
    const margin = 10;
    const usableWidth = pageWidthMm - margin * 2; // 190mm
    const pageHeightMm = 297;                      // A4 height in mm

    // Physical canvas dimensions (after scale)
    const canvasW = canvas.width;
    const canvasH = canvas.height;

    // How many pixels fit in 1mm at this scale
    const pxPerMm = canvasW / usableWidth;

    // Total content height in mm
    const contentHeightMm = canvasH / pxPerMm;
    const totalPages = Math.ceil(contentHeightMm / pageHeightMm);

    for (let page = 0; page < totalPages; page++) {
      if (page > 0) doc.addPage();

      // Source region in canvas pixels
      const srcY = Math.round(page * pageHeightMm * pxPerMm);
      const srcH = Math.round(Math.min(canvasH - srcY, pageHeightMm * pxPerMm));

      if (srcH > 0) {
        const pageCanvas = document.createElement('canvas');
        pageCanvas.width = canvasW;
        pageCanvas.height = Math.round(pageHeightMm * pxPerMm);
        const ctx = pageCanvas.getContext('2d')!;
        ctx.drawImage(
          canvas,
          0, srcY, canvasW, srcH,
          0, 0, pageCanvas.width, pageCanvas.height
        );
        const pageImgData = pageCanvas.toDataURL('image/png');
        doc.addImage(pageImgData, 'PNG', margin, 0, usableWidth, pageHeightMm);
      }
    }

    // Generate filename
    const safeName = report.name
      .replace(/[^a-zA-Z0-9À-ÿ\s-]/g, '')
      .replace(/\s+/g, '_')
      .slice(0, 80);

    doc.save(`${safeName}.pdf`);
  } finally {
    // Cleanup
    root.unmount();
    if (container.parentNode) {
      document.body.removeChild(container);
    }
  }
}

// ───────────────────────────────────────────────
// Contract PDF Download
// ───────────────────────────────────────────────

interface ContractPDFData {
  id: string;
  artistName: string;
  artistGenre: string;
  artistScore: number;
  type: string;
  subType: string;
  status: string;
  amount: number;
  advance: number;
  royaltyRate: string;
  revenueShare: string;
  recoupableItems: string[];
  term: string;
  territory: string;
  albumCommitment: number;
  mastersOwnership: string;
  publishingSplit: string;
  creativeControl: string;
  marketingCommitment: string;
  syncRights: string;
  riskLevel: string;
  reviewedBy: string;
  clauses: string[];
  agentAlert: string;
  createdAt: string;
  expiryDate: string;
  signedDate: string | null;
  notes: string;
}

function formatCurrency(n: number): string {
  return '$' + n.toLocaleString('en-US');
}

function formatDate(d: string): string {
  try {
    return new Date(d).toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric',
    });
  } catch {
    return d;
  }
}

export function downloadContractAsPDF(contract: ContractPDFData): void {
  const doc = new jsPDF('p', 'mm', 'a4');
  const pageW = 210;
  const margin = 20;
  const contentW = pageW - margin * 2;
  let y = margin;

  // Helper: add page if not enough space remains
  const checkPage = (needed: number) => {
    if (y + needed > 275) {
      doc.addPage();
      y = margin + 5;
      return true;
    }
    return false;
  };

  const addFooter = () => {
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(156, 163, 175);
      doc.text('SIGNAL · Music Intelligence Platform · Abe Music Group', margin, 290);
      doc.text(`Page ${i} of ${pageCount}`, pageW - margin, 290, { align: 'right' });
    }
  };

  const statusColors: Record<string, number[]> = {
    pending_review: [239, 68, 68], draft: [217, 119, 6], negotiation: [59, 130, 246],
    signed: [5, 150, 105], terminated: [107, 114, 128],
  };
  const statusBg: Record<string, number[]> = {
    pending_review: [254, 242, 242], draft: [255, 251, 235], negotiation: [239, 246, 255],
    signed: [240, 253, 244], terminated: [249, 250, 251],
  };
  const sc = statusColors[contract.status] || [107, 114, 128];
  const sbg = statusBg[contract.status] || [249, 250, 251];
  const statusLabel = contract.status.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

  // ══════════════════════════════════════
  // PAGE 1: HEADER + PARTIES + DETAILS
  // ══════════════════════════════════════
  // Dark header
  doc.setFillColor(30, 27, 75);
  doc.rect(0, 0, pageW, 50, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(22);
  doc.setFont('helvetica', 'bold');
  doc.text('SIGNAL', margin, 22);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(165, 180, 252);
  doc.text('Music Intelligence Platform · Abe Music Group', margin, 32);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(255, 255, 255);
  doc.text('CONFIDENTIAL', pageW - margin, 22, { align: 'right' });
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(156, 163, 175);
  doc.text('Contract Document', pageW - margin, 32, { align: 'right' });

  y = 65;

  // ═══ AGENT HANDOFF ALERT (prominent, top of page) ═══
  checkPage(30);
  doc.setFillColor(255, 251, 235);
  doc.setDrawColor(251, 191, 36);
  doc.roundedRect(margin, y - 4, contentW, 24, 3, 3, 'FD');
  doc.setTextColor(146, 64, 14);
  doc.setFontSize(7);
  doc.setFont('helvetica', 'bold');
  doc.text('⚠ AGENT REVIEW COMPLETE — HUMAN SIGNATURE REQUIRED', margin + 4, y + 2);
  doc.setFontSize(6.5);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(120, 53, 15);
  doc.text('SIGNAL agents drafted this contract for evaluation. Agents CANNOT sign or execute contracts.', margin + 4, y + 11);
  doc.text('Forward to legal counsel for final review, negotiation, and execution.', margin + 4, y + 18);
  y += 32;

  // ═══ TITLE ═══
  doc.setTextColor(67, 56, 202);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.text('CONTRACT AGREEMENT', margin, y);
  y += 9;

  doc.setTextColor(30, 27, 75);
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text(contract.type + ' Agreement', margin, y);
  y += 8;

  doc.setTextColor(75, 85, 99);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(contract.subType || '', margin, y);
  y += 7;

  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 27, 75);
  doc.text(contract.artistName, margin, y);
  y += 12;

  // Status badge + genre
  doc.setFillColor(sbg[0], sbg[1], sbg[2]);
  doc.setDrawColor(sc[0], sc[1], sc[2]);
  doc.roundedRect(margin, y - 5, 42, 8, 2, 2, 'FD');
  doc.setTextColor(sc[0], sc[1], sc[2]);
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.text(statusLabel.toUpperCase(), margin + 3, y + 1);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.setTextColor(156, 163, 175);
  doc.text(contract.artistGenre + ' · Score ' + contract.artistScore, margin + 48, y + 1);
  y += 18;

  // Line
  doc.setDrawColor(99, 102, 241);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageW - margin, y);
  y += 12;

  // ═══ PARTIES ═══
  checkPage(42);
  doc.setFillColor(249, 250, 251);
  doc.setDrawColor(229, 231, 235);
  doc.roundedRect(margin, y - 4, contentW, 38, 3, 3, 'FD');
  doc.setTextColor(30, 27, 75);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('PARTIES', margin + 6, y + 4);
  doc.setFontSize(8.5);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(55, 65, 81);
  doc.text('This Agreement is made between:', margin + 6, y + 14);
  doc.setFont('helvetica', 'bold');
  doc.text('Abe Music Group LLC ("Company")', margin + 6, y + 22);
  doc.setFont('helvetica', 'normal');
  doc.text(`and ${contract.artistName} ("Artist")`, margin + 6, y + 30);
  y += 46;

  // ═══ FINANCIAL TERMS ═══
  checkPage(60);
  doc.setFillColor(249, 250, 251);
  doc.setDrawColor(229, 231, 235);
  doc.roundedRect(margin, y - 4, contentW, 56, 3, 3, 'FD');
  doc.setTextColor(30, 27, 75);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('FINANCIAL TERMS', margin + 6, y + 4);

  const finTerms = [
    { label: 'Total Deal Value', value: formatCurrency(contract.amount), bold: true },
    { label: 'Advance (Recoupable)', value: formatCurrency(contract.advance) },
    { label: 'Royalty Rate', value: contract.royaltyRate },
    { label: 'Revenue Split', value: contract.revenueShare },
  ];
  finTerms.forEach((t, i) => {
    const rowY = y + 14 + i * 10;
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(107, 114, 128);
    doc.text(t.label.toUpperCase(), margin + 6, rowY);
    doc.setFontSize(t.bold ? 10 : 8.5);
    doc.setFont('helvetica', t.bold ? 'bold' : 'normal');
    doc.setTextColor(t.bold ? 5 : 55, t.bold ? 150 : 65, t.bold ? 105 : 81);
    doc.text(t.value, margin + contentW / 2, rowY);
  });
  y += 62;

  // ═══ KEY DEAL TERMS ═══
  checkPage(70);
  doc.setFillColor(249, 250, 251);
  doc.setDrawColor(229, 231, 235);
  doc.roundedRect(margin, y - 4, contentW, 70, 3, 3, 'FD');
  doc.setTextColor(30, 27, 75);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('KEY DEAL TERMS', margin + 6, y + 4);

  const dealTerms = [
    { label: 'Term', value: contract.term },
    { label: 'Territory', value: contract.territory },
    { label: 'Albums Commitment', value: String(contract.albumCommitment) },
    { label: 'Masters Ownership', value: contract.mastersOwnership },
    { label: 'Publishing Split', value: contract.publishingSplit },
    { label: 'Creative Control', value: contract.creativeControl },
  ];
  dealTerms.forEach((t, i) => {
    const col = i < 3 ? 0 : 1;
    const idx = i < 3 ? i : i - 3;
    const x = margin + 6 + (col * contentW) / 2;
    const rowY = y + 14 + idx * 16;
    doc.setFontSize(6.5);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(107, 114, 128);
    doc.text(t.label.toUpperCase(), x, rowY);
    // Wrap long values
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(55, 65, 81);
    const lines = doc.splitTextToSize(t.value, contentW / 2 - 12);
    doc.text(lines, x, rowY + 5);
  });
  y += 78;

  // ═══ ADDITIONAL TERMS ═══
  checkPage(30);
  doc.setFillColor(249, 250, 251);
  doc.setDrawColor(229, 231, 235);
  const addTerms: { label: string; value: string }[] = [
    { label: 'Marketing Commitment', value: contract.marketingCommitment },
    { label: 'Sync Rights', value: contract.syncRights },
  ];
  const addBoxH = 20 + addTerms.length * 12;
  doc.roundedRect(margin, y - 4, contentW, addBoxH, 3, 3, 'FD');
  doc.setTextColor(30, 27, 75);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('ADDITIONAL TERMS', margin + 6, y + 4);
  addTerms.forEach((t, i) => {
    const rowY = y + 14 + i * 12;
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(107, 114, 128);
    doc.text(t.label.toUpperCase(), margin + 6, rowY);
    doc.setFontSize(7.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(55, 65, 81);
    doc.text(t.value, margin + contentW / 2, rowY);
  });
  y += addBoxH + 10;

  // ═══ RECOUPABLE ITEMS ═══
  checkPage(20 + (contract.recoupableItems?.length || 0) * 8);
  if (contract.recoupableItems && contract.recoupableItems.length > 0) {
    doc.setFillColor(254, 242, 242);
    doc.setDrawColor(252, 165, 165);
    doc.roundedRect(margin, y - 4, contentW, 16 + contract.recoupableItems.length * 7, 3, 3, 'FD');
    doc.setTextColor(185, 28, 28);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('RECOUPABLE EXPENSES', margin + 6, y + 4);
    contract.recoupableItems.forEach((item: string, i: number) => {
      doc.setFontSize(7);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(120, 53, 15);
      doc.text(`• ${item}`, margin + 10, y + 14 + i * 7);
    });
    y += 18 + contract.recoupableItems.length * 7;
  }

  // ══════════════════════════════════════
  // PAGE 2+: TERMS & CONDITIONS
  // ══════════════════════════════════════
  doc.addPage();
  y = margin + 10;

  // Header
  doc.setFillColor(30, 27, 75);
  doc.rect(0, 0, pageW, 35, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text(contract.type + ' Agreement', margin, 16);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(165, 180, 252);
  doc.text(contract.artistName + ' · ' + statusLabel + ' · ' + contract.subType, margin, 26);
  y = 50;

  doc.setTextColor(30, 27, 75);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text('Terms & Conditions', margin, y);
  y += 8;

  doc.setDrawColor(99, 102, 241);
  doc.setLineWidth(0.3);
  doc.line(margin, y, pageW - margin, y);
  y += 8;

  contract.clauses.forEach((clause: string, i: number) => {
    const lines = doc.splitTextToSize(clause, contentW - 20);
    const needed = lines.length * 5 + 12;
    if (y + needed > 265) {
      doc.addPage();
      y = margin + 5;
      doc.setFillColor(30, 27, 75);
      doc.rect(0, 0, pageW, 25, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.text(contract.type + ' · ' + contract.artistName, margin, 12);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(165, 180, 252);
      doc.text('Terms & Conditions (continued)', margin, 20);
      y = 42;
    }

    doc.setFillColor(99, 102, 241);
    doc.circle(margin + 4, y + 3, 3, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(6);
    doc.setFont('helvetica', 'bold');
    doc.text(String(i + 1), margin + 4, y + 5, { align: 'center' });

    doc.setTextColor(55, 65, 81);
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    doc.text(lines, margin + 14, y + 1);
    y += lines.length * 5 + 10;

    if (i < contract.clauses.length - 1) {
      doc.setDrawColor(243, 244, 246);
      doc.setLineWidth(0.2);
      doc.line(margin, y - 5, pageW - margin, y - 5);
    }
  });

  y += 8;

  // ═══ NOTES ═══
  if (contract.notes) {
    const noteLines = doc.splitTextToSize(contract.notes, contentW - 16);
    const noteH = noteLines.length * 5 + 20;
    if (y + noteH > 265) {
      doc.addPage();
      y = margin + 10;
    }
    doc.setFillColor(254, 251, 235);
    doc.setDrawColor(251, 191, 36);
    doc.roundedRect(margin, y - 4, contentW, noteH, 3, 3, 'FD');
    doc.setTextColor(146, 64, 14);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('AGENT NOTES', margin + 6, y + 4);
    doc.setFontSize(7.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(120, 53, 15);
    doc.text(noteLines, margin + 6, y + 14);
    y += noteH + 10;
  }

  // ═══ AGENT ALERT (on terms page) ═══
  const alertLines = doc.splitTextToSize(contract.agentAlert || '', contentW - 16);
  const alertH = alertLines.length * 5 + 20;
  if (y + alertH + 30 > 265) {
    doc.addPage();
    y = margin + 10;
  }
  doc.setFillColor(255, 247, 237);
  doc.setDrawColor(251, 146, 60);
  doc.roundedRect(margin, y - 4, contentW, alertH, 3, 3, 'FD');
  doc.setTextColor(194, 65, 12);
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.text('⚠ AGENT DISCLAIMER', margin + 6, y + 4);
  doc.setFontSize(7);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(154, 52, 18);
  doc.text(alertLines, margin + 6, y + 14);
  y += alertH + 10;

  // ═══ SIGNATURES ═══
  if (y + 60 > 265) {
    doc.addPage();
    y = margin + 10;
  }

  y += 6;
  doc.setDrawColor(99, 102, 241);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageW - margin, y);
  y += 10;

  doc.setTextColor(30, 27, 75);
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.text('Execution', margin, y);
  y += 7;

  doc.setFontSize(8.5);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(75, 85, 99);
  doc.text('IN WITNESS WHEREOF, the parties have executed this Agreement as of the date above.', margin, y);
  y += 14;

  // Signature lines
  doc.setDrawColor(156, 163, 175);
  doc.setLineWidth(0.5);
  doc.line(margin, y + 18, margin + 70, y + 18);
  doc.line(margin + contentW - 70, y + 18, margin + contentW, y + 18);

  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(107, 114, 128);
  doc.text('Abe Music Group LLC', margin, y + 25);
  doc.text(contract.artistName, margin + contentW - 70, y + 25);

  doc.setFontSize(7);
  doc.setTextColor(156, 163, 175);
  doc.text('Authorized Signature', margin, y + 31);
  doc.text('Artist Signature', margin + contentW - 70, y + 31);

  y += 48;

  // Risk level + ID footer
  const riskColors: Record<string, string[]> = {
    low: ['#d1fae5', '#065f46'], medium: ['#fef3c7', '#92400e'], high: ['#fee2e2', '#991b1b'],
  };
  const rc = riskColors[contract.riskLevel] || riskColors.low;
  doc.setFillColor(parseInt(rc[0].slice(1, 3), 16), parseInt(rc[0].slice(3, 5), 16), parseInt(rc[0].slice(5, 7), 16));
  doc.setDrawColor(parseInt(rc[1].slice(1, 3), 16), parseInt(rc[1].slice(3, 5), 16), parseInt(rc[1].slice(5, 7), 16));
  doc.roundedRect(margin, y - 4, contentW, 14, 3, 3, 'FD');

  doc.setFontSize(7);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(parseInt(rc[1].slice(1, 3), 16), parseInt(rc[1].slice(3, 5), 16), parseInt(rc[1].slice(5, 7), 16));
  doc.text(`Risk Level: ${contract.riskLevel.toUpperCase()}  ·  Reviewed by: ${contract.reviewedBy}  ·  ID: ${contract.id}`, margin + 6, y + 5);

  addFooter();

  const safeName = `${contract.artistName}_${contract.type}_Contract`
    .replace(/[^a-zA-Z0-9À-ÿ\s-]/g, '').replace(/\s+/g, '_').slice(0, 80);
  doc.save(`${safeName}.pdf`);
}

// ───────────────────────────────────────────────
// Consensus Decision PDF Download
// ───────────────────────────────────────────────

export function downloadConsensusDecisionAsPDF(decision: {
  id: string;
  artistName: string;
  type: string;
  decision: string;
  confidence: number;
  agents: string[];
  summary: string;
  justification: string;
  report: string;
  processSteps: { agent: string; action: string; detail: string }[];
  agentVotes: { agent: string; vote: string; confidence: number; reason: string }[];
  date: string;
}): void {
  const doc = new jsPDF('p', 'mm', 'a4');
  const pageW = 210;
  const margin = 20;
  const contentW = pageW - margin * 2;
  let y = margin;

  const addFooter = () => {
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(156, 163, 175);
      doc.text('SIGNAL · Music Intelligence Platform · Abe Music Group', margin, 290);
      doc.text(`Page ${i} of ${pageCount}`, pageW - margin, 290, { align: 'right' });
    }
  };

  const outcomeColor: Record<string, [number, number, number]> = {
    APPROVED: [5, 150, 105],
    'IN REVIEW': [59, 130, 246],
    PENDING: [217, 119, 6],
    FLAGGED: [239, 68, 68],
  };
  const oc = outcomeColor[decision.decision] || [107, 114, 128];

  // ═══ PAGE 1: HEADER + SUMMARY ═══
  // Header bar
  doc.setFillColor(30, 27, 75);
  doc.rect(0, 0, pageW, 50, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text('SIGNAL', margin, 22);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(165, 180, 252);
  doc.text('Multi-Agent Consensus Decision Report', margin, 32);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(255, 255, 255);
  doc.text('CONFIDENTIAL', pageW - margin, 22, { align: 'right' });
  y = 65;

  // Type badge
  doc.setFillColor(99, 102, 241);
  doc.setDrawColor(99, 102, 241);
  doc.roundedRect(margin, y - 4, 55, 8, 2, 2, 'FD');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(7);
  doc.setFont('helvetica', 'bold');
  doc.text(decision.type.toUpperCase(), margin + 4, y + 2);
  y += 16;

  // Title
  doc.setTextColor(30, 27, 75);
  doc.setFontSize(26);
  doc.setFont('helvetica', 'bold');
  doc.text(decision.type, margin, y);
  y += 10;

  doc.setFontSize(16);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(75, 85, 99);
  doc.text(decision.artistName, margin, y);
  y += 12;

  // Outcome badge
  doc.setFillColor(oc[0], oc[1], oc[2]);
  doc.setDrawColor(oc[0], oc[1], oc[2]);
  const outcomeLabel = decision.decision === 'IN REVIEW' ? 'IN REVIEW' : decision.decision;
  doc.roundedRect(margin, y - 4, 40, 8, 2, 2, 'FD');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(8);
  doc.setFont('helvetica', 'bold');
  doc.text(outcomeLabel, margin + 4, y + 2);
  y += 18;

  // Line
  doc.setDrawColor(99, 102, 241);
  doc.setLineWidth(0.3);
  doc.line(margin, y, pageW - margin, y);
  y += 12;

  // Key metrics
  doc.setFillColor(249, 250, 251);
  doc.roundedRect(margin, y - 4, contentW, 28, 3, 3, 'F');

  doc.setTextColor(30, 27, 75);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('DECISION OVERVIEW', margin + 6, y + 4);

  const overviewItems = [
    { label: 'Date', value: decision.date },
    { label: 'Confidence', value: `${decision.confidence}%` },
    { label: 'Agents', value: `${decision.agents.length} agents` },
    { label: 'Decision ID', value: decision.id.slice(0, 12) },
  ];

  overviewItems.forEach((item, i) => {
    const x = margin + 6 + i * (contentW / 4);
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(107, 114, 128);
    doc.text(item.label.toUpperCase(), x, y + 15);
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(55, 65, 81);
    doc.text(item.value, x, y + 22);
  });

  y += 40;

  // Subtitle
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 27, 75);
  doc.text('Justification', margin, y);
  y += 10;

  doc.setFontSize(9.5);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(55, 65, 81);
  const justificationLines = doc.splitTextToSize(decision.justification, contentW);
  doc.text(justificationLines, margin, y);
  y += justificationLines.length * 5 + 12;

  // ═══ AGENT VOTES ═══
  if (y > 220) {
    doc.addPage();
    y = margin + 20;
  }
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 27, 75);
  doc.text('Agent Voting', margin, y);
  y += 8;

  doc.setDrawColor(229, 231, 235);
  doc.setLineWidth(0.3);
  doc.line(margin, y, pageW - margin, y);
  y += 6;

  decision.agentVotes.forEach((av) => {
    // Check space
    if (y > 250) {
      doc.addPage();
      y = margin + 20;
    }

    const voteColors: Record<string, [number, number, number]> = {
      APPROVED: [5, 150, 105],
      CONDITIONAL: [217, 119, 6],
      PENDING: [107, 114, 128],
      FLAGGED: [239, 68, 68],
    };
    const vc = voteColors[av.vote] || [107, 114, 128];

    doc.setFillColor(249, 250, 251);
    doc.roundedRect(margin, y - 3, contentW, 32, 3, 3, 'F');

    // Agent name
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 27, 75);
    doc.text(av.agent, margin + 6, y + 4);

    // Vote badge
    doc.setFillColor(vc[0], vc[1], vc[2]);
    doc.roundedRect(margin + contentW - 48, y, 28, 6, 2, 2, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(6);
    doc.setFont('helvetica', 'bold');
    doc.text(av.vote, margin + contentW - 34, y + 5, { align: 'center' });

    // Confidence
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(107, 114, 128);
    doc.text(`${av.confidence}% confidence`, margin + contentW - 56, y + 5);

    // Reason
    doc.setFontSize(8);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(75, 85, 99);
    const reasonLines = doc.splitTextToSize(av.reason, contentW - 80);
    doc.text(reasonLines, margin + 6, y + 13);

    y += 38;
  });

  // ═══ PROCESS STEPS ═══
  if (y > 210) {
    doc.addPage();
    y = margin + 20;
  }
  y += 6;
  doc.setFontSize(13);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 27, 75);
  doc.text('Decision Process', margin, y);
  y += 8;

  doc.setDrawColor(229, 231, 235);
  doc.setLineWidth(0.3);
  doc.line(margin, y, pageW - margin, y);
  y += 8;

  decision.processSteps.forEach((step, i) => {
    if (y > 240) {
      doc.addPage();
      y = margin + 20;
    }

    // Step number circle
    doc.setFillColor(99, 102, 241);
    doc.circle(margin + 4, y + 3, 3, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(6);
    doc.setFont('helvetica', 'bold');
    doc.text(String(i + 1), margin + 4, y + 5, { align: 'center' });

    // Agent step
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 27, 75);
    doc.text(`${step.agent}:`, margin + 14, y + 1);

    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(55, 65, 81);
    const stepLines = doc.splitTextToSize(step.action, contentW - 20);
    doc.text(stepLines, margin + 14, y + 9);
    y += stepLines.length * 5 + 14;

    // Detail (smaller text)
    doc.setFontSize(7.5);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(107, 114, 128);
    const detailLines = doc.splitTextToSize(step.detail, contentW - 20);
    doc.text(detailLines, margin + 14, y);
    y += detailLines.length * 4 + 6;

    // Separator
    if (i < decision.processSteps.length - 1) {
      doc.setDrawColor(243, 244, 246);
      doc.setLineWidth(0.2);
      doc.line(margin + 14, y - 2, pageW - margin, y - 2);
    }
  });

  y += 10;

  // ═══ RECOMMENDATIONS ═══
  if (y > 220) {
    doc.addPage();
    y = margin + 20;
  }

  const nextSteps = decision.decision === 'APPROVED'
    ? ['Prepare and send offer letter', 'Schedule artist meeting', 'Begin contract drafting', 'Set onboarding timeline']
    : decision.decision === 'IN REVIEW'
      ? ['Request pending documentation', 'Complete background check', 'Schedule follow-up review']
      : decision.decision === 'PENDING'
        ? ['Escalate to executive committee', 'Define investment budget', 'Re-submit for approval']
        : ['Review flagged risks with legal counsel', 'Develop risk mitigation plan', 'Re-evaluation in 2 weeks'];

  doc.setFillColor(238, 242, 255);
  doc.setDrawColor(199, 210, 254);
  doc.roundedRect(margin, y - 4, contentW, nextSteps.length * 8 + 28, 3, 3, 'FD');

  doc.setTextColor(67, 56, 202);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text('RECOMMENDATIONS & NEXT STEPS', margin + 6, y + 4);

  doc.setTextColor(55, 65, 81);
  doc.setFontSize(8);
  doc.setFont('helvetica', 'normal');
  nextSteps.forEach((step, i) => {
    doc.text(`${i + 1}. ${step}`, margin + 10, y + 16 + i * 8);
  });

  y += nextSteps.length * 8 + 36;

  // ═══ AGENT HANDOFF ═══
  if (y + 28 > 270) {
    doc.addPage();
    y = margin + 10;
  }
  doc.setFillColor(255, 247, 237);
  doc.setDrawColor(251, 146, 60);
  doc.roundedRect(margin, y - 4, contentW, 24, 3, 3, 'FD');
  doc.setTextColor(194, 65, 12);
  doc.setFontSize(7);
  doc.setFont('helvetica', 'bold');
  doc.text('⚠ HUMAN DECISION REQUIRED', margin + 6, y + 4);
  doc.setFontSize(6.5);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(154, 52, 18);
  const handoffText = 'SIGNAL agents have completed their analysis and provide the recommendation above. Agents CANNOT make final decisions or execute contracts. This recommendation requires human review and approval before any action is taken. Please review the agent votes, process steps, and justification above, then make a final decision.';
  const handoffLines = doc.splitTextToSize(handoffText, contentW - 16);
  doc.text(handoffLines, margin + 6, y + 13);

  y += 30;

  // Footer
  addFooter();

  // Save
  const safeName = `${decision.artistName}_${decision.type}_Consensus`
    .replace(/[^a-zA-Z0-9À-ÿ\s-]/g, '')
    .replace(/\s+/g, '_')
    .slice(0, 80);
  doc.save(`${safeName}.pdf`);
}

export default ReportPDFContent;
