import React from 'react';
import { ShieldCheck, Lock, EyeOff, Database, Server, Check } from 'lucide-react';

export default function PrivacyPolicy() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 sm:p-8 border border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 rounded-xl">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-900 dark:text-white">
              Privacy, Anonymity & Data Protection
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
              Zero PII Architecture: Designed for citizen trust and alignment with Indian DPDP Act principles.
            </p>
          </div>
        </div>

        <div className="space-y-6 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
          {/* Key Pillars */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-6">
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <EyeOff className="w-5 h-5 text-blue-600 mb-2" />
              <h3 className="font-bold text-slate-900 dark:text-white mb-1">No Raw Text Stored</h3>
              <p className="text-xs text-slate-500">
                Messages, chats, and notice texts you paste are analyzed in ephemeral RAM and never written to disk.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <Lock className="w-5 h-5 text-emerald-600 mb-2" />
              <h3 className="font-bold text-slate-900 dark:text-white mb-1">No File Retention</h3>
              <p className="text-xs text-slate-500">
                Uploaded photos, PDFs, and audio recordings are discarded immediately after analysis is complete.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800">
              <Database className="w-5 h-5 text-amber-500 mb-2" />
              <h3 className="font-bold text-slate-900 dark:text-white mb-1">Anonymized Trends Only</h3>
              <p className="text-xs text-slate-500">
                Our public dashboard aggregates only anonymous category counters (e.g. "Digital Arrest", "Hindi").
              </p>
            </div>
          </div>

          <h3 className="text-base font-extrabold text-slate-900 dark:text-white mt-6">
            1. What Data We Process During Verification
          </h3>
          <p>
            When you submit text, an image, or a voice recording to SarkariSach, our hybrid detection engine
            inspects the content strictly to identify extortion patterns, impersonation of official Indian
            authorities (CBI, ED, Police, Courts, TRAI), phishing URLs, and credential theft attempts.
          </p>

          <h3 className="text-base font-extrabold text-slate-900 dark:text-white mt-4">
            2. What We Store in Our Database
          </h3>
          <p>
            To power the public threat intelligence dashboard and alert citizens to emerging fraud waves,
            we record <strong>only the following aggregated non-PII fields:</strong>
          </p>
          <ul className="list-disc pl-5 space-y-1 text-xs sm:text-sm text-slate-600 dark:text-slate-300">
            <li>Timestamp (date and hour of check)</li>
            <li>Classified Scam Category (e.g., "Digital Arrest", "Electricity Bill Scam")</li>
            <li>Risk Bucket ("LIKELY SCAM", "SUSPICIOUS", "LOOKS GENUINE")</li>
            <li>Selected query language code (e.g., "hi", "mr", "en")</li>
            <li>Input type ("text", "image", "audio", "url")</li>
            <li>Complainant State (optional, if selected by user)</li>
          </ul>

          <h3 className="text-base font-extrabold text-slate-900 dark:text-white mt-4">
            3. What We NEVER Store
          </h3>
          <div className="space-y-1.5 text-xs sm:text-sm font-medium text-red-700 dark:text-red-300">
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>We NEVER store your personal name, Aadhaar, PAN, phone number, or IP address.</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>We NEVER store the raw text of your message or WhatsApp chat history.</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>We NEVER store uploaded images, PDFs, or audio voice clips.</span>
            </div>
          </div>

          <h3 className="text-base font-extrabold text-slate-900 dark:text-white mt-4">
            4. Legal Guidance Disclaimer
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
            SarkariSach is an automated public-service verification aid powered by heuristic rules and artificial
            intelligence. While built upon official advisories issued by the Ministry of Home Affairs, Indian Cyber
            Crime Coordination Centre (I4C), Reserve Bank of India, and TRAI, its outputs are for educational
            awareness and do not constitute formal legal counsel. If financial fraud has occurred, contact
            helpline <strong>1930</strong> or register a grievance at <strong>cybercrime.gov.in</strong> immediately.
          </p>
        </div>
      </div>
    </div>
  );
}

