let currentLang = localStorage.getItem('lang') || 'fr';

function t(key) {
  return (translations[currentLang] && translations[currentLang][key])
    || (translations['fr'] && translations['fr'][key])
    || key;
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  applyTranslations();
}

function applyTranslations() {
  // Texte des éléments avec data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = t(key);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
      el.placeholder = val;
    } else {
      el.textContent = val;
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  applyTranslations();
});