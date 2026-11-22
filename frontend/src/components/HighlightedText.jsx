import React, { useState } from 'react';
import { AlertCircle, Tag, Eye } from 'lucide-react';

export default function HighlightedText({ text, redFlags }) {
  const [activeFlag, setActiveFlag] = useState(null);

  if (!text) return null;
  const flags = redFlags || [];

  // If no flags, render text normally
  if (flags.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 flex items-center gap-2">
          <Eye className="w-4 h-4 text-emerald-500" />
          Submitted Content
        </h3>
        <p className="text-sm sm:text-base leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
          {text}
        </p>
      </div>
    );
  }

  // Highlight matches in text
  // Sort flags by position or length
  const renderHighlighted = () => {
    let result = [];
    let lowerText = text.toLowerCase();
    let currentIdx = 0;

    // Collect all match spans
    let matches = [];
    flags.forEach((flag, flagIdx) => {
      const span = (flag.text_span || '').toLowerCase().trim();
      if (!span) return;

      let start = lowerText.indexOf(span);
      while (start !== -1) {
        matches.push({
          start,
          end: start + span.length,
          flag,
          flagIdx
        });
        start = lowerText.indexOf(span, start + span.length);
      }
    });

    // Sort by start position
    matches.sort((a, b) => a.start - b.start);

    // Merge overlapping
    let nonOverlapping = [];
    let lastEnd = 0;
    matches.forEach((m) => {
      if (m.start >= lastEnd) {
        nonOverlapping.push(m);
        lastEnd = m.end;
      }
    });

    // Build segments
    let lastPos = 0;
    nonOverlapping.forEach((m, i) => {
      if (m.start > lastPos) {
        result.push(text.slice(lastPos, m.start));
      }
      const matchedString = text.slice(m.start, m.end);
      const isSelected = activeFlag === m.flag;

      result.push(
        <mark
          key={`m-${i}`}
          onClick={() => setActiveFlag(isSelected ? null : m.flag)}
          className={`highlight-scam cursor-pointer transition-all ${
            isSelected ? 'ring-2 ring-red-600 bg-red-300 dark:bg-red-900' : ''
          }`}
          title={`${m.flag.category}: ${m.flag.reason}`}
        >
          {matchedString}
        </mark>
      );
      lastPos = m.end;
    });

    if (lastPos < text.length) {
      result.push(text.slice(lastPos));
    }

    return result;
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-3 border-b border-slate-100 dark:border-slate-800 pb-2">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500" />
          Evidence View (Click highlighted red flags)
        </h3>
        <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200 font-bold">
          {flags.length} red flag{flags.length > 1 ? 's' : ''} detected
        </span>
      </div>

      <div className="text-sm sm:text-base leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap p-3 rounded-xl bg-slate-50 dark:bg-slate-950 font-mono text-xs sm:text-sm border border-slate-200 dark:border-slate-800">
        {renderHighlighted()}
      </div>

      {/* Selected Flag Details or Flag Legend List */}
      <div className="mt-4 space-y-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Red Flags Breakdown:
        </h4>
        <div className="grid grid-cols-1 gap-2">
          {flags.map((flag, idx) => (
            <div
              key={idx}
              onClick={() => setActiveFlag(flag)}
              className={`p-3 rounded-xl border text-xs sm:text-sm cursor-pointer transition-all ${
                activeFlag === flag
                  ? 'border-red-500 bg-red-50/80 dark:bg-red-950/40 ring-1 ring-red-500'
                  : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-mono font-bold text-red-600 dark:text-red-400">
                  "{flag.text_span}"
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                  {flag.category}
                </span>
              </div>
              <p className="text-slate-700 dark:text-slate-300 font-medium">
                {flag.reason}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

