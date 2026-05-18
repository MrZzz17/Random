(function () {
  var SMS = 'sms:+61421047915';
  var EMAIL = 'AlexTrips@hotmail.com';
  var MAX_WINERIES = 4;

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
      image: 'img/tour-mornington.jpg',
      imagePosition: '65% center',
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
      return;
    }

    var tour = getTour(selectedTourId);
    if (!tour) return;

    var picked = selectedWineries[tour.id] || [];
    var limitMsg = document.getElementById('routeLimitMsg');

    panel.hidden = false;
    panel.innerHTML =
      '<div class="route-panel" id="' + tour.routeId + '">' +
        '<header class="route-panel__head">' +
          '<h3>' + tour.detailHeading + '</h3>' +
          '<p class="route-panel__intro">' + tour.detailIntro + '</p>' +
          '<p class="route-panel__note"><strong>До 4 виноделен за поездку.</strong> Вы можете выбрать предпочитаемые винодельни, но маршрут ограничен 4 винодельнями за одну поездку.</p>' +
          '<div class="route-panel__ctas">' +
            '<a class="btn btn-gold" href="' + SMS + '">Написать нам в SMS</a>' +
            '<a class="btn btn-outline-dark" href="' + buildMailto(tour, picked) + '">Отправить email</a>' +
          '</div>' +
        '</header>' +
        (picked.length ? (
          '<div class="route-selected">' +
            '<p class="route-selected__label">Выбрано в маршрут (' + picked.length + '/' + MAX_WINERIES + '):</p>' +
            '<div class="route-selected__chips">' +
              picked.map(function (n) { return '<span class="route-chip">' + n + '</span>'; }).join('') +
            '</div>' +
            '<a class="btn btn-gold btn-sm" href="' + buildMailto(tour, picked) + '">Отправить выбранный маршрут</a>' +
          '</div>'
        ) : '') +
        '<p class="route-limit" id="routeLimitMsg" hidden>За одну поездку можно выбрать до 4 виноделен.</p>' +
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
                  (isOn ? 'В маршруте' : 'Добавить в маршрут') +
                '</button>' +
              '</article>'
            );
          }).join('') +
        '</div>' +
      '</div>';

    panel.querySelectorAll('.winery-add').forEach(function (btn) {
      btn.addEventListener('click', function () {
        toggleWinery(btn.getAttribute('data-tour'), parseInt(btn.getAttribute('data-winery'), 10));
      });
    });

    if (limitMsg) limitMsg.hidden = true;
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
          setTimeout(function () { msg.hidden = true; }, 3500);
        }
        return;
      }
      list.push(name);
    }
    renderTourCards();
    renderRoutePanel();
  }

  function buildMailto(tour, picked) {
    var subject = encodeURIComponent('Wine Tour Booking Request — ' + tour.title);
    var body = encodeURIComponent(
      'Здравствуйте,\n\n' +
      'Хочу забронировать винный тур: ' + tour.detailHeading + '.\n\n' +
      (picked.length ? 'Выбранные винодельни:\n- ' + picked.join('\n- ') + '\n\n' : '') +
      'Пожалуйста, свяжитесь со мной для уточнения даты и деталей.\n\n' +
      'Спасибо!'
    );
    return 'mailto:' + EMAIL + '?subject=' + subject + '&body=' + body;
  }

  function openRoute(tourId) {
    selectedTourId = tourId;
    if (!selectedWineries[tourId]) selectedWineries[tourId] = [];
    renderTourCards();
    renderRoutePanel();
    var panel = document.getElementById('routePanel');
    if (panel) {
      requestAnimationFrame(function () {
        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  }

  window.openTourRoute = openRoute;

  renderTourCards();
  renderRoutePanel();

  if (location.hash === '#yarra-route') openRoute('yarra');
  if (location.hash === '#mornington-route') openRoute('mornington');
})();
