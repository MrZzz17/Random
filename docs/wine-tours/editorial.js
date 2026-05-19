(function () {
  'use strict';

  var PROTECTED_SELECTOR =
    '.hero__media, .about__media, .region-card__media, .tour-card__visual, ' +
    '.editorial-features__media, .editorial-features__photo, .cinematic-divider, .contact__stage';

  function isProtectedTarget(target) {
    if (!target || !target.closest) return false;
    if (target.tagName === 'IMG') return true;
    return !!(target.matches && target.matches(PROTECTED_SELECTOR)) || !!target.closest(PROTECTED_SELECTOR);
  }

  function initReveal() {
    var els = document.querySelectorAll('.reveal-on-scroll');
    if (!els.length) return;

    if (!('IntersectionObserver' in window)) {
      els.forEach(function (el) {
        el.classList.add('is-visible');
      });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }
    );

    els.forEach(function (el) {
      observer.observe(el);
    });
  }

  function initImageProtection() {
    var root = document.querySelector('main') || document.body;

    root.addEventListener(
      'contextmenu',
      function (e) {
        if (isProtectedTarget(e.target)) e.preventDefault();
      },
      true
    );

    root.addEventListener(
      'dragstart',
      function (e) {
        if (isProtectedTarget(e.target)) e.preventDefault();
      },
      true
    );
  }

  function init() {
    initReveal();
    initImageProtection();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
