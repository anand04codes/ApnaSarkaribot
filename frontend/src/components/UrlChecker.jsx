import React, { useState } from 'react';
import { Search, Globe, ShieldCheck, ShieldAlert, AlertTriangle, Lock, Unlock, Loader2, ArrowRight } from 'lucide-react';
import { apiClient } from '../api/client';

export default function UrlChecker() {
  const [urlInput, setUrlInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInspect = async (targetUrl) => {
    const checkUrl = targetUrl || urlInput;
    if (!checkUrl.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.checkUrl(checkUrl);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Inspection failed');
    } finally {
      setLoading(false);
    }
  };

  const sampleUrls = [
    { label: 'Official Portal (Income Tax)', url: 'https://incometax.gov.in' },
    { label: 'Lookalike Phishing Spoof', url: 'http://incometax-gov.in/portal/login' },
    { label: 'Suspicious TLD (.xyz)', url: 'http://sbi-kyc-verify.xyz/update' },
    { label: 'Malicious APK Link', url: 'http://echallan-parivahan.top/challan.apk' }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <Globe className="w-5 h-5 text-blue-600 dark:text-sky-400" />
          <h2 className="text-xl font-black text-slate-900 dark:text-white">
            Static Link & Typo-Squatting Checker
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mb-4">
          Safe static inspection: Analyzes look-alike domains, URL shorteners, punycode, and suspicious TLDs without navigating to the target website.
        </p>

        {/* Input Bar */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
            <input
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleInspect()}
              placeholder="Paste suspicious website link (e.g. incometax-gov.in or bit.ly/pm-kisan)"
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <button
            onClick={() => handleInspect()}
            disabled={loading || !urlInput.trim()}
            className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Inspect Link'}
          </button>
        </div>

        {/* Quick Samples */}
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400 block mb-2">
            Try test links:
          </span>
          <div className="flex flex-wrap gap-2">
            {sampleUrls.map((s, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setUrlInput(s.url);
                  handleInspect(s.url);
                }}
                className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-slate-700 transition-colors"
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <p className="mt-3 text-xs text-red-600 dark:text-red-400 font-bold">
            {error}
          </p>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-extrabold tracking-widest text-slate-400">
                Inspection Verdict
              </span>
              <div className="flex items-center gap-2 mt-0.5">
                <span
                  className={`text-xl font-black px-3 py-1 rounded-xl uppercase tracking-wider ${
                    result.verdict === 'LIKELY SCAM'
                      ? 'bg-red-100 text-red-800 dark:bg-red-950/80 dark:text-red-300'
                      : result.verdict === 'SUSPICIOUS'
                      ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300'
                      : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300'
                  }`}
                >
                  {result.verdict}
                </span>
                <span className="text-sm font-bold text-slate-600 dark:text-slate-300">
                  Risk Score: {result.risk_score} / 100
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {result.has_https ? (
                <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-lg">
                  <Lock className="w-3.5 h-3.5" /> HTTPS Encrypted
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs font-bold text-red-600 bg-red-50 dark:bg-red-950/40 px-2.5 py-1 rounded-lg">
                  <Unlock className="w-3.5 h-3.5" /> Unencrypted HTTP
                </span>
              )}
            </div>
          </div>

          {/* Grid Indicators */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <span className="text-slate-500 font-semibold block">Official Registry</span>
              <span className="font-extrabold text-sm text-slate-800 dark:text-white">
                {result.is_safe_domain ? '✅ Verified Official' : '❌ Unofficial'}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <span className="text-slate-500 font-semibold block">Look-Alike Spoof</span>
              <span className={`font-extrabold text-sm ${result.is_lookalike ? 'text-red-600' : 'text-slate-800 dark:text-white'}`}>
                {result.is_lookalike ? `🚨 Spoofs ${result.lookalike_target}` : 'None detected'}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <span className="text-slate-500 font-semibold block">Link Shortener</span>
              <span className="font-extrabold text-sm text-slate-800 dark:text-white">
                {result.is_shortener ? '⚠️ Shortened URL' : 'Direct URL'}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <span className="text-slate-500 font-semibold block">Domain TLD</span>
              <span className={`font-extrabold text-sm ${result.suspicious_tld ? 'text-red-600' : 'text-slate-800 dark:text-white'}`}>
                {result.suspicious_tld ? '🚩 High-Risk TLD' : 'Standard TLD'}
              </span>
            </div>
          </div>

          {/* Reasons List */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
              Detailed Findings:
            </h4>
            <ul className="space-y-1.5 text-xs sm:text-sm">
              {result.reasons?.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-700 dark:text-slate-300 font-medium">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* WHOIS Information */}
          {result.whois_info && (
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs">
              <span className="font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Domain Registration Metadata (WHOIS):
              </span>
              <div className="grid grid-cols-2 gap-2 text-slate-700 dark:text-slate-300">
                <div>
                  <span className="font-semibold text-slate-500">Registrar:</span> {result.whois_info.registrar || 'N/A'}
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Created:</span> {result.whois_info.creation_date || 'N/A'}
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Status:</span> {result.whois_info.status || 'Active'}
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Country:</span> {result.whois_info.country || 'N/A'}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

