import React, { useState, useRef } from 'react';
import { Mic, Square, Trash2, Volume2, AlertCircle } from 'lucide-react';

export default function AudioRecorder({ onAudioReady, onClear }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];

      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        const file = new File([audioBlob], `voicenote_${Date.now()}.webm`, { type: 'audio/webm' });
        onAudioReady(file);

        // Stop all audio tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setRecordingSeconds(0);

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError('Microphone permission denied or not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const handleClear = () => {
    setAudioUrl(null);
    setRecordingSeconds(0);
    if (onClear) onClear();
  };

  return (
    <div className="p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {isRecording ? (
            <div className="flex items-center gap-2">
              <span className="w-3.5 h-3.5 rounded-full bg-red-600 animate-ping" />
              <span className="font-mono text-sm font-bold text-red-600 dark:text-red-400">
                Recording ({recordingSeconds}s)...
              </span>
            </div>
          ) : audioUrl ? (
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Voice note recorded ({recordingSeconds}s)
              </span>
            </div>
          ) : (
            <div className="text-xs text-slate-500 dark:text-slate-400">
              Record suspicious extortion call or audio threat
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isRecording ? (
            <button
              type="button"
              onClick={stopRecording}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-sm transition-all"
            >
              <Square className="w-3.5 h-3.5 fill-white" />
              Stop Recording
            </button>
          ) : (
            <button
              type="button"
              onClick={startRecording}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm transition-all"
            >
              <Mic className="w-3.5 h-3.5" />
              {audioUrl ? 'Record Again' : 'Record Audio'}
            </button>
          )}

          {audioUrl && !isRecording && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              title="Delete audio"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {audioUrl && !isRecording && (
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800">
          <audio src={audioUrl} controls className="w-full h-8" />
        </div>
      )}

      {error && (
        <div className="mt-2 text-xs text-red-600 dark:text-red-400 flex items-center gap-1 font-medium">
          <AlertCircle className="w-3.5 h-3.5" />
          {error}
        </div>
      )}
    </div>
  );
}

