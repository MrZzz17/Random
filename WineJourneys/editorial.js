(function () {
  'use strict';

  var PROTECTED_SELECTOR =
    '.hero__media, .about__media, .region-card__media, .tour-card__visual, ' +
    '.editorial-features__media, .editorial-features__photo, .editorial-features__media--transfer, ' +
    '.cinematic-end__bg';

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

  function initCinematicParallax() {
    var section = document.querySelector('.cinematic-end');
    var bg = document.querySelector('.cinematic-end__bg');
    if (!section || !bg) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var ticking = false;

    function update() {
      ticking = false;
      var rect = section.getBoundingClientRect();
      var vh = window.innerHeight;
      if (rect.bottom < 0 || rect.top > vh) return;
      var center = rect.top + rect.height * 0.5;
      var offset = (center - vh * 0.5) * 0.06;
      bg.style.transform = 'translate3d(0,' + offset.toFixed(2) + 'px,0) scale(1.05)';
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
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
    initCinematicParallax();
    initImageProtection();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
