// author: Wassim Alkhalil

// Simple client-side i18n with safe whitelisting
// Only load whitelisted locales to avoid path traversal or unwanted resource loads.

import en from '../locales/en.json';
import bg from '../locales/bg.json';

const ALLOWED = {
  en,
  bg,
};

function safeLangFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const raw = (params.get('lang') || '').trim().toLowerCase();
  if (raw && Object.prototype.hasOwnProperty.call(ALLOWED, raw)) {
    return raw;
  }
  return null;
}

export function getCurrentLang() {
  const fromUrl = safeLangFromUrl();
  if (fromUrl) return fromUrl;
  try {
    const saved = (localStorage.getItem('lang') || '').trim().toLowerCase();
    if (saved && Object.prototype.hasOwnProperty.call(ALLOWED, saved)) {
      return saved;
    }
  } catch (_) {
    // localStorage disabled
  }
  return 'en';
}

export function setLang(lang) {
  const code = (lang || '').trim().toLowerCase();
  if (!Object.prototype.hasOwnProperty.call(ALLOWED, code)) return;
  try {
    localStorage.setItem('lang', code);
  } catch (_) {}
  const url = new URL(window.location.href);
  url.searchParams.set('lang', code);
  // Navigate to persist query param (backend also reads this).
  window.location.assign(url.toString());
}

export function t(key, params) {
  const dict = ALLOWED[getCurrentLang()] || ALLOWED.en;
  let str = dict[key] || key;
  if (params && typeof params === 'object') {
    for (const [k, v] of Object.entries(params)) {
      // Basic placeholder replacement: {{key}}
      str = str.replace(new RegExp(`\\{\\{${k}\\}\\}`, 'g'), String(v));
    }
  }
  return str;
}

export function ensureQueryLang() {
  // If no lang in query but we have a saved lang, add it.
  const params = new URLSearchParams(window.location.search);
  if (!params.has('lang')) {
    const saved = getCurrentLang();
    const url = new URL(window.location.href);
    url.searchParams.set('lang', saved);
    // Replace to avoid extra history entries
    window.history.replaceState(null, '', url.toString());
  }
}
