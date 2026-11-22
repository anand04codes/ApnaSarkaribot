import React, { useState } from 'react';
import { AlertOctagon, AlertTriangle, CheckCircle, Volume2, Loader2, FileText, Info } from 'lucide-react';
import { apiClient } from '../api/client';
import { TRANSLATIONS } from '../i18n/translations';

export default function VerdictCard({ analysis, language, onOpenComplaint }) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioError, setAudioError] = useState(null);
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  if (!analysis) return null;

  const {
    verdict,
    risk_score,
    confidence,
    confidence_score,
    scam_type,
    plain_explanation,
    what_it_really_means,
    disagreement_warning
  } = analysis;

  const isScam = verdict === 'LIKELY SCAM';
  const isSuspicious = verdict === 'SUSPICIOUS';
  const isGenuine = verdict === 'LOOKS GENUINE';

  const handlePlayVoice = async () => {
    try {
      setIsPlayingAudio(true);
      setAudioError(null);
      const textToSpeak = `${plain_explanation}. ${what_it_really_means || ''}`;
      const audioUrl = await apiClient.getTTS(textToSpeak, language);
      const audio = new Audio(audioUrl);
      audio.onended = () => setIsPlayingAudio(false);
      audio.onerror = () => {
        setIsPlayingAudio(false);
        setAudioError('Voice playback unavailable on this device.');
      };
      await audio.play();
    } catch (err) {
      setIsPlayingAudio(false);
      setAudioError('Could not stream audio.');
    }
  };

  const badgeConfig = isScam
    ? {
        bg: 'bg-red-50 dark:bg-red-950/40 border-red-500 text-red-900 dark:text-red-200',
        bar: 'bg-red-600',
        icon: <AlertOctagon className="w-8 h-8 text-red-600" />,
        label: t.verdict.likelyScam
      }
    : isSuspicious
    ? {
        bg: 'bg-amber-50 dark:bg-amber-950/40 border-amber-500 text-amber-900 dark:text-amber-200',
        bar: 'bg-amber-500',
        icon: <AlertTriangle className="w-8 h-8 text-amber-500" />,
        label: t.verdict.suspicious
      }
    : {
        bg: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-500 text-emerald-900 dark:text-emerald-200',
        bar: 'bg-emerald-600',
        icon: <CheckCircle className="w-8 h-8 text-emerald-600" />,
        label: t.verdict.looksGenuine
      };

  return (
    <div className={`rounded-2xl border-2 p-5 sm:p-6 shadow-md transition-all ${badgeConfig.bg}`}>
      {/* Header: Verdict Badge & Audio */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-black/10 dark:border-white/10 pb-4">
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 rounded-xl bg-white dark:bg-slate-900 shadow-sm">
            {badgeConfig.icon}
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-widest opacity-75">
              {t.verdict.confidence}: {confidence} ({Math.round((confidence_score || 0.8) * 100)}%)
            </span>
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
              {badgeConfig.label}
            </h2>
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              {scam_type}
            </div>
          </div>
        </div>

        {/* Listen Button */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePlayVoice}
            disabled={isPlayingAudio}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-bold text-sm shadow-sm hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-all active:scale-95 disabled:opacity-50"
            aria-label="Listen to explanation in voice"
          >
            {isPlayingAudio ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span>{t.verdict.playingVoice}</span>
              </>
            ) : (
              <>
                <Volume2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span>{t.verdict.listenBtn}</span>
              </>
            )}
          </button>

          {isScam && onOpenComplaint && (
            <button
              onClick={onOpenComplaint}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs sm:text-sm shadow-sm transition-all active:scale-95"
            >
              <FileText className="w-4 h-4" />
              <span className="hidden sm:inline">Report 1930</span>
            </button>
          )}
        </div>
      </div>

      {audioError && (
        <p className="text-xs text-red-600 dark:text-red-400 mt-2 font-medium">
          {audioError}
        </p>
      )}

      {/* Risk Meter Gauge */}
      <div className="mt-4">
        <div className="flex justify-between items-center text-xs sm:text-sm font-bold mb-1.5">
          <span>{t.verdict.riskScore}:</span>
          <span className="text-base font-extrabold">{risk_score} / 100</span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-800 h-3.5 rounded-full overflow-hidden p-0.5">
          <div
            className={`h-full rounded-full transition-all duration-700 ${badgeConfig.bar}`}
            style={{ width: `${Math.max(5, risk_score)}%` }}
          />
        </div>
      </div>

      {/* Disagreement Warning if rules and LLM diverged */}
      {disagreement_warning && (
        <div className="mt-4 p-3 rounded-xl bg-amber-100 dark:bg-amber-900/30 border border-amber-300 dark:border-amber-700 text-xs sm:text-sm text-amber-900 dark:text-amber-200 flex items-start gap-2">
          <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-amber-700 dark:text-amber-400" />
          <p>{disagreement_warning}</p>
        </div>
      )}

      {/* Plain Language Explanation */}
      <div className="mt-5 bg-white/80 dark:bg-slate-900/80 rounded-xl p-4 border border-black/5 dark:border-white/5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5">
          {t.verdict.plainExplanation}
        </h3>
        <p className="text-sm sm:text-base leading-relaxed text-slate-800 dark:text-slate-200 font-medium">
          {plain_explanation}
        </p>

        {what_it_really_means && (
          <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 mb-1">
              {t.verdict.whatItReallyMeans}
            </h4>
            <p className="text-sm text-slate-700 dark:text-slate-300">
              {what_it_really_means}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

