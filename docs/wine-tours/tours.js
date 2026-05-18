(function () {
  var EMAIL = 'AlexTrips@hotmail.com';
  var WHATSAPP_BASE = 'https://wa.me/61421047915?text=';
  var MAX_WINERIES = 4;
  var WHATSAPP_ICON =
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">' +
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>' +
    '</svg>';

  var tours = [
    {
      id: 'yarra',
      routeId: 'yarra-route',
      title: 'YARRA VALLEY',
      subtitle: 'Private Winery Tour',
      image: 'img/tour-yarra.jpg?v=3',
      imagePosition: 'center 35%',
      description: 'Классический винный регион недалеко от Мельбурна с лучшими Pinot Noir и Chardonnay Австралии.',
      details: [
        { icon: 'clock', text: '6–8 часов' },
        { icon: 'grape', text: 'До 4 виноделен' },
        { icon: 'car', text: 'Частный трансфер' },
        { icon: 'map', text: 'Индивидуальный маршрут' }
      ],
      tags: ['Tokar Estate', 'Oakridge Wines', 'Yering Station', 'Domaine Chandon', 'Coldstream Hills'],
      detailHeading: 'Yarra Valley Private Winery Tour',
      detailIntro: 'Всего в часе езды от Мельбурна, Yarra Valley известна зелёными виноградниками, award-winning wines и красивыми видами. Это один из лучших регионов для Pinot Noir, Chardonnay и спокойного винного дня за городом.',
      wineries: [
        { name: 'Tokar Estate', type: 'Boutique winery', desc: 'Семейная винодельня с тёплой атмосферой, средиземноморским стилем и уютным cellar door. Хороший вариант для расслабленной дегустации и обеда.', hours: 'Daily, 11 AM – 5 PM' },
        { name: 'Oakridge Wines', type: 'Restaurant', desc: 'Одна из самых известных виноделен Yarra Valley, расположенная вдоль Yarra River. Известна качественными винами, современной кухней и сильной ресторанной программой.', hours: 'Daily, 10 AM – 5 PM' },
        { name: 'Yering Station', type: 'Historic estate', desc: 'Историческая винодельня, основанная в 1838 году, считается первой винодельней Victoria. Сочетает исторический характер, современные вина и красивые виды.', hours: 'Daily, 10 AM – 5 PM' },
        { name: 'Coldstream Hills', type: 'Cool-climate wines', desc: 'Основана James Halliday в 1985 году и считается benchmark для cool-climate wines в Yarra Valley. Отличный выбор для Chardonnay и Pinot Noir.', hours: 'Daily, 10 AM – 5 PM' },
        { name: "Payne's Rise", type: 'Boutique winery', desc: 'Небольшая винодельня на исторической территории в Seville. Подходит для тех, кто любит handcrafted, small-batch wines и спокойную garden setting атмосферу.', hours: 'Friday to Sunday, 11 AM – 5 PM; Public Holidays, 11 AM – 5 PM' },
        { name: 'Domaine Chandon', type: 'Sparkling wines', desc: 'Известна sparkling wines, красивой архитектурой и панорамными видами на виноградники. Хороший premium stop для гостей, которые хотят более эффектный опыт.', hours: 'Daily, 10 AM – 5 PM' },
        { name: 'De Bortoli Wines', type: 'Restaurant', desc: 'Известная семейная винодельня с premium cool-climate wines и Italian-inspired рестораном Locale.', hours: 'Daily, 10 AM – 5 PM' },
        { name: 'Seville Hill', type: 'Boutique winery', desc: 'Boutique winery с красивыми видами, charming cellar door и выбором Shiraz, Cabernet Sauvignon и Chardonnay. По выходным возможна живая jazz atmosphere.', hours: 'Wednesday to Sunday, 10 AM – 5 PM' }
      ]
    },
    {
      id: 'mornington',
      routeId: 'mornington-route',
      title: 'MORNINGTON PENINSULA',
      subtitle: 'Private Winery Tour',
      image: 'img/tour-mornington.jpg?v=1',
      imagePosition: 'center 40%',
      description: 'Идеальное сочетание вин, океанских видов, гастрономии и атмосферы побережья.',
      details: [
        { icon: 'clock', text: '6–8 часов' },
        { icon: 'grape', text: 'До 4 виноделен' },
        { icon: 'car', text: 'Частный трансфер' },
        { icon: 'wave', text: 'Coastal wine experience' }
      ],
      tags: ['Montalto', 'Pt. Leo Estate', 'Paringa Estate', 'Ten Minutes by Tractor', 'Foxeys Hangout'],
      detailHeading: 'Mornington Peninsula Private Winery Tour',
      detailIntro: 'Mornington Peninsula находится к югу от Мельбурна и сочетает cool-climate wines, холмы, океанские виды и атмосферу coastal escape. Это отличный маршрут для тех, кто хочет совместить дегустации, красивые пляжи и гастрономию.',
      wineries: [
        { name: 'Montalto Vineyard & Olive Grove', type: 'Estate & sculpture trail', desc: 'Винодельня с vineyard, olive grove и sculpture trail. Отличный вариант для тех, кто хочет совместить дегустацию, прогулку и красивую визуальную атмосферу.', hours: 'Daily, 11 AM – 5 PM' },
        { name: 'Paringa Estate', type: 'Restaurant', desc: 'Известна premium cool-climate wines и сильной ресторанной программой. Хороший выбор для fine dining и более гастрономического тура.', hours: 'Daily, 11 AM – 6 PM' },
        { name: 'Pt. Leo Estate', type: 'Wine, food & art', desc: 'Сочетает wine, food and art. На территории есть cellar door, ресторан, масштабный sculpture park и впечатляющие виды.', hours: 'Daily, 10 AM – 5 PM' },
        { name: 'Ten Minutes by Tractor', type: 'Fine dining', desc: 'Одна из наиболее известных виноделен региона, особенно для Pinot Noir и Chardonnay. Подходит для более intimate tasting experience и ценителей вина.', hours: 'Daily, 11 AM – 5 PM' },
        { name: 'Foxeys Hangout', type: 'Boutique winery', desc: 'Расслабленная и дружелюбная атмосфера, handcrafted wines, sparkling wines и cool-climate varietals. Хороший вариант для менее формальной остановки.', hours: 'Friday to Sunday, 11 AM – 5 PM' }
      ]
    }
  ];

  var selectedTourId = null;
  var selectedWineries = {};
  var selectedDates = {};

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
    return d.toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function formatTourDateMobile(isoDate) {
    if (!isoDate) return null;
    var parts = isoDate.split('-');
    if (parts.length !== 3) return null;
    return parts[2] + '.' + parts[1] + '.' + parts[0];
  }

  function isMobileViewport() {
    return window.matchMedia('(max-width: 768px)').matches;
  }

  function generateBookingMessage(tourName, selectedDate, wineries) {
    var wineryBlock =
      wineries && wineries.length
        ? wineries.map(function (w) { return '- ' + w; }).join('\n')
        : '- пока не выбраны';
    return (
      'Здравствуйте!\n\n' +
      'Хочу забронировать винный тур: ' + tourName + '.\n\n' +
      'Желаемая дата тура: ' + (selectedDate || 'не указана') + '\n\n' +
      'Выбранные винодельни:\n' +
      wineryBlock + '\n\n' +
      'Пожалуйста, свяжитесь со мной для уточнения деталей.\n\n' +
      'Спасибо!'
    );
  }

  function buildBookingLinks(tour, picked) {
    var dateLabel = formatTourDate(selectedDates[tour.id]);
    var message = generateBookingMessage(tour.detailHeading, dateLabel, picked || []);
    var encoded = encodeURIComponent(message);
    var subject = encodeURIComponent('Wine Tour Booking Request — ' + tour.title);
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

    if (countEl) countEl.textContent = 'Выбрано: ' + picked.length + '/4';
    if (dateEl) {
      if (iso) {
        dateEl.hidden = false;
        dateEl.textContent = 'Дата: ' + formatTourDateMobile(iso);
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
        btn.innerHTML = WHATSAPP_ICON + 'Написать в WhatsApp';
      } else {
        btn.href = '#';
        btn.removeAttribute('target');
        btn.removeAttribute('rel');
        btn.classList.add('is-disabled');
        btn.setAttribute('aria-disabled', 'true');
        btn.textContent = 'Выберите винодельни';
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
        '<p class="route-selected__label">Выбрано в маршрут (' + picked.length + '/' + MAX_WINERIES + '):</p>' +
        '<div class="route-selected__chips">' +
          picked.map(function (n) { return '<span class="route-chip">' + n + '</span>'; }).join('') +
        '</div>' +
        (selectedDates[tour.id]
          ? '<p class="route-selected__date">Дата: ' + formatTourDateMobile(selectedDates[tour.id]) + '</p>'
          : '') +
        '<a class="btn btn-email btn-sm" data-booking="email" href="' + links.mailto + '">Отправить выбранный маршрут</a>' +
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
    return tours.find(function (t) { return t.id === id; });
  }

  function renderTourCards() {
    var grid = document.getElementById('toursGrid');
    if (!grid) return;
    grid.innerHTML = tours.map(function (t) {
      return (
        '<article class="tour-card' + (selectedTourId === t.id ? ' is-active' : '') + '" data-tour-id="' + t.id + '">' +
          '<div class="tour-card__visual">' +
            '<img class="tour-card__bg" src="' + t.image + '" alt="" loading="lazy" style="object-position:' + t.imagePosition + '">' +
            '<div class="tour-card__overlay" aria-hidden="true"></div>' +
          '</div>' +
          '<div class="tour-card__content">' +
            '<h3 class="tour-card__title">' + t.title + '</h3>' +
            '<p class="tour-card__subtitle">' + t.subtitle + '</p>' +
            '<p class="tour-card__desc">' + t.description + '</p>' +
            '<ul class="tour-card__meta">' +
              t.details.map(function (d) {
                return '<li><span class="tour-card__meta-icon">' + iconSvg(d.icon) + '</span>' + d.text + '</li>';
              }).join('') +
            '</ul>' +
            '<p class="tour-card__tags-label">Винодельни, которые могут войти в маршрут</p>' +
            '<div class="tour-card__tags">' +
              t.tags.map(function (tag) { return '<span class="tour-tag">' + tag + '</span>'; }).join('') +
            '</div>' +
            '<button type="button" class="btn tour-card__cta" data-route="' + t.id + '">Посмотреть маршрут →</button>' +
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
      '<div class="route-panel" id="' + tour.routeId + '">' +
        '<header class="route-panel__head">' +
          '<h3>' + tour.detailHeading + '</h3>' +
          '<p class="route-panel__intro route-panel__intro--desk">' + tour.detailIntro + '</p>' +
          '<p class="route-panel__note"><strong>До 4 виноделен за поездку.</strong> Вы можете выбрать предпочитаемые винодельни, но маршрут ограничен 4 винодельнями за одну поездку.</p>' +
        '</header>' +
        renderSelectedSummary(tour, picked, links) +
        '<div class="route-flow">' +
          '<section class="route-step route-step--date" aria-labelledby="routeStepDateLabel">' +
            '<p class="route-step__heading" id="routeStepDateLabel"><span class="route-step__num">1</span> Дата тура</p>' +
            '<p class="route-step__title route-step__title--mobile">Выберите дату</p>' +
            '<div class="route-date">' +
              '<label class="route-date__label" for="tourDateInput">Желаемая дата тура</label>' +
              '<input type="date" class="route-date__input" id="tourDateInput" min="' + minTourDateISO() + '" value="' + (selectedDates[tour.id] || '') + '">' +
            '</div>' +
          '</section>' +
          '<section class="route-step route-step--wineries" aria-labelledby="routeStepWineriesLabel">' +
            '<p class="route-step__heading" id="routeStepWineriesLabel"><span class="route-step__num">2</span> Винодельни</p>' +
            '<p class="route-step__title route-step__title--mobile">Выберите до 4 виноделен</p>' +
            '<p class="route-limit" id="routeLimitMsg" hidden role="alert">За одну поездку можно выбрать до 4 виноделен.</p>' +
            '<div class="route-wineries">' +
          tour.wineries.map(function (w, i) {
            var isOn = picked.indexOf(w.name) !== -1;
            return (
              '<article class="winery-card' + (isOn ? ' is-selected' : '') + '">' +
                '<div class="winery-card__top">' +
                  '<h4>' + w.name + '</h4>' +
                  '<span class="winery-card__type">' + w.type + '</span>' +
                '</div>' +
                '<p>' + w.desc + '</p>' +
                '<p class="winery-card__hours"><svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="10" cy="10" r="7"/><path d="M10 6v4l2.5 1.5"/></svg> ' + w.hours + '</p>' +
                '<button type="button" class="btn winery-add' + (isOn ? ' is-on' : '') + '" data-tour="' + tour.id + '" data-winery="' + i + '">' +
                  (isOn ? 'В маршруте' : 'Добавить') +
                '</button>' +
              '</article>'
            );
          }).join('') +
            '</div>' +
          '</section>' +
          '<section class="route-step route-step--submit" aria-labelledby="routeStepSubmitLabel">' +
            '<p class="route-step__heading" id="routeStepSubmitLabel"><span class="route-step__num">3</span> Отправить заявку</p>' +
            '<div class="route-panel__ctas contact-actions">' +
              '<a class="btn btn-whatsapp" data-booking="whatsapp" href="' + links.whatsapp + '" target="_blank" rel="noopener noreferrer">' + WHATSAPP_ICON + 'Написать в WhatsApp</a>' +
              '<a class="btn btn-email" data-booking="email" href="' + links.mailto + '">Отправить Email</a>' +
              '<!-- TODO: add Telegram username/link -->' +
              '<a class="btn btn-telegram" href="#" tabindex="-1" aria-disabled="true">Написать в Telegram</a>' +
            '</div>' +
          '</section>' +
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

  window.openTourRoute = openRoute;

  renderTourCards();
  renderRoutePanel();

  window.addEventListener('resize', function () {
    if (!selectedTourId) return;
    var tour = getTour(selectedTourId);
    if (tour) updateMobileBookingBar(tour, selectedWineries[selectedTourId] || []);
  });

  if (location.hash === '#yarra-route') openRoute('yarra');
  if (location.hash === '#mornington-route') openRoute('mornington');
})();
