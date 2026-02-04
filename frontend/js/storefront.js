import 'bootstrap';
import 'lazysizes';
import SVGInjector from 'svg-injector-2';

import './components/address-form';
import './components/cart';
import './components/mycart';
import './components/navbar';
import './components/product-filters';
import './components/sorter';
import './components/styleguide';
import './components/variant-choose';

import '../scss/storefront.scss';
import { t } from './i18n';
import { initLangSelector } from './components/lang-selector';

new SVGInjector().inject(document.querySelectorAll('svg[data-src]'));

document.addEventListener('DOMContentLoaded', () => {
  initLangSelector();
  const editForm = document.getElementById('addressForm')
    || document.querySelector('.address-form');
  if (!editForm) return;

  const submitButtons = Array.from(
    editForm.querySelectorAll('[type="submit"]'),
  );

  editForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    submitButtons.forEach((b) => b.setAttribute('disabled', 'disabled'));

    const hidden = editForm.querySelector('input[name="csrf_token"]');
    const meta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = (hidden && hidden.value) || (meta && meta.getAttribute('content')) || '';

    const formData = new FormData(editForm);
    const url = editForm.getAttribute('action')
      || window.location.pathname + window.location.search;

    try {
      const resp = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-CSRFToken': csrfToken,
        },
        body: formData,
      });

      if (!resp.ok) {
        const ct = resp.headers.get('Content-Type') || '';
        if (ct.includes('application/json')) {
          const err = await resp.json().catch(() => null);
          const msg = err && (err.message || err.error)
            ? err.message || err.error
            : t('server_responded', { status: resp.status });
          alert(`${t('save_failed')}: ${msg}`);
        } else {
          const txt = await resp.text().catch(() => '');
          console.error('Save failed:', resp.status, txt);
          alert(t('save_failed_console'));
        }
        submitButtons.forEach((b) => b.removeAttribute('disabled'));
        return;
      }
      // success
      window.location.reload();
    } catch (err) {
      console.error('Address save error', err);
      alert(t('network_error_saving_address'));
    } finally {
      submitButtons.forEach((b) => b.removeAttribute('disabled'));
    }
  });
});
