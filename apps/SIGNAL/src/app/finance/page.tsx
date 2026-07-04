'use client';

import { DashboardLayout } from '@/components/dashboard/layout';
import { Wallet, TrendingUp, TrendingDown, DollarSign, BarChart3, PieChart, ArrowUpRight, ArrowDownRight, Loader2, AlertCircle } from 'lucide-react';
import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(r => r.json());

function formatCurrency(n: number) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 0 }).format(n);
}

const t = (es: string, en: string) => `${es} / ${en}`;

function SkeletonCard() {
  return <div className="rounded-xl border bg-card p-4 space-y-3 animate-pulse"><div className="h-3 w-20 bg-muted rounded" /><div className="h-7 w-20 bg-muted rounded" /><div className="h-3 w-16 bg-muted rounded" /></div>;
}

function SkeletonBar() {
  return <div className="space-y-3"><div className="h-4 w-32 bg-muted rounded mb-4" />{[...Array(6)].map((_, i) => <div key={i} className="space-y-1"><div className="flex justify-between"><div className="h-3 w-20 bg-muted rounded" /><div className="h-3 w-16 bg-muted rounded" /></div><div className="h-2 rounded-full bg-muted" /></div>)}</div>;
}

function SkeletonTable() {
  return <div className="space-y-3"><div className="h-4 w-36 bg-muted rounded mb-4" />{[...Array(5)].map((_, i) => <div key={i} className="flex items-center justify-between p-3"><div className="h-3 w-28 bg-muted rounded" /><div className="h-3 w-20 bg-muted rounded" /></div>)}</div>;
}

