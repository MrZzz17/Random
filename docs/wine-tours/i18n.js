(function () {
  'use strict';

  var STORAGE_KEY = 'language';
  var DEFAULT_LANG = 'ru';
  var SUPPORTED = ['ru', 'en'];
  var WHATSAPP_PHONE = '61421047915';

  var REGION_IDS = ['yarra', 'mornington', 'macedon', 'geelong'];

  var REGION_TITLES = {
    yarra: 'Yarra Valley',
    mornington: 'Mornington Peninsula',
    macedon: 'Macedon Ranges',
    geelong: 'Geelong / Bellarine'
  };

  var REGION_IMAGE_BY_ID = {
    yarra: 'img/region-yarra.jpg',
    mornington: 'img/region-mornington.jpg',
    macedon: 'img/region-macedon.jpg',
    geelong: 'img/region-geelong.jpg'
  };

  var currentLang = DEFAULT_LANG;

  function normalizeLang(lang) {
    if (!lang) return DEFAULT_LANG;
    lang = String(lang).toLowerCase().split('-')[0];
    return SUPPORTED.indexOf(lang) !== -1 ? lang : DEFAULT_LANG;
  }

  function getByPath(obj, path) {
    if (!obj || !path) return undefined;
    var parts = String(path).split('.');
    var cur = obj;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function getTranslations(lang) {
    var tr = window.TRANSLATIONS;
    if (!tr) return {};
    return tr[lang] || tr[DEFAULT_LANG] || {};
  }

  function getLang() {
    return currentLang;
  }

  function t(key) {
    var lang = getLang();
    var val = getByPath(getTranslations(lang), key);
    if (val != null && val !== '') return val;
    if (lang !== DEFAULT_LANG) {
      val = getByPath(getTranslations(DEFAULT_LANG), key);
      if (val != null && val !== '') return val;
    }
    return key;
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function getMainEl() {
    return document.querySelector('main');
  }

  function applyFade() {
    var main = getMainEl();
    if (!main) return;
    main.classList.add('lang-fade');
    setTimeout(function () {
      main.classList.remove('lang-fade');
    }, 200);
  }

  function buildWhatsAppHref() {
    var text = t('contact.contactWaText');
    var phone = t('contact.contactWaPhone');
    if (!phone || phone === 'contact.contactWaPhone') phone = WHATSAPP_PHONE;
    return 'https://wa.me/' + String(phone).replace(/\D/g, '') + '?text=' + encodeURIComponent(text);
  }

  function updateWhatsAppLinks() {
    var href = buildWhatsAppHref();

    document.querySelectorAll('[data-i18n-wa-href]').forEach(function (el) {
      el.setAttribute('href', href);
      if (el.tagName === 'A') el.href = href;
    });

    document.querySelectorAll('.btn-chat').forEach(function (el) {
      el.href = href;
    });
  }

  function applyI18n() {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      el.textContent = t(el.getAttribute('data-i18n'));
    });

    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      el.innerHTML = t(el.getAttribute('data-i18n-html'));
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
      el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
    });

    document.querySelectorAll('[data-i18n-alt]').forEach(function (el) {
      el.alt = t(el.getAttribute('data-i18n-alt'));
    });

    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      var spec = el.getAttribute('data-i18n-attr');
      if (!spec) return;
      var pipe = spec.indexOf('|');
      if (pipe === -1) return;
      var key = spec.slice(0, pipe).trim();
      var attr = spec.slice(pipe + 1).trim();
      if (!key || !attr) return;
      el.setAttribute(attr, t(key));
    });

    document.querySelectorAll('.card-toggle').forEach(function (btn) {
      var card = btn.closest('.card');
      if (!card) return;
      btn.textContent = card.classList.contains('is-open')
        ? t('regions.collapse')
        : t('regions.more');
    });

    updateWhatsAppLinks();
  }

  function updateMeta() {
    var lang = getLang();
    var meta = getByPath(window.TRANSLATIONS && window.TRANSLATIONS[lang], 'meta');
    if (!meta) return;

    if (meta.title) document.title = meta.title;

    var descEl = document.querySelector('meta[name="description"]');
    if (descEl && meta.description) descEl.setAttribute('content', meta.description);

    var ogTitle = meta.ogTitle != null ? meta.ogTitle : meta['og:title'];
    var ogEl = document.querySelector('meta[property="og:title"]');
    if (ogEl && ogTitle) ogEl.setAttribute('content', ogTitle);
  }

  function regionMoreHtml(region) {
    if (region.moreHtml) return region.moreHtml;
    if (Array.isArray(region.more)) return region.more.join('');
    if (Array.isArray(region.paragraphs)) {
      return region.paragraphs
        .map(function (p) {
          return '<p>' + p + '</p>';
        })
        .join('');
    }
    return '';
  }

  function renderRegionCard(region) {
    var id = region.id;
    var imgSrc = REGION_IMAGE_BY_ID[id] || 'img/region-' + id + '.jpg';
    var alt = region.alt != null ? region.alt : region.title || '';
    var moreHtml = regionMoreHtml(region);

    return (
      '<article class="region-card region-card--' +
        escapeHtml(id) +
        ' card" data-region="' +
        escapeHtml(id) +
        '">' +
        '<div class="region-card__media">' +
        '<img src="' +
        escapeHtml(imgSrc) +
        '" alt="' +
        escapeHtml(alt) +
        '" loading="lazy">' +
        '<div class="region-card__shade" aria-hidden="true"></div>' +
        '</div>' +
        '<div class="region-card__body">' +
        '<h3 class="region-card__title">' +
        (region.title || '') +
        '</h3>' +
        '<p class="region-card__teaser">' +
        (region.teaser || '') +
        '</p>' +
        '<div class="card__more region-card__more">' +
        moreHtml +
        '</div>' +
        '<button type="button" class="region-card__link card-toggle">' +
        t('regions.more') +
        '</button>' +
        '</div>' +
      '</article>'
    )
  }

  function bindRegionCardToggles(grid) {
    if (!grid || grid._i18nToggleBound) return;
    grid._i18nToggleBound = true;
    grid.addEventListener('click', function (e) {
      var btn = e.target.closest('.card-toggle');
      if (!btn || !grid.contains(btn)) return;
      var card = btn.closest('.card');
      if (!card) return;
      var open = card.classList.toggle('is-open');
      btn.textContent = open ? t('regions.collapse') : t('regions.more');
    });
  }

  function renderRegions() {
    var grid = document.getElementById('regionsGrid');
    if (!grid) return;

    var lang = getLang();
    var content = window.REGION_CONTENT;
    if (!content) return;

    var regions = REGION_IDS.map(function (id) {
      var block = (content[id] && content[id][lang]) || content[id][DEFAULT_LANG];
      return {
        id: id,
        title: REGION_TITLES[id] || id,
        teaser: block.teaser,
        more: block.more
      };
    });

    grid.innerHTML = regions.map(renderRegionCard).join('');
    bindRegionCardToggles(grid);
  }

  function syncLanguageButtons() {
    document.querySelectorAll('.lang-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === getLang());
    });
  }

  function bindLanguageSwitcher() {
    document.querySelectorAll('.lang-btn').forEach(function (btn) {
      if (btn._i18nBound) return;
      btn._i18nBound = true;
      btn.addEventListener('click', function () {
        var lang = btn.getAttribute('data-lang');
        if (lang) setLang(lang);
      });
    });
    syncLanguageButtons();
  }

  function setLang(lang, opts) {
    opts = opts || {};
    var next = normalizeLang(lang);
    currentLang = next;

    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (e) {}

    document.documentElement.lang = next;

    if (!opts.skipFade) applyFade();

    applyI18n();
    updateMeta();
    renderRegions();
    syncLanguageButtons();

    document.dispatchEvent(
      new CustomEvent('languagechange', { detail: { lang: next } })
    );
  }

  function init() {
    var params = new URLSearchParams(window.location.search);
    var urlLang = params.get('lang');
    var stored = null;

    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch (e) {}

    currentLang = normalizeLang(urlLang || stored || DEFAULT_LANG);

    try {
      localStorage.setItem(STORAGE_KEY, currentLang);
    } catch (e) {}

    document.documentElement.lang = currentLang;
    applyI18n();
    updateMeta();
    renderRegions();
    bindLanguageSwitcher();
  }

  window.I18n = {
    init: init,
    getLang: getLang,
    setLang: setLang,
    t: t,
    applyI18n: applyI18n,
    renderRegions: renderRegions,
    updateMeta: updateMeta
  };
})();
