import React, { useState } from 'react';
import { UploadCloud, Image as ImageIcon, Sliders, ShieldCheck, AlertCircle, Info, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';

export default function MediaCheckView() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mediaResult, setMediaResult] = useState(null);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('heatmap'); // 'heatmap' | 'original' | 'split'

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setMediaResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.checkMedia(selectedFile);
      setMediaResult(res);
    } catch (err) {
      setError(err.message || 'Media analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <ImageIcon className="w-5 h-5 text-blue-600 dark:text-sky-400" />
          <h2 className="text-xl font-black text-slate-900 dark:text-white">
            Forensic Media Authenticity & Tampering Check
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mb-4">
          Uses Error Level Analysis (ELA) to identify compression discrepancies caused by digital manipulation, forged police seals, or pasted signatures.
        </p>

        {/* Upload Box */}
        <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-500 rounded-2xl p-6 text-center cursor-pointer transition-colors bg-slate-50/50 dark:bg-slate-950/50">
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp,audio/*"
            onChange={handleFileChange}
            id="media-upload-input"
            className="hidden"
          />
          <label htmlFor="media-upload-input" className="cursor-pointer block">
            <UploadCloud className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <span className="text-sm font-bold text-slate-700 dark:text-slate-300 block">
              {selectedFile ? selectedFile.name : 'Choose notice screenshot, document, or audio clip'}
            </span>
            <span className="text-xs text-slate-500 block mt-1">
              Supports PNG, JPG, WEBP, MP3, WAV (Max 10 MB)
            </span>
          </label>
        </div>

        {selectedFile && (
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating ELA Forensic Heatmap...
                </>
              ) : (
                'Run Forensic Analysis'
              )}
            </button>
          </div>
        )}

        {error && (
          <p className="mt-3 text-xs text-red-600 dark:text-red-400 font-bold">
            {error}
          </p>
        )}
      </div>

      {/* Analysis Results View */}
      {mediaResult && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-md space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
            <div>
              <span className="text-xs uppercase font-extrabold tracking-widest text-slate-400">
                Forensic Finding
              </span>
              <div className="flex items-center gap-2 mt-0.5">
                <span
                  className={`text-lg font-black px-3 py-1 rounded-xl uppercase tracking-wider ${
                    mediaResult.has_manipulation_signs
                      ? 'bg-red-100 text-red-800 dark:bg-red-950/80 dark:text-red-300'
                      : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300'
                  }`}
                >
                  {mediaResult.has_manipulation_signs ? 'TAMPERING DETECTED' : 'NO SPLICING DETECTED'}
                </span>
                <span className="text-xs font-bold text-slate-500">
                  Confidence: {mediaResult.confidence}
                </span>
              </div>
            </div>

            {/* View Mode Switcher */}
            {mediaResult.ela_heatmap_base64 && (
              <div className="flex rounded-lg bg-slate-100 dark:bg-slate-800 p-1 text-xs font-bold">
                <button
                  onClick={() => setViewMode('original')}
                  className={`px-3 py-1 rounded-md transition-all ${
                    viewMode === 'original' ? 'bg-white dark:bg-slate-700 shadow-sm text-blue-600 dark:text-sky-400' : 'text-slate-600 dark:text-slate-300'
                  }`}
                >
                  Original
                </button>
                <button
                  onClick={() => setViewMode('heatmap')}
                  className={`px-3 py-1 rounded-md transition-all ${
                    viewMode === 'heatmap' ? 'bg-white dark:bg-slate-700 shadow-sm text-blue-600 dark:text-sky-400' : 'text-slate-600 dark:text-slate-300'
                  }`}
                >
                  ELA Heatmap
                </button>
                <button
                  onClick={() => setViewMode('split')}
                  className={`px-3 py-1 rounded-md transition-all ${
                    viewMode === 'split' ? 'bg-white dark:bg-slate-700 shadow-sm text-blue-600 dark:text-sky-400' : 'text-slate-600 dark:text-slate-300'
                  }`}
                >
                  Side-by-Side
                </button>
              </div>
            )}
          </div>

          {/* Visual Display */}
          {mediaResult.ela_heatmap_base64 && (
            <div>
              {viewMode === 'original' && (
                <div className="rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-950 max-h-96 flex items-center justify-center p-2">
                  <img src={previewUrl} alt="Original Notice" className="max-h-92 object-contain rounded-lg" />
                </div>
              )}

              {viewMode === 'heatmap' && (
                <div className="rounded-xl overflow-hidden bg-black max-h-96 flex items-center justify-center p-2">
                  <img
                    src={mediaResult.ela_heatmap_base64}
                    alt="Error Level Analysis Heatmap"
                    className="max-h-92 object-contain rounded-lg"
                  />
                </div>
              )}

              {viewMode === 'split' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-950 p-2 text-center">
                    <span className="text-xs font-bold text-slate-500 mb-1 block">Original</span>
                    <img src={previewUrl} alt="Original" className="max-h-64 mx-auto object-contain rounded-lg" />
                  </div>
                  <div className="rounded-xl overflow-hidden bg-black p-2 text-center">
                    <span className="text-xs font-bold text-slate-400 mb-1 block">ELA Compression Map</span>
                    <img src={mediaResult.ela_heatmap_base64} alt="Heatmap" className="max-h-64 mx-auto object-contain rounded-lg" />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Notes & Metadata */}
          <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-xs sm:text-sm">
            <h4 className="font-bold text-slate-700 dark:text-slate-300 mb-1">
              Forensic Summary:
            </h4>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {mediaResult.analysis_notes}
            </p>

            {mediaResult.metadata && (
              <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="font-semibold text-slate-500">Editing Tool:</span> {mediaResult.metadata.software || 'None in EXIF'}
                </div>
                <div>
                  <span className="font-semibold text-slate-500">Dimensions:</span> {mediaResult.metadata.image_width} x {mediaResult.metadata.image_height}
                </div>
              </div>
            )}
          </div>

          {/* Honest Disclaimer Banner */}
          <div className="p-3.5 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 flex items-start gap-2 text-xs text-blue-900 dark:text-blue-300">
            <Info className="w-4 h-4 flex-shrink-0 text-blue-600 mt-0.5" />
            <p className="leading-relaxed">
              <strong>Ethical Disclosure:</strong> {mediaResult.limitations_disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

