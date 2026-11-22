import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import VerdictCard from './components/VerdictCard';
import HighlightedText from './components/HighlightedText';
import ActionChecklist from './components/ActionChecklist';
import ComplaintModal from './components/ComplaintModal';
import AudioRecorder from './components/AudioRecorder';
import UrlChecker from './components/UrlChecker';
import MediaCheckView from './components/MediaCheckView';
import TrendingDashboard from './components/TrendingDashboard';
import PrivacyPolicy from './components/PrivacyPolicy';
import { apiClient } from './api/client';
import { TRANSLATIONS } from './i18n/translations';
import {
  UploadCloud, FileText, Image as ImageIcon, Sparkles, AlertCircle,
  Loader2, Trash2, ShieldCheck, MapPin
} from 'lucide-react';

const INDIAN_STATES = [
  'All India', 'Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu',
  'Uttar Pradesh', 'Gujarat', 'West Bengal', 'Telangana', 'Rajasthan',
  'Kerala', 'Madhya Pradesh', 'Punjab', 'Haryana', 'Bihar'
];

export default function App() {
  const [activeTab, setActiveTab] = useState('verify');
  const [language, setLanguage] = useState('hi');
  const [darkMode, setDarkMode] = useState(false);

  // Form State
  const [inputText, setInputText] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [userState, setUserState] = useState('Maharashtra');

  // Analysis State
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [showComplaintModal, setShowComplaintModal] = useState(false);

  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // Dark Mode Sync
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      if (file.type.startsWith('image/')) {
        setFilePreview(URL.createObjectURL(file));
      } else {
        setFilePreview(null);
      }
    }
  };

  const handleAudioReady = (audioFile) => {
    setUploadedFile(audioFile);
    setFilePreview(null);
  };

  const handleClearFile = () => {
    setUploadedFile(null);
    setFilePreview(null);
  };

  const handleRunAnalysis = async (customText = null, customFile = null) => {
    const textToAnalyze = customText !== null ? customText : inputText;
    const fileToAnalyze = customFile !== null ? customFile : uploadedFile;

    if (!textToAnalyze.trim() && !fileToAnalyze) {
      setError('Please enter text or upload a document/screenshot/audio file.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setAnalysisResult(null);

      const result = await apiClient.analyze({
        text: textToAnalyze,
        file: fileToAnalyze,
        language: language,
        user_state: userState === 'All India' ? '' : userState
      });

      setAnalysisResult(result);
    } catch (err) {
      setError(err.message || 'Verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Sample Cases
  const sampleScenarios = [
    {
      label: t.input.sampleDigitalArrest,
      text: 'सीबीआई और मुंबई पुलिस नोटिस: आपके आधार कार्ड से 16 गैरकानूनी सिम कार्ड खरीदे गए हैं और नशीली दवाओं का अवैध पार्सल भेजा गया है। आपको डिजिटल अरेस्ट में रखा जाता है। स्काइप वीडियो कॉल पर 2 घंटे के भीतर पेश हों, वरना गैर-जमानती गिरफ्तारी वारंट जारी होगा। मामला रफा-दफा करने के लिए सुरक्षा राशि 2,50,000 रुपये आरबीआई सत्यापन खाते में तुरंत ट्रांसफर करें।'
    },
    {
      label: t.input.sampleFedEx,
      text: 'FedEx Alert: Your shipment tracking #FDX984210 bound for Cambodia has been seized by Narcotics Control Bureau (NCB). 140g MDMA contraband detected. Connect on WhatsApp video call +91-9871234567 immediately to record statement before police custody and asset freeze.'
    },
    {
      label: t.input.sampleElectricity,
      text: 'Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the power grid because your previous month bill was not updated. Please immediately contact our Electricity Officer Mr. Verma at mobile 9834567890. Disconnection order #EB-9821.'
    },
    {
      label: t.input.sampleGenuineIT,
      text: 'Your refund of Rs. 14,280 for AY 2024-25 has been credited to your bank account ending in 4108 on 12-OCT-2024 vide CMP. Income Tax Department, Government of India. Track status at https://incometax.gov.in. ITD never asks for PIN or OTP.'
    }
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors">
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'url' && <UrlChecker />}
        {activeTab === 'media' && <MediaCheckView />}
        {activeTab === 'dashboard' && <TrendingDashboard />}
        {activeTab === 'privacy' && <PrivacyPolicy />}

        {activeTab === 'verify' && (
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Input Card */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 sm:p-7 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="mb-4">
                <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <Sparkles className="w-6 h-6 text-amber-500" />
                  {t.input.title}
                </h1>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
                  {t.input.subtitle}
                </p>
              </div>

              {/* Text Area */}
              <div className="relative mb-4">
                <textarea
                  rows={5}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={t.input.placeholder}
                  className="w-full p-4 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white text-sm sm:text-base focus:ring-2 focus:ring-blue-500 focus:outline-none resize-y leading-relaxed"
                />
                {inputText && (
                  <button
                    onClick={() => setInputText('')}
                    className="absolute right-3 top-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs font-bold px-2 py-1 rounded bg-slate-200 dark:bg-slate-800"
                  >
                    Clear
                  </button>
                )}
              </div>

              {/* Voice Recorder & File Upload Controls */}
              <div className="space-y-3 mb-4">
                <AudioRecorder onAudioReady={handleAudioReady} onClear={handleClearFile} />

                {/* File Attachment Bar */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50">
                  <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 truncate max-w-sm">
                    <ImageIcon className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    {uploadedFile ? (
                      <span className="font-semibold text-slate-900 dark:text-white truncate">
                        Attached: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(0)} KB)
                      </span>
                    ) : (
                      <span>Upload document screenshot or PDF notice (Max 10MB)</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="file"
                      id="doc-upload"
                      accept="image/png,image/jpeg,image/webp,application/pdf,audio/*"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <label
                      htmlFor="doc-upload"
                      className="px-3 py-1.5 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 text-xs font-bold cursor-pointer transition-colors"
                    >
                      Browse File
                    </label>

                    {uploadedFile && (
                      <button
                        onClick={handleClearFile}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 transition-colors"
                        title="Remove file"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {filePreview && (
                  <div className="relative inline-block mt-2">
                    <img
                      src={filePreview}
                      alt="Uploaded preview"
                      className="h-24 w-auto rounded-lg object-contain border border-slate-300 dark:border-slate-700"
                    />
                  </div>
                )}
              </div>

              {/* State Context & Verify Button */}
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 w-full sm:w-auto">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>State (for complaint jurisdiction):</span>
                  <select
                    value={userState}
                    onChange={(e) => setUserState(e.target.value)}
                    className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs font-semibold text-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700"
                  >
                    {INDIAN_STATES.map((st) => (
                      <option key={st} value={st}>{st}</option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={() => handleRunAnalysis()}
                  disabled={loading || (!inputText.trim() && !uploadedFile)}
                  className="w-full sm:w-auto px-8 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white font-extrabold text-sm sm:text-base shadow-lg hover:shadow-xl transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      {t.input.checkingBtn}
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-5 h-5" />
                      {t.input.checkBtn}
                    </>
                  )}
                </button>
              </div>

              {/* Quick Sample Test Buttons */}
              <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800">
                <span className="text-xs font-bold text-slate-500 dark:text-slate-400 block mb-2">
                  {t.input.sampleButtonsTitle}
                </span>
                <div className="flex flex-wrap gap-2">
                  {sampleScenarios.map((s, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setInputText(s.text);
                        handleRunAnalysis(s.text, null);
                      }}
                      className="text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-blue-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 transition-colors"
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {error && (
                <div className="mt-4 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-300 dark:border-red-800 text-xs sm:text-sm text-red-800 dark:text-red-300 flex items-center gap-2 font-medium">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Analysis Results View */}
            {analysisResult && (
              <div className="space-y-6 animate-in fade-in duration-300">
                {/* 1. Verdict Card */}
                <VerdictCard
                  analysis={analysisResult}
                  language={language}
                  onOpenComplaint={() => setShowComplaintModal(true)}
                />

                {/* 2. Highlighted Evidence Card */}
                <HighlightedText
                  text={analysisResult.extracted_text || inputText}
                  redFlags={analysisResult.red_flags}
                />

                {/* 3. Action Checklist */}
                <ActionChecklist
                  actions={analysisResult.recommended_actions}
                  onGenerateComplaint={() => setShowComplaintModal(true)}
                />
              </div>
            )}
          </div>
        )}
      </main>

      {/* Cyber Complaint Modal */}
      {analysisResult?.complaint_summary && (
        <ComplaintModal
          complaint={analysisResult.complaint_summary}
          isOpen={showComplaintModal}
          onClose={() => setShowComplaintModal(false)}
        />
      )}

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 text-center text-xs text-slate-500 dark:text-slate-400 transition-colors">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p>{t.footer.disclaimer}</p>
          <div className="flex items-center justify-center gap-2 font-semibold text-slate-700 dark:text-slate-300">
            <span>🛡️ SarkariSach Open-Source</span>
            <span>•</span>
            <span>Helpline: 1930</span>
            <span>•</span>
            <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 text-[10px] uppercase font-bold">
              IDEA//FORGE Hackathon Track 1
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}

