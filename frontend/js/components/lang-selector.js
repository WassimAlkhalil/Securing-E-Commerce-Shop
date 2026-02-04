import { getCurrentLang, setLang, ensureQueryLang } from '../i18n';
/* author: Wassim Alkhalil */
/* Initialize language selector with safe whitelisting. */
export function initLangSelector() {
  ensureQueryLang();
  const sel = document.getElementById('langSelector');
  if (!sel) return;

  // Set current selection
  const current = getCurrentLang();
  for (const opt of Array.from(sel.options)) {
    opt.selected = (opt.value.toLowerCase() === current);
  }

  sel.addEventListener('change', (e) => {
    const value = (e.target && e.target.value) || 'en';
    // setLang() validates value against ALLOWED whitelist before persisting
    setLang(value);
  });
}
