(function () {
  'use strict';

  var menuBtn = document.getElementById('menuBtn');
  var mobileNav = document.getElementById('mobileNav');
  var mobileNavClose = document.getElementById('mobileNavClose');
  var mobileNavBackdrop = document.getElementById('mobileNavBackdrop');
  var header = document.getElementById('siteHeader');
  var MOBILE_MQ = window.matchMedia('(max-width: 768px)');

  if (!menuBtn || !mobileNav) return;

  function isMobile() {
    return MOBILE_MQ.matches;
  }

  function setMenuOpen(open) {
    menuBtn.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    mobileNav.hidden = !open;
    mobileNav.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.classList.toggle('nav-open', open);
    if (open && mobileNavClose) {
      mobileNavClose.focus();
    } else if (!open && document.activeElement && mobileNav.contains(document.activeElement)) {
      menuBtn.focus();
    }
  }

  function closeMenu() {
    if (!mobileNav.hidden) setMenuOpen(false);
  }

  function toggleMenu() {
    setMenuOpen(mobileNav.hidden);
  }

  menuBtn.addEventListener('click', toggleMenu);
  if (mobileNavClose) mobileNavClose.addEventListener('click', closeMenu);
  if (mobileNavBackdrop) mobileNavBackdrop.addEventListener('click', closeMenu);

  mobileNav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });

  function onBreakpointChange() {
    if (!isMobile()) closeMenu();
  }

  if (typeof MOBILE_MQ.addEventListener === 'function') {
    MOBILE_MQ.addEventListener('change', onBreakpointChange);
  } else if (typeof MOBILE_MQ.addListener === 'function') {
    MOBILE_MQ.addListener(onBreakpointChange);
  }

  function onScroll() {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
