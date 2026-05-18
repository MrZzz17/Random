(function () {
  'use strict';

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

  function initDecorativePhotos() {
    document.querySelectorAll('.editorial-features__photo').forEach(function (el) {
      el.addEventListener('contextmenu', function (e) {
        e.preventDefault();
      });
    });
  }

  function init() {
    initReveal();
    initDecorativePhotos();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
