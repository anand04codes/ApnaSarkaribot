import React, { useState } from 'react';
import { X, Copy, Check, Download, ExternalLink, ShieldAlert } from 'lucide-react';

export default function ComplaintModal({ complaint, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !complaint) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(complaint.summary_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (e) {
      // Fallback
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([complaint.summary_text], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = `cybercrime_complaint_${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 relative max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-red-100 text-red-700 dark:bg-red-950/60 dark:text-red-300 rounded-xl">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-black text-slate-900 dark:text-white">
                Official Complaint Draft (Ready to Paste)
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Formatted for National Cyber Crime Portal (cybercrime.gov.in) & 1930
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content body */}
        <div className="my-4 overflow-y-auto flex-1">
          <div className="grid grid-cols-2 gap-2 text-xs mb-3 bg-slate-50 dark:bg-slate-950 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
            <div>
              <span className="font-bold text-slate-500">Scam Type:</span>
              <p className="font-semibold text-slate-800 dark:text-slate-200">{complaint.scam_category}</p>
            </div>
            <div>
              <span className="font-bold text-slate-500">Impersonated:</span>
              <p className="font-semibold text-slate-800 dark:text-slate-200">{complaint.claimed_agency || 'N/A'}</p>
            </div>
            <div>
              <span className="font-bold text-slate-500">Demanded Amount:</span>
              <p className="font-semibold text-red-600 dark:text-red-400">{complaint.demanded_amount || 'None noted'}</p>
            </div>
            <div>
              <span className="font-bold text-slate-500">Suspect Phone(s):</span>
              <p className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                {complaint.suspect_numbers?.join(', ') || 'None found'}
              </p>
            </div>
          </div>

          <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 block">
            Generated Statement:
          </label>
          <pre className="p-3.5 bg-slate-100 dark:bg-slate-950 rounded-xl text-xs font-mono text-slate-800 dark:text-slate-200 whitespace-pre-wrap overflow-x-auto border border-slate-200 dark:border-slate-800 leading-relaxed select-all">
            {complaint.summary_text}
          </pre>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-100 dark:border-slate-800">
          <a
            href="https://cybercrime.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 dark:text-sky-400 hover:underline"
          >
            Open cybercrime.gov.in Portal
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs sm:text-sm transition-all"
            >
              <Download className="w-4 h-4" />
              Download .txt
            </button>

            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm shadow-md transition-all active:scale-95"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy Complaint
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

