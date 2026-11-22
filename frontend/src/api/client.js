/**
 * API client for SarkariSach backend services.
 */
const BASE_URL = '/api';

export const apiClient = {
  async healthCheck() {
    const res = await fetch(`${BASE_URL}/health`);
    return res.json();
  },

  async analyze({ text, url, file, language = 'en', user_state = '' }) {
    const formData = new FormData();
    if (text) formData.append('text', text);
    if (url) formData.append('url', url);
    if (language) formData.append('language', language);
    if (user_state) formData.append('user_state', user_state);
    if (file) formData.append('file', file);

    const res = await fetch(`${BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(err.detail || 'Analysis request failed');
    }
    return res.json();
  },

  async checkUrl(url) {
    const res = await fetch(`${BASE_URL}/check-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'URL check failed' }));
      throw new Error(err.detail || 'URL check failed');
    }
    return res.json();
  },

  async checkMedia(file) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${BASE_URL}/check-media`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Media check failed' }));
      throw new Error(err.detail || 'Media check failed');
    }
    return res.json();
  },

  async getTTS(text, language = 'en') {
    const res = await fetch(`${BASE_URL}/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    });

    if (!res.ok) {
      throw new Error('TTS generation failed');
    }
    const blob = await res.blob();
    return URL.createObjectURL(blob);
  },

  async generateComplaint(text, claimed_agency = '', user_state = '') {
    const res = await fetch(`${BASE_URL}/generate-complaint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, claimed_agency, user_state }),
    });

    if (!res.ok) {
      throw new Error('Complaint generation failed');
    }
    return res.json();
  },

  async getDashboardStats() {
    const res = await fetch(`${BASE_URL}/dashboard/stats`);
    if (!res.ok) {
      throw new Error('Failed to fetch dashboard stats');
    }
    return res.json();
  }
};

