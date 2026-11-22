import React from 'react';
import { Shield, Moon, Sun, PhoneCall, Globe, AlertTriangle } from 'lucide-react';
import { TRANSLATIONS } from '../i18n/translations';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'mr', label: 'मराठी' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'gu', label: 'ગુજરાતી' },
  { code: 'kn', label: 'ಕನ್ನಡ' }
];

export default function Navbar({ activeTab, setActiveTab, language, setLanguage, darkMode, setDarkMode }) {
  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('verify')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-blue-700 to-emerald-600 flex items-center justify-center text-white shadow-md">
              <Shield className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">
                  {t.appTitle}
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300">
                  CIVIC PULSE
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
                {t.tagline}
              </p>
            </div>
          </div>

          {/* Right Tools: Helpline, Language, Theme */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* National 1930 Helpline Button */}
            <a
              href="tel:1930"
              className="flex items-center gap-1.5 bg-red-600 hover:bg-red-700 text-white font-semibold text-xs sm:text-sm px-2.5 py-1.5 rounded-lg shadow-sm transition-transform active:scale-95"
              title="Call National Cyber Crime Helpline 1930"
            >
              <PhoneCall className="w-4 h-4 animate-bounce" />
              <span className="hidden md:inline">Helpline:</span>
              <span className="font-black">1930</span>
            </a>

            {/* Language Selector */}
            <div className="relative flex items-center">
              <Globe className="w-4 h-4 text-slate-500 absolute left-2.5 pointer-events-none" />
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                aria-label="Select Language"
                className="pl-8 pr-3 py-1.5 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 text-xs sm:text-sm rounded-lg border border-slate-300 dark:border-slate-700 font-medium cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700 focus:outline-none"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              aria-label="Toggle Dark/Light Mode"
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
            </button>
          </div>
        </div>

        {/* Tab Navigation Navigation */}
        <nav className="flex space-x-1 sm:space-x-4 border-t border-slate-200 dark:border-slate-800 py-2 overflow-x-auto">
          {[
            { id: 'verify', label: t.tabs.verify },
            { id: 'url', label: t.tabs.linkChecker },
            { id: 'media', label: t.tabs.mediaForensics },
            { id: 'dashboard', label: t.tabs.dashboard },
            { id: 'privacy', label: t.tabs.privacy },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-sm dark:bg-blue-600'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}