export default function FinancePage() {
  const { data, error, isLoading } = useSWR('/api/v1/finance', fetcher, { revalidateOnFocus: false });

  const expenseEntries = data?.expenses ? Object.entries(data.expenses).filter(([k]) => k !== 'total') : [];
  const revenueEntries = data?.revenue ? Object.entries(data.revenue).filter(([k]) => k !== 'total') : [];

  const totalRevenue = data?.revenue?.total ?? 0;
  const totalExpenses = data?.expenses?.total ?? 0;
  const profitMargin = totalRevenue > 0 ? ((totalRevenue - totalExpenses) / totalRevenue * 100).toFixed(1) : '0.0';

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('Vista Financiera', 'Financial View')}</h1>
          <p className="text-muted-foreground mt-1">{t('Ingresos, gastos y proyecciones', 'Revenue tracking, expenses, and financial forecasts')}</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-500">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <div>
              <p className="text-sm font-medium">{t('Error al cargar datos', 'Failed to load financial data')}</p>
              <p className="text-xs text-red-400/80 mt-0.5">{error.message}</p>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}

        {isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SkeletonBar />
            <SkeletonTable />
          </div>
        )}

        {data && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="rounded-xl border bg-card p-4 hover:border-primary/30 transition-colors">
                <p className="text-xs text-muted-foreground mb-1">{t('Presupuesto Total', 'Total Budget')} ({data.summary.fiscalYear})</p>
                <p className="text-2xl font-bold text-green-500">{formatCurrency(data.summary.totalBudget)}</p>
                <div className="flex items-center gap-2 mt-1 text-xs">
                  <span className="text-muted-foreground">{t('Asignado', 'Allocated')}: {formatCurrency(data.summary.allocated)}</span>
                  <span className={`font-medium ${data.summary.remaining >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {t('Restante', 'Remaining')}: {formatCurrency(data.summary.remaining)}
                  </span>
                </div>
              </div>
              <div className="rounded-xl border bg-card p-4 hover:border-primary/30 transition-colors">
                <p className="text-xs text-muted-foreground mb-1">{t('Ingreso Total', 'Total Revenue')}</p>
                <p className="text-2xl font-bold text-emerald-500">{formatCurrency(totalRevenue)}</p>
                {data.projectedVsActual && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {t('Proyectado', 'Projected')}: {formatCurrency(data.projectedVsActual.projected)}
                  </p>
                )}
              </div>
              <div className="rounded-xl border bg-card p-4 hover:border-primary/30 transition-colors">
                <p className="text-xs text-muted-foreground mb-1">{t('Gastos Totales', 'Total Expenses')}</p>
                <p className="text-2xl font-bold text-red-500">{formatCurrency(totalExpenses)}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {t('Variación', 'Variance')}: {data.projectedVsActual?.variance || 'N/A'}
                </p>
              </div>
              <div className="rounded-xl border bg-card p-4 hover:border-primary/30 transition-colors">
                <p className="text-xs text-muted-foreground mb-1">{t('Margen de Ganancia', 'Profit Margin')}</p>
                <p className={`text-2xl font-bold ${Number(profitMargin) >= 0 ? 'text-emerald-500' : 'text-red-500'}`}>{profitMargin}%</p>
                {data.projectedVsActual && (
                  <p className="text-xs text-muted-foreground mt-1">{data.projectedVsActual.note}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Revenue Streams */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-primary" />
                  {t('Fuentes de Ingreso', 'Revenue Streams')}
                </h2>
                <div className="space-y-4">
                  {revenueEntries.map(([key, val]: [string, any], i: number) => {
                    const pct = totalRevenue > 0 ? ((val / totalRevenue) * 100).toFixed(1) : '0';
                    return (
                      <div key={key}>
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="font-medium capitalize">{key}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs text-muted-foreground">{formatCurrency(val)}</span>
                            <span className="text-xs text-muted-foreground">{pct}%</span>
                          </div>
                        </div>
                        <div className="h-2 rounded-full bg-muted overflow-hidden">
                          <div className="h-full rounded-full bg-primary transition-all duration-500" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Expenses */}
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-primary" />
                  {t('Desglose de Gastos', 'Expense Breakdown')}
                </h2>
                <div className="space-y-4">
                  {expenseEntries.map(([key, val]: [string, any], i: number) => {
                    const pct = totalExpenses > 0 ? ((val / totalExpenses) * 100).toFixed(1) : '0';
                    const colors = ['bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-purple-500', 'bg-cyan-500'];
                    return (
                      <div key={key}>
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span className="font-medium capitalize">{key === 'aAndR' ? 'A&R' : key}</span>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs text-muted-foreground">{formatCurrency(val)}</span>
                            <span className="text-xs text-muted-foreground">{pct}%</span>
                          </div>
                        </div>
                        <div className="h-2 rounded-full bg-muted overflow-hidden">
                          <div className={`h-full rounded-full ${colors[i % colors.length]} transition-all duration-500`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Deals Table */}
            <div className="rounded-xl border bg-card p-5">
              <h2 className="font-semibold mb-4 flex items-center gap-2">
                <PieChart className="h-4 w-4 text-primary" />
                {t('Acuerdos y Costos', 'Deals & Cost Breakdown')}
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground text-xs">
                      <th className="text-left py-2 pr-4 font-medium">{t('Artista', 'Artist')}</th>
                      <th className="text-left py-2 pr-4 font-medium">{t('Tipo', 'Type')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Valor', 'Value')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Adelanto', 'Advance')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Marketing', 'Marketing')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Producción', 'Production')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Legal', 'Legal')}</th>
                      <th className="text-right py-2 pr-4 font-medium">{t('Operaciones', 'Ops')}</th>
                      <th className="text-right py-2 font-medium">ROI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.deals.map((d: any, i: number) => (
                      <tr key={i} className="border-b last:border-0 hover:bg-accent/30 transition-colors">
                        <td className="py-3 pr-4 font-medium">{d.name}</td>
                        <td className="py-3 pr-4 text-xs text-muted-foreground">{d.type}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.value)}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.costBreakdown.advance)}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.costBreakdown.marketing)}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.costBreakdown.production)}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.costBreakdown.legal)}</td>
                        <td className="py-3 pr-4 text-right font-mono text-xs">{formatCurrency(d.costBreakdown.operations)}</td>
                        <td className="py-3 text-right">
                          <span className="text-xs font-medium text-green-500">{d.roi}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Projected vs Actual */}
            {data.projectedVsActual && (
              <div className="rounded-xl border bg-card p-5">
                <h2 className="font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  {t('Proyectado vs Real', 'Projected vs Actual')}
                </h2>
                <div className="flex flex-wrap items-center gap-6">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">{t('Proyectado', 'Projected')}</p>
                    <p className="text-lg font-bold">{formatCurrency(data.projectedVsActual.projected)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">{t('Real', 'Actual')}</p>
                    <p className="text-lg font-bold">{formatCurrency(data.projectedVsActual.actual)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">{t('Variación', 'Variance')}</p>
                    <p className={`text-lg font-bold flex items-center gap-1 ${data.projectedVsActual.variance.startsWith('-') ? 'text-red-500' : 'text-green-500'}`}>
                      {data.projectedVsActual.variance.startsWith('-') ? <ArrowDownRight className="h-4 w-4" /> : <ArrowUpRight className="h-4 w-4" />}
                      {data.projectedVsActual.variance}
                    </p>
                  </div>
                  <div className="text-xs text-muted-foreground italic">{data.projectedVsActual.note}</div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
