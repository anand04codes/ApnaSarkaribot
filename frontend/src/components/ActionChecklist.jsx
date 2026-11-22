import React, { useState } from 'react';
import { ShieldAlert, ExternalLink, CheckSquare, Square, PhoneCall } from 'lucide-react';

export default function ActionChecklist({ actions, onGenerateComplaint }) {
  const [completedSteps, setCompletedSteps] = useState({});

  if (!actions || actions.length === 0) return null;

  const toggleStep = (step) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [step]: !prev[step],
    }));
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 className="font-extrabold text-base sm:text-lg text-slate-900 dark:text-white">
            Action Checklist: What You Must Do Now
          </h3>
        </div>
        {onGenerateComplaint && (
          <button
            onClick={onGenerateComplaint}
            className="text-xs sm:text-sm font-bold text-red-600 hover:text-red-700 dark:text-red-400 underline"
          >
            Draft Cyber Complaint &rarr;
          </button>
        )}
      </div>

      <div className="space-y-3">
        {actions.map((act) => {
          const isDone = !!completedSteps[act.step];
          return (
            <div
              key={act.step}
              onClick={() => toggleStep(act.step)}
              className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition-all ${
                isDone
                  ? 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 opacity-60'
                  : 'bg-white dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 hover:border-blue-400 shadow-sm'
              }`}
            >
              <button
                type="button"
                className="mt-0.5 text-blue-600 dark:text-blue-400 flex-shrink-0"
                aria-label={`Mark step ${act.step} as ${isDone ? 'incomplete' : 'complete'}`}
              >
                {isDone ? <CheckSquare className="w-5 h-5 text-emerald-600" /> : <Square className="w-5 h-5" />}
              </button>

              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300">
                    Step {act.step}
                  </span>
                  <span className={`text-sm sm:text-base font-bold ${isDone ? 'line-through text-slate-500' : 'text-slate-900 dark:text-white'}`}>
                    {act.title}
                  </span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 ml-auto">
                    {act.action_type}
                  </span>
                </div>

                <p className={`text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed ${isDone ? 'line-through' : ''}`}>
                  {act.description}
                </p>

                {act.link && (
                  <div className="mt-2" onClick={(e) => e.stopPropagation()}>
                    <a
                      href={act.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-bold text-blue-600 hover:text-blue-700 dark:text-sky-400 hover:underline"
                    >
                      Visit Official Portal ({act.link.replace('https://', '')})
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

