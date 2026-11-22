import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { TrendingUp, ShieldAlert, CheckCircle, AlertTriangle, Layers, Info, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';

const COLORS = ['#DC2626', '#EA580C', '#D97706', '#2563EB', '#7C3AED', '#059669', '#0891B2', '#4B5563'];

export default function TrendingDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const data = await apiClient.getDashboardStats();
        setStats(data);
      } catch (err) {
        setError(err.message || 'Failed to load public stats');
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-2" />
        <p className="text-sm font-semibold">Loading Public Cyber Crime Intelligence Dashboard...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="text-center py-16 text-red-600 font-bold">
        Failed to load statistics: {error}
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Banner with Sample Data Alert */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600 dark:text-sky-400" />
            <h2 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
              Anonymized Citizen Threat Intelligence Dashboard
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Aggregated trends across India. Strictly NO personal messages, phone numbers, or user files are ever stored.
          </p>
        </div>

        {stats.is_sample_data && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-100 text-amber-900 dark:bg-amber-950/70 dark:text-amber-200 text-xs font-bold border border-amber-300 dark:border-amber-800 self-start sm:self-auto">
            <Info className="w-4 h-4 flex-shrink-0" />
            <span>Sample Data Displayed (Fresh Clone Mode)</span>
          </div>
        )}
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Checks</span>
          <p className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-1">
            {stats.total_checks}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-red-600 dark:text-red-400">Scams Caught</span>
            <ShieldAlert className="w-4 h-4 text-red-600" />
          </div>
          <p className="text-2xl sm:text-3xl font-black text-red-600 dark:text-red-400 mt-1">
            {stats.scams_detected}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-600 dark:text-amber-400">Suspicious</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-2xl sm:text-3xl font-black text-amber-600 dark:text-amber-400 mt-1">
            {stats.suspicious_detected}
          </p>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Genuine Notices</span>
            <CheckCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <p className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-1">
            {stats.genuine_detected}
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: 30-Day Trend */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            Verification Activity (Last 30 Days)
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.daily_trends}>
                <defs>
                  <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <YAxis tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px'
                  }}
                />
                <Area type="monotone" dataKey="checks" stroke="#2563EB" fillOpacity={1} fill="url(#trendGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Top Scam Categories */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-red-600" />
            Top Detected Scam Schemes
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.scam_type_breakdown} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="value" fill="#DC2626" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Top Red Flags */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            Most Common Attack Vectors (Red Flags)
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.top_red_flags}>
                <XAxis dataKey="category" tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <YAxis tick={{ fontSize: 10 }} stroke="#94A3B8" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" fill="#EA580C" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Language Distribution */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-600" />
            Language Distribution of Queries
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.language_distribution}
                  dataKey="count"
                  nameKey="language"
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {stats.language_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

