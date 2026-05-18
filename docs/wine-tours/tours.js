(function () {
  var EMAIL = 'AlexTrips@hotmail.com';
  var WHATSAPP_BASE = 'https://wa.me/61421047915?text=';
  var MAX_WINERIES = 4;
  var WHATSAPP_ICON =
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>' +
    '</svg>';

  var TOUR_DEFS = [
    {
      id: 'yarra',
      routeId: 'yarra-route',
      title: 'YARRA VALLEY',
      subtitle: 'Private Winery Tour',
      image: 'img/tour-yarra.jpg?v=3',
      imagePosition: 'center 35%',
      detailHeading: 'Yarra Valley Private Winery Tour',
      tags: ['Tokar Estate', 'Oakridge Wines', 'Yering Station', 'Domaine Chandon', 'Coldstream Hills']
    },
    {
      id: 'mornington',
      routeId: 'mornington-route',
      title: 'MORNINGTON PENINSULA',
      subtitle: 'Private Winery Tour',
      image: 'img/tour-mornington.jpg?v=1',
      imagePosition: 'center 40%',
      detailHeading: 'Mornington Peninsula Private Winery Tour',
      tags: ['Montalto', 'Pt. Leo Estate', 'Paringa Estate', 'Ten Minutes by Tractor', 'Foxeys Hangout']
    }
  ];

  var selectedTourId = null;
  var selectedWineries = {};
  var selectedDates = {};

  function t(key) {
    return window.I18n ? window.I18n.t(key) : key;
  }

  function getLang() {
    return window.I18n ? window.I18n.getLang() : 'ru';
  }

  function wineryTypeLabel(type) {
    var lang = getLang();
    var types =
      window.TRANSLATIONS &&
      window.TRANSLATIONS[lang] &&
      window.TRANSLATIONS[lang].wineryTypes;
    return (types && types[type]) || type;
  }

  function getLocalizedTour(id) {
    var def = TOUR_DEFS.find(function (x) { return x.id === id; });
    if (!def) return null;
    var lang = getLang();
    var loc =
      (window.TOUR_CONTENT &&
        window.TOUR_CONTENT[id] &&
        (window.TOUR_CONTENT[id][lang] || window.TOUR_CONTENT[id].ru)) ||
      {};
    return Object.assign({}, def, loc);
  }

  function getTours() {
    return TOUR_DEFS.map(function (d) { return getLocalizedTour(d.id); }).filter(Boolean);
  }

  function minTourDateISO() {
    var d = new Date();
    var m = String(d.getMonth() + 1);
    var day = String(d.getDate());
    if (m.length < 2) m = '0' + m;
    if (day.length < 2) day = '0' + day;
    return d.getFullYear() + '-' + m + '-' + day;
  }

  function formatTourDate(isoDate) {
    if (!isoDate) return null;
    var parts = isoDate.split('-');
    if (parts.length !== 3) return null;
    var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (isNaN(d.getTime())) return null;
    var locale = getLang() === 'en' ? 'en-AU' : 'ru-RU';
    return d.toLocaleDateString(locale, { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function formatTourDateMobile(isoDate) {
    if (!isoDate) return null;
    var parts = isoDate.split('-');
    if (parts.length !== 3) return null;
    var d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (isNaN(d.getTime())) return null;
    if (getLang() === 'en') {
      return d.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });
    }
    return parts[2] + '.' + parts[1] + '.' + parts[0];
  }

  function generateBookingMessage(tourName, selectedDate, wineries) {
    var wineryBlock =
      wineries && wineries.length
        ? wineries.map(function (w) { return '- ' + w; }).join('\n')
        : '- ' + t('booking.wineriesNone');
    return (
      t('booking.msgGreeting') + '\n\n' +
      t('booking.msgBook') + ' ' + tourName + '.\n\n' +
      t('booking.msgDate') + ' ' + (selectedDate || t('booking.dateNotSet')) + '\n\n' +
      t('booking.msgWineries') + '\n' +
      wineryBlock + '\n\n' +
      t('booking.msgContact') + '\n\n' +
      t('booking.msgThanks')
    );
  }

  function buildBookingLinks(tour, picked) {
    var dateLabel = formatTourDate(selectedDates[tour.id]);
    var message = generateBookingMessage(tour.detailHeading, dateLabel, picked || []);
    var encoded = encodeURIComponent(message);
    var subject = encodeURIComponent(t('booking.emailSubject') + ' — ' + tour.title);
    return {
      mailto: 'mailto:' + EMAIL + '?subject=' + subject + '&body=' + encoded,
      whatsapp: WHATSAPP_BASE + encoded
    };
  }

  function refreshBookingLinks(tour, picked) {
    var panel = document.getElementById('routePanel');
    if (!panel) return;
    var links = buildBookingLinks(tour, picked);
    panel.querySelectorAll('[data-booking="whatsapp"]').forEach(function (a) {
      a.href = links.whatsapp;
    });
    panel.querySelectorAll('[data-booking="email"]').forEach(function (a) {
      a.href = links.mailto;
    });
    updateMobileBookingBar(tour, picked);
  }

  function updateMobileBookingBar(tour, picked) {
    var bar = document.getElementById('mobileBookingBar');
    if (!bar) return;
    picked = picked || [];
    var active = tour && selectedTourId && isMobileViewport();

    document.body.classList.toggle('booking-flow-active', !!(active && selectedTourId));

    if (!active) {
      bar.hidden = true;
      bar.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('has-mobile-booking-bar');
      return;
    }

    var countEl = document.getElementById('mbCount');
    var dateEl = document.getElementById('mbDate');
    var btn = document.getElementById('mbWhatsApp');
    var links = buildBookingLinks(tour, picked);
    var hasWineries = picked.length > 0;
    var iso = selectedDates[tour.id];

    bar.hidden = false;
    bar.setAttribute('aria-hidden', 'false');
    document.body.classList.add('has-mobile-booking-bar');

    if (countEl) {
      countEl.textContent = t('booking.selectedCount') + ': ' + picked.length + '/4';
    }
    if (dateEl) {
      if (iso) {
        dateEl.hidden = false;
        dateEl.textContent = t('booking.datePrefix') + ': ' + formatTourDateMobile(iso);
      } else {
        dateEl.hidden = true;
        dateEl.textContent = '';
      }
    }

    if (btn) {
      if (hasWineries) {
        btn.href = links.whatsapp;
        btn.target = '_blank';
        btn.rel = 'noopener noreferrer';
        btn.classList.remove('is-disabled');
        btn.removeAttribute('aria-disabled');
        btn.innerHTML = WHATSAPP_ICON + t('booking.whatsapp');
      } else {
        btn.href = '#';
        btn.removeAttribute('target');
        btn.removeAttribute('rel');
        btn.classList.add('is-disabled');
        btn.setAttribute('aria-disabled', 'true');
        btn.textContent = t('booking.selectWineriesCta');
      }
    }
  }

  function bindBookingControls(tour, picked) {
    var dateInput = document.getElementById('tourDateInput');
    if (dateInput) {
      dateInput.min = minTourDateISO();
      if (selectedDates[tour.id]) dateInput.value = selectedDates[tour.id];
      dateInput.addEventListener('change', function () {
        selectedDates[tour.id] = dateInput.value;
        refreshBookingLinks(tour, selectedWineries[tour.id] || []);
      });
    }
    refreshBookingLinks(tour, picked);
  }

  function renderSelectedSummary(tour, picked, links) {
    if (!picked.length) return '';
    return (
      '<div class="route-selected route-selected--compact" id="routeSelectedSummary">' +
        '<p class="route-selected__label">' + t('booking.selectedRoute') + ' (' + picked.length + '/' + MAX_WINERIES + '):</p>' +
        '<div class="route-selected__chips">' +
          picked.map(function (n) { return '<span class="route-chip">' + n + '</span>'; }).join('') +
        '</div>' +
        (selectedDates[tour.id]
          ? '<p class="route-selected__date">' + t('booking.datePrefix') + ': ' + formatTourDateMobile(selectedDates[tour.id]) + '</p>'
          : '') +
        '<a class="btn btn-email btn-sm" data-booking="email" href="' + links.mailto + '">' + t('booking.sendRoute') + '</a>' +
      '</div>'
    );
  }

  function iconSvg(name) {
    var icons = {
      clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
      grape: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="10" r="2"/><circle cx="12" cy="8" r="2"/><circle cx="16" cy="10" r="2"/><path d="M6 18c0-3 2-5 6-5s6 2 6 5"/></svg>',
      car: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 17h18l-2-7H5L3 17z"/><circle cx="7" cy="18" r="1.5"/><circle cx="17" cy="18" r="1.5"/></svg>',
      map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 20l6-14 4 6 6-10 4 18H4z"/></svg>',
      wave: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/><path d="M2 18c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/></svg>'
    };
    return icons[name] || icons.map;
  }

  function getTour(id) {
    return getLocalizedTour(id);
  }

  function isMobileViewport() {
    return window.matchMedia('(max-width: 768px)').matches;
  }

  function renderTourCards() {
    var grid = document.getElementById('toursGrid');
    if (!grid) return;
    grid.innerHTML = getTours().map(function (tour) {
      return (
        '<article class="tour-card tour-card--' + tour.id + (selectedTourId === tour.id ? ' is-active' : '') + '" data-tour-id="' + tour.id + '">' +
          '<div class="tour-card__visual">' +
            '<img class="tour-card__bg" src="' + tour.image + '" alt="" loading="lazy" style="object-position:' + tour.imagePosition + '">' +
            '<div class="tour-card__overlay" aria-hidden="true"></div>' +
          '</div>' +
          '<div class="tour-card__content">' +
            '<h3 class="tour-card__title">' + tour.title + '</h3>' +
            '<p class="tour-card__subtitle">' + tour.subtitle + '</p>' +
            '<p class="tour-card__desc">' + tour.description + '</p>' +
            '<ul class="tour-card__meta">' +
              tour.details.map(function (d) {
                return '<li><span class="tour-card__meta-icon">' + iconSvg(d.icon) + '</span>' + d.text + '</li>';
              }).join('') +
            '</ul>' +
            '<p class="tour-card__tags-label">' + t('tours.tagsLabel') + '</p>' +
            '<div class="tour-card__tags">' +
              tour.tags.map(function (tag) { return '<span class="tour-tag">' + tag + '</span>'; }).join('') +
            '</div>' +
            '<button type="button" class="btn tour-card__cta" data-route="' + tour.id + '">' + t('tours.viewRoute') + '</button>' +
          '</div>' +
        '</article>'
      );
    }).join('');

    grid.querySelectorAll('[data-route]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        openRoute(btn.getAttribute('data-route'));
      });
    });
  }

  function renderRoutePanel() {
    var panel = document.getElementById('routePanel');
    if (!panel) return;

    if (!selectedTourId) {
      panel.hidden = true;
      panel.innerHTML = '';
      updateMobileBookingBar(null, []);
      return;
    }

    var tour = getTour(selectedTourId);
    if (!tour) return;

    var picked = selectedWineries[tour.id] || [];
    var links = buildBookingLinks(tour, picked);

    panel.hidden = false;
    panel.innerHTML =
      '<div class="route-panel route-panel--editorial" id="' + tour.routeId + '">' +
        '<div class="route-panel__layout">' +
          '<aside class="route-sidebar">' +
            '<header class="route-panel__head">' +
              '<h3>' + tour.detailHeading + '</h3>' +
              '<p class="route-panel__intro route-panel__intro--desk">' + tour.detailIntro + '</p>' +
              '<p class="route-panel__note"><strong>' + t('booking.routeNoteBold') + '</strong> ' + t('booking.routeNote') + '</p>' +
            '</header>' +
            renderSelectedSummary(tour, picked, links) +
            '<section class="route-step route-step--date" aria-labelledby="routeStepDateLabel">' +
              '<p class="route-step__heading" id="routeStepDateLabel"><span class="route-step__num">1</span> ' + t('booking.stepDate') + '</p>' +
              '<p class="route-step__title route-step__title--mobile">' + t('booking.selectDate') + '</p>' +
              '<div class="route-date">' +
                '<label class="route-date__label" for="tourDateInput">' + t('booking.dateLabel') + '</label>' +
                '<input type="date" class="route-date__input" id="tourDateInput" min="' + minTourDateISO() + '" value="' + (selectedDates[tour.id] || '') + '">' +
              '</div>' +
            '</section>' +
            '<section class="route-step route-step--submit" aria-labelledby="routeStepSubmitLabel">' +
              '<p class="route-step__heading" id="routeStepSubmitLabel"><span class="route-step__num">3</span> ' + t('booking.stepSubmit') + '</p>' +
              '<div class="route-panel__ctas contact-actions">' +
                '<a class="btn btn-whatsapp" data-booking="whatsapp" href="' + links.whatsapp + '" target="_blank" rel="noopener noreferrer">' + WHATSAPP_ICON + t('booking.whatsapp') + '</a>' +
                '<a class="btn btn-telegram" href="#" tabindex="-1" aria-disabled="true">' + t('booking.telegram') + '</a>' +
                '<a class="btn btn-email" data-booking="email" href="' + links.mailto + '">' + t('booking.email') + '</a>' +
              '</div>' +
            '</section>' +
          '</aside>' +
          '<div class="route-main">' +
            '<section class="route-step route-step--wineries" aria-labelledby="routeStepWineriesLabel">' +
              '<p class="route-step__heading" id="routeStepWineriesLabel"><span class="route-step__num">2</span> ' + t('booking.stepWineries') + '</p>' +
              '<p class="route-step__title route-step__title--mobile">' + t('booking.selectWineries') + '</p>' +
              '<p class="route-limit" id="routeLimitMsg" hidden role="alert">' + t('booking.limitWarning') + '</p>' +
              '<div class="route-wineries">' +
          tour.wineries.map(function (w, i) {
            var isOn = picked.indexOf(w.name) !== -1;
            var num = String(i + 1).padStart(2, '0');
            return (
              '<article class="winery-card' + (isOn ? ' is-selected' : '') + '">' +
                '<span class="winery-card__num" aria-hidden="true">' + num + '</span>' +
                '<div class="winery-card__top">' +
                  '<h4>' + w.name + '</h4>' +
                  '<span class="winery-card__type">' + wineryTypeLabel(w.type) + '</span>' +
                '</div>' +
                '<p>' + w.desc + '</p>' +
                '<p class="winery-card__hours"><svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="10" cy="10" r="7"/><path d="M10 6v4l2.5 1.5"/></svg> ' + w.hours + '</p>' +
                '<button type="button" class="btn winery-add' + (isOn ? ' is-on' : '') + '" data-tour="' + tour.id + '" data-winery="' + i + '">' +
                  (isOn ? t('booking.inRoute') : t('booking.addToRoute')) +
                '</button>' +
              '</article>'
            );
          }).join('') +
              '</div>' +
            '</section>' +
          '</div>' +
        '</div>' +
      '</div>';

    panel.querySelectorAll('.winery-add').forEach(function (btn) {
      btn.addEventListener('click', function () {
        toggleWinery(btn.getAttribute('data-tour'), parseInt(btn.getAttribute('data-winery'), 10));
      });
    });

    bindBookingControls(tour, picked);
  }

  function toggleWinery(tourId, wineryIndex) {
    var tour = getTour(tourId);
    if (!tour) return;
    var name = tour.wineries[wineryIndex].name;
    if (!selectedWineries[tourId]) selectedWineries[tourId] = [];
    var list = selectedWineries[tourId];
    var idx = list.indexOf(name);
    if (idx !== -1) {
      list.splice(idx, 1);
    } else {
      if (list.length >= MAX_WINERIES) {
        var msg = document.getElementById('routeLimitMsg');
        if (msg) {
          msg.hidden = false;
          if (isMobileViewport()) {
            msg.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }
          setTimeout(function () { msg.hidden = true; }, 3500);
        }
        return;
      }
      list.push(name);
    }
    renderTourCards();
    renderRoutePanel();
  }

  function scrollToRoutePanel() {
    var panel = document.getElementById('routePanel');
    if (!panel || panel.hidden) return;
    requestAnimationFrame(function () {
      var navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h'), 10) || 76;
      var top = panel.getBoundingClientRect().top + window.scrollY - navH - 10;
      window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });
    });
  }

  function openRoute(tourId) {
    selectedTourId = tourId;
    if (!selectedWineries[tourId]) selectedWineries[tourId] = [];
    renderTourCards();
    renderRoutePanel();
    scrollToRoutePanel();
  }

  function refreshAll() {
    renderTourCards();
    renderRoutePanel();
  }

  window.openTourRoute = openRoute;

  function initTours() {
    refreshAll();
    window.addEventListener('resize', function () {
      if (!selectedTourId) return;
      var tour = getTour(selectedTourId);
      if (tour) updateMobileBookingBar(tour, selectedWineries[selectedTourId] || []);
    });
    document.addEventListener('languagechange', function () {
      refreshAll();
    });
    if (location.hash === '#yarra-route') openRoute('yarra');
    if (location.hash === '#mornington-route') openRoute('mornington');
  }

  if (window.I18n) {
    document.addEventListener('DOMContentLoaded', function () {
      window.I18n.init();
      initTours();
    });
  } else {
    initTours();
  }
})();
