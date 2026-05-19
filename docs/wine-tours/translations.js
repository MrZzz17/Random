/* global window */
(function () {
  window.TRANSLATIONS = {
    ru: {
      meta: {
        title: 'Alex Trips — Туры по винодельням Австралии',
        description:
          'Alex Trips Wine Tours — авторские винные туры по винодельням Австралии. Русскоязычное сопровождение из Мельбурна.'
      },
      nav: {
        home: 'Главная',
        regions: 'Регионы',
        tours: 'Туры и цены',
        included: 'Что входит',
        about: 'О нас',
        reviews: 'Отзывы',
        contact: 'Контакты',
        bookTour: 'Забронировать тур',
        bookShort: 'Забронировать',
        menuLabel: 'Меню',
        ariaLabel: 'Навигация',
        mobileAriaLabel: 'Мобильное меню',
        langAria: 'Выбор языка',
        closeLabel: 'Закрыть меню'
      },
      hero: {
        eyebrow: 'Вино · Природа · Атмосфера',
        titleHtml: 'Туры по<br>винодельням<br>Австралии',
        script: 'Откройте Австралию через вкус, пейзажи и вино',
        lead:
          'Авторские винные туры по лучшим регионам Австралии: Yarra Valley, Mornington Peninsula, Macedon Ranges и Geelong / Bellarine. Дегустации, красивые маршруты, локальная кухня и незабываемые впечатления.',
        cta: 'Посмотреть туры',
        imgAlt: 'Винный тур в виноградниках Австралии на закате'
      },
      features: {
        items: [
          'Комфортный трансфер',
          'Дегустации вин',
          'Обед на винодельне',
          'Русскоязычное сопровождение',
          'Индивидуальный маршрут'
        ],
        sectionAria: 'Что входит в тур',
        editorial: {
          eyebrow: 'Что входит',
          title: 'Вино, природа и Австралия — в одном дне',
          lead:
            'Каждый тур — это не набор остановок, а цельный сценарий: дорога, дегустации, обед, пейзажи и спокойный ритм без спешки.',
          imgAlt: 'Гости на винной дегустации среди виноградников',
          transferImgAlt: 'Комфортный автомобиль для винного тура'
        }
      },
      divider: {
        title: 'Идеальный день среди виноградников',
        lead:
          'Мы продумываем маршрут, темп, дегустации и атмосферу — вам остаётся только наслаждаться.'
      },
      timeline: {
        eyebrow: 'Маршрут дня',
        title: 'Как проходит день',
        lead: 'От выезда из Мельбурна до бокала на закате — каждый этап выстроен так, чтобы день ощущался лёгким и запоминающимся.',
        steps: [
          'Утренний выезд из Мельбурна',
          'Первая дегустация',
          'Обед на винодельне',
          'Ещё 2–3 остановки по маршруту',
          'Возвращение вечером'
        ]
      },
      regions: {
        eyebrow: 'Популярные регионы',
        title: 'Лучшие винные регионы Австралии',
        more: 'Подробнее',
        collapse: 'Свернуть'
      },
      tours: {
        eyebrow: 'Private Wine Experiences',
        title: 'Выберите ваш винный тур',
        sub: 'Каждый маршрут создаётся индивидуально под ваш вкус, темп и предпочтения.',
        tagsLabel: 'Винодельни, которые могут войти в маршрут',
        cardPrice: 'от USD $500+',
        cardPriceAria: 'Стоимость — от 500 долларов США с человека',
        viewRoute: 'Посмотреть маршрут →',
        benefits: [
          { strong: 'Частный тур', span: 'Только для вас и вашей компании' },
          { strong: 'Премиальные винодельни', span: 'Только лучшие винодельни региона' },
          { strong: 'Гастрономические опыты', span: 'Рестораны, дегустации и локальные деликатесы' },
          { strong: 'Живописные места', span: 'Лучшие виды, виноградники и фотолокации' }
        ],
        benefitsAria: 'Преимущества тура'
      },
      booking: {
        stepDate: 'Дата тура',
        stepWineries: 'Винодельни',
        stepSubmit: 'Отправить заявку',
        selectDate: 'Выберите дату',
        dateLabel: 'Желаемая дата тура',
        dateHint: '',
        selectWineries: 'Выберите до 4 виноделен',
        routeNote:
          'Вы можете выбрать предпочитаемые винодельни, но маршрут ограничен 4 винодельнями за одну поездку.',
        routeNoteBold: 'До 4 виноделен за поездку.',
        selectedRoute: 'Выбрано в маршрут',
        selectedWineries: 'Выбранные винодельни',
        sendRoute: 'Отправить выбранный маршрут',
        limitWarning: 'За одну поездку можно выбрать до 4 виноделен.',
        addToRoute: 'Добавить',
        inRoute: 'В маршруте',
        whatsapp: 'Написать в WhatsApp',
        email: 'Отправить Email',
        telegram: 'Написать в Telegram',
        selectWineriesCta: 'Выберите винодельни',
        selectedCount: 'Выбрано',
        datePrefix: 'Дата',
        wineriesNone: 'пока не выбраны',
        dateNotSet: 'не указана',
        emailSubject: 'Запрос на бронирование винного тура',
        msgGreeting: 'Здравствуйте!',
        msgBook: 'Хочу забронировать винный тур:',
        msgDate: 'Желаемая дата тура:',
        msgWineries: 'Выбранные винодельни:',
        msgContact: 'Пожалуйста, свяжитесь со мной для уточнения деталей.',
        msgThanks: 'Спасибо!'
      },
      why: {
        title: 'Почему выбирают нас',
        lead: 'Мы создаём персональный винный день — не шаблонную экскурсию в автобусе.',
        items: [
          'Индивидуальный подход',
          'Проверенные винодельни',
          'Комфорт и безопасность',
          'Незабываемые впечатления'
        ],
        panelTitle: 'Для кого наши туры',
        panelItems: [
          'Для пар',
          'Для компаний друзей',
          'Для туристов из СНГ',
          'Для корпоративных групп',
          'Для праздников и особых дат'
        ],
        reviewsAria: 'Отзывы гостей (заглушки)',
        reviewsNote: 'Скоро здесь появятся настоящие отзывы гостей',
        reviews: [
          {
            author: 'Марина К.',
            meta: 'Google · 2 недели назад',
            text: 'Лучший винный день в жизни! Подобрали винодельни под наш вкус — Pinot на закате просто магия.'
          },
          {
            text: 'Спасибо за тёплый приём! Обязательно вернёмся в Yarra с друзьями — Оля & Саша'
          },
          {
            label: 'WhatsApp',
            text: 'Алекс, спасибо за тур! Всё супер организовано, дети тоже в восторге 🍷',
            meta: 'вчера, 19:42'
          },
          {
            author: 'Дмитрий В.',
            meta: 'Google · октябрь 2025',
            text: 'Профессионально, без спешки, отличный гид. Рекомендуем всем, кто любит вино!'
          },
          {
            author: 'Елена и Михаил',
            text: 'Частный тур мечты: винодельни, обед с видом на виноградники, никакой суеты.'
          }
        ]
      },
      about: {
        title: 'О нас',
        eyebrow: 'Наша история',
        pullQuote:
          'Будто вы приехали к друзьям, которые давно живут в Австралии и хотят показать вам её настоящую сторону.',
        paragraphs: [
          'Мы — русскоговорящая пара из Мельбурна, уже много лет живущая в Австралии и по-настоящему влюблённая в эту страну. За это время Австралия стала для нас не просто домом, а местом, которым хочется делиться — через её природу, атмосферу, людей, гастрономию и, конечно, удивительную винную культуру.',
          'Мы сами много путешествуем по миру и всегда особенно ценим не «туристические программы», а тёплые, глубокие впечатления от местных людей — когда тебе показывают страну не по шаблону, а через личный взгляд и любовь к своему региону. Именно такой опыт мы стараемся создавать и для наших гостей.',
          'Мы с удовольствием рассказываем о вине простым и понятным языком на русском, помогаем открыть для себя лучшие винные регионы вокруг Мельбурна и подбираем маршруты так, чтобы они были не только красивыми, но и по-настоящему запоминающимися.',
          'Помимо винных туров, мы также можем помочь с рекомендациями и организацией отдыха в самом Мельбурне: лучшие рестораны, бары, океанские дороги, природа, скрытые места и любимые уголки местных жителей.',
          'Для нас это не просто работа. Это возможность знакомить людей с Австралией такой, какой мы сами её полюбили.'
        ],
        imgAlt: 'Основатели Alex Trips Wine Tours'
      },
      contact: {
        title: 'Свяжитесь с нами',
        sub: 'Мы с радостью подберём идеальный тур для вас',
        address: 'Адрес',
        email: 'Email',
        phone: 'Телефон',
        phoneNote: 'WhatsApp / Telegram',
        writeUs: 'Написать нам',
        contactWaText:
          'Здравствуйте! Интересует винный тур.',
        contactWaPhone: '61421047915'
      },
      footer: {
        copyright: '© 2026 Alex Trips Wine Tours'
      },
      wineryTypes: {
        'Boutique winery': 'Бутиковая винодельня',
        Restaurant: 'Ресторан',
        'Historic estate': 'Историческое поместье',
        'Cool-climate wines': 'Вина прохладного климата',
        'Sparkling wines': 'Игристые вина',
        'Estate & sculpture trail': 'Поместье и скульптурный парк',
        'Wine, food & art': 'Вино, еда и искусство',
        'Fine dining': 'Fine dining'
      }
    },
    en: {
      meta: {
        title: 'Alex Trips — Australian Winery Tours',
        description:
          'Alex Trips Wine Tours — curated private wine tours across Australia. Experienced guides from Melbourne.'
      },
      nav: {
        home: 'Home',
        regions: 'Regions',
        tours: 'Tours & pricing',
        included: "What's included",
        about: 'About us',
        reviews: 'Reviews',
        contact: 'Contact',
        bookTour: 'Book a tour',
        bookShort: 'Book now',
        menuLabel: 'Menu',
        ariaLabel: 'Navigation',
        mobileAriaLabel: 'Mobile menu',
        langAria: 'Language selection',
        closeLabel: 'Close menu'
      },
      hero: {
        eyebrow: 'Wine · Nature · Atmosphere',
        titleHtml: 'Australian<br>winery<br>tours',
        script: 'Discover Australia through taste, landscapes, and wine',
        lead:
          'Curated private wine tours to Australia\'s finest regions: Yarra Valley, Mornington Peninsula, Macedon Ranges, and Geelong / Bellarine. Tastings, scenic routes, local cuisine, and unforgettable experiences.',
        cta: 'View tours',
        imgAlt: 'Wine tour among Australian vineyards at sunset'
      },
      features: {
        items: [
          'Comfortable private transfer',
          'Wine tastings',
          'Winery lunch',
          'Experienced guides',
          'Custom itinerary'
        ],
        sectionAria: "What's included in the tour",
        editorial: {
          eyebrow: "What's included",
          title: 'Wine, nature, and Australia — in one day',
          lead:
            'Each tour is a single narrative: the drive, tastings, lunch, scenery, and an unhurried pace — never a checklist of stops.',
          imgAlt: 'Guests enjoying a wine tasting among the vines',
          transferImgAlt: 'Comfortable vehicle for a wine tour'
        }
      },
      divider: {
        title: 'The perfect day among the vines',
        lead:
          'We shape the route, pace, tastings, and atmosphere — you simply arrive and enjoy.'
      },
      timeline: {
        eyebrow: 'Your day',
        title: 'How the day unfolds',
        lead: 'From leaving Melbourne to a glass at sunset — every moment is paced to feel effortless and memorable.',
        steps: [
          'Morning departure from Melbourne',
          'First tasting',
          'Winery lunch',
          'Two or three more stops on your route',
          'Evening return'
        ]
      },
      regions: {
        eyebrow: 'Popular regions',
        title: "Australia's finest wine regions",
        more: 'Read more',
        collapse: 'Show less'
      },
      tours: {
        eyebrow: 'Private Wine Experiences',
        title: 'Choose your wine tour',
        sub: 'Every itinerary is tailored to your taste, pace, and preferences.',
        tagsLabel: 'Wineries that may be included on your route',
        cardPrice: 'from USD $500+',
        cardPriceAria: 'Pricing from five hundred US dollars per person',
        viewRoute: 'View itinerary →',
        benefits: [
          { strong: 'Private tour', span: 'Just for you and your group' },
          { strong: 'Premium wineries', span: 'Only the region\'s best estates' },
          { strong: 'Gastronomic experiences', span: 'Restaurants, tastings, and local delicacies' },
          { strong: 'Scenic highlights', span: 'Top views, vineyards, and photo spots' }
        ],
        benefitsAria: 'Tour highlights'
      },
      booking: {
        stepDate: 'Tour date',
        stepWineries: 'Wineries',
        stepSubmit: 'Send request',
        selectDate: 'Choose a date',
        dateLabel: 'Preferred tour date',
        dateHint: '',
        selectWineries: 'Choose up to 4 wineries',
        routeNote:
          'You may select your preferred wineries, but each trip is limited to 4 stops.',
        routeNoteBold: 'Up to 4 wineries per trip.',
        selectedRoute: 'On your itinerary',
        selectedWineries: 'Selected wineries',
        sendRoute: 'Send selected itinerary',
        limitWarning: 'You can select up to 4 wineries per trip.',
        addToRoute: 'Add to route',
        inRoute: 'Selected',
        whatsapp: 'Message on WhatsApp',
        email: 'Send email',
        telegram: 'Message on Telegram',
        selectWineriesCta: 'Select wineries',
        selectedCount: 'Selected',
        datePrefix: 'Date',
        wineriesNone: 'not selected yet',
        dateNotSet: 'not specified',
        emailSubject: 'Wine Tour Booking Request',
        msgGreeting: 'Hello!',
        msgBook: 'I would like to book a winery tour:',
        msgDate: 'Preferred tour date:',
        msgWineries: 'Selected wineries:',
        msgContact: 'Please contact me to confirm the details.',
        msgThanks: 'Thank you!'
      },
      why: {
        title: 'Why guests choose us',
        lead: 'We craft a personal wine day — not a template bus tour.',
        items: [
          'Personalised approach',
          'Trusted winery partners',
          'Comfort and safety',
          'Memorable experiences'
        ],
        panelTitle: 'Who our tours are for',
        panelItems: [
          'Couples',
          'Groups of friends',
          'International visitors',
          'Corporate groups',
          'Celebrations and special occasions'
        ],
        reviewsAria: 'Guest reviews (placeholders)',
        reviewsNote: 'Real guest review photos coming soon',
        reviews: [
          {
            author: 'Marina K.',
            meta: 'Google · 2 weeks ago',
            text: 'Best wine day of our lives! Wineries matched our taste — sunset Pinot was pure magic.'
          },
          {
            text: 'Thank you for the warm welcome! We will be back to Yarra with friends — Olya & Sasha'
          },
          {
            label: 'WhatsApp',
            text: 'Alex, thanks for the tour! Everything was seamless — the kids loved it too 🍷',
            meta: 'yesterday, 7:42 pm'
          },
          {
            author: 'Dmitry V.',
            meta: 'Google · October 2025',
            text: 'Professional, unhurried, excellent guide. Highly recommend for wine lovers!'
          },
          {
            author: 'Elena & Mikhail',
            text: 'A dream private tour: wineries, lunch overlooking the vines, zero rush.'
          }
        ]
      },
      about: {
        title: 'About us',
        eyebrow: 'Our story',
        pullQuote:
          'As if you have come to friends who have long lived in Australia and want to show you its real side.',
        paragraphs: [
          'We are a Russian-speaking couple based in Melbourne, living in Australia for many years and genuinely in love with this country. Over time, Australia has become more than home for us — it is a place we want to share through its nature, atmosphere, people, food, and remarkable wine culture.',
          'We travel widely ourselves and always value warm, personal experiences with locals — when a country is shown not from a template, but through someone’s own perspective and love for their region. That is the experience we aim to create for our guests.',
          'We are happy to talk about wine in clear, approachable Russian, help you discover the best wine regions around Melbourne, and shape routes that are not only scenic, but truly memorable.',
          'Beyond wine tours, we can also help with recommendations and planning time in Melbourne itself: restaurants, bars, coastal drives, nature, hidden spots, and favourite local corners.',
          'For us, this is not just work. It is a chance to introduce people to the Australia we have come to love.'
        ],
        imgAlt: 'Founders of Alex Trips Wine Tours'
      },
      contact: {
        title: 'Get in touch',
        sub: 'We will gladly help you choose the perfect tour',
        address: 'Address',
        email: 'Email',
        phone: 'Phone',
        phoneNote: 'WhatsApp / Telegram',
        writeUs: 'Message us',
        contactWaText:
          'Hello! I am interested in a wine tour.',
        contactWaPhone: '61421047915'
      },
      footer: {
        copyright: '© 2026 Alex Trips Wine Tours'
      },
      wineryTypes: {
        'Boutique winery': 'Boutique winery',
        Restaurant: 'Restaurant',
        'Historic estate': 'Historic estate',
        'Cool-climate wines': 'Cool-climate wines',
        'Sparkling wines': 'Sparkling wines',
        'Estate & sculpture trail': 'Estate & sculpture trail',
        'Wine, food & art': 'Wine, food & art',
        'Fine dining': 'Fine dining'
      }
    }
  };

  window.TOUR_CONTENT = {
    yarra: {
      ru: {
        title: 'ДОЛИНА',
        titleLine2: 'ЯРРА',
        titleEn: 'Yarra Valley',
        subtitle: 'Частный винный тур',
        detailHeading: 'Частный винный тур — Долина Ярра',
        description:
          'Классический винный регион недалеко от Мельбурна с лучшими Pinot Noir и Chardonnay<br>Австралии.',
        detailIntro:
          'Всего в часе езды от Мельбурна, Yarra Valley известна зелёными виноградниками, award-winning wines и красивыми видами. Это один из лучших регионов для Pinot Noir, Chardonnay и спокойного винного дня за городом.',
        details: [
          { icon: 'clock', text: '6–8 часов' },
          { icon: 'grape', text: 'До 4 виноделен' },
          { icon: 'car', text: 'Частный трансфер' },
          { icon: 'map', text: 'Индивидуальный маршрут' }
        ],
        wineries: [
          {
            name: 'Tokar Estate',
            type: 'Boutique winery',
            desc: 'Семейная винодельня с тёплой атмосферой, средиземноморским стилем и уютным cellar door. Хороший вариант для расслабленной дегустации и обеда.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Oakridge Wines',
            type: 'Restaurant',
            desc: 'Одна из самых известных виноделен Yarra Valley, расположенная вдоль Yarra River. Известна качественными винами, современной кухней и сильной ресторанной программой.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Yering Station',
            type: 'Historic estate',
            desc: 'Историческая винодельня, основанная в 1838 году, считается первой винодельней Victoria. Сочетает исторический характер, современные вина и красивые виды.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Coldstream Hills',
            type: 'Cool-climate wines',
            desc: 'Основана James Halliday в 1985 году и считается benchmark для cool-climate wines в Yarra Valley. Отличный выбор для Chardonnay и Pinot Noir.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: "Payne's Rise",
            type: 'Boutique winery',
            desc: 'Небольшая винодельня на исторической территории в Seville. Подходит для тех, кто любит handcrafted, small-batch wines и спокойную garden setting атмосферу.',
            hours: 'Friday to Sunday, 11 AM – 5 PM; Public Holidays, 11 AM – 5 PM'
          },
          {
            name: 'Domaine Chandon',
            type: 'Sparkling wines',
            desc: 'Известна sparkling wines, красивой архитектурой и панорамными видами на виноградники. Хороший premium stop для гостей, которые хотят более эффектный опыт.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'De Bortoli Wines',
            type: 'Restaurant',
            desc: 'Известная семейная винодельня с premium cool-climate wines и Italian-inspired рестораном Locale.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Seville Hill',
            type: 'Boutique winery',
            desc: 'Boutique winery с красивыми видами, charming cellar door и выбором Shiraz, Cabernet Sauvignon и Chardonnay. По выходным возможна живая jazz atmosphere.',
            hours: 'Wednesday to Sunday, 10 AM – 5 PM'
          }
        ]
      },
      en: {
        description:
          'A classic wine region near Melbourne, home to some of Australia\'s finest<br>Pinot Noir and Chardonnay.',
        detailIntro:
          'Just an hour from Melbourne, Yarra Valley is known for green vineyards, award-winning wines, and beautiful views. It is one of the best regions for Pinot Noir, Chardonnay, and a relaxed wine day out of the city.',
        details: [
          { icon: 'clock', text: '6–8 hours' },
          { icon: 'grape', text: 'Up to 4 wineries' },
          { icon: 'car', text: 'Private transfer' },
          { icon: 'map', text: 'Custom itinerary' }
        ],
        wineries: [
          {
            name: 'Tokar Estate',
            type: 'Boutique winery',
            desc: 'A family winery with a warm atmosphere, Mediterranean style, and a welcoming cellar door — ideal for a relaxed tasting and lunch.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Oakridge Wines',
            type: 'Restaurant',
            desc: 'One of Yarra Valley\'s best-known wineries on the Yarra River, celebrated for quality wines, modern cuisine, and a strong restaurant program.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Yering Station',
            type: 'Historic estate',
            desc: 'Founded in 1838, this historic estate is considered Victoria\'s first winery. It blends heritage character, contemporary wines, and scenic views.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Coldstream Hills',
            type: 'Cool-climate wines',
            desc: 'Founded by James Halliday in 1985 and regarded as a benchmark for cool-climate wines in Yarra Valley — excellent for Chardonnay and Pinot Noir.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: "Payne's Rise",
            type: 'Boutique winery',
            desc: 'A small winery on historic land in Seville, perfect for guests who enjoy handcrafted, small-batch wines in a peaceful garden setting.',
            hours: 'Friday to Sunday, 11 AM – 5 PM; Public Holidays, 11 AM – 5 PM'
          },
          {
            name: 'Domaine Chandon',
            type: 'Sparkling wines',
            desc: 'Famous for sparkling wines, striking architecture, and panoramic vineyard views — a premium stop for a more elevated experience.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'De Bortoli Wines',
            type: 'Restaurant',
            desc: 'A well-known family winery with premium cool-climate wines and the Italian-inspired Locale restaurant.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Seville Hill',
            type: 'Boutique winery',
            desc: 'A boutique winery with beautiful views, a charming cellar door, and Shiraz, Cabernet Sauvignon, and Chardonnay. Live jazz on weekends.',
            hours: 'Wednesday to Sunday, 10 AM – 5 PM'
          }
        ]
      }
    },
    mornington: {
      ru: {
        title: 'ПОЛУОСТРОВ',
        titleLine2: 'МОРНИНГТОН',
        titleEn: 'Mornington Peninsula',
        subtitle: 'Частный винный тур',
        detailHeading: 'Частный винный тур — Полуостров Морнингтон',
        description:
          'Идеальное сочетание вин, океанских видов, гастрономии и атмосферы побережья.',
        detailIntro:
          'Mornington Peninsula находится к югу от Мельбурна и сочетает cool-climate wines, холмы, океанские виды и атмосферу coastal escape. Это отличный маршрут для тех, кто хочет совместить дегустации, красивые пляжи и гастрономию.',
        details: [
          { icon: 'clock', text: '6–8 часов' },
          { icon: 'grape', text: 'До 4 виноделен' },
          { icon: 'car', text: 'Частный трансфер' },
          { icon: 'wave', text: 'Coastal wine experience' }
        ],
        wineries: [
          {
            name: 'Montalto Vineyard & Olive Grove',
            type: 'Estate & sculpture trail',
            desc: 'Винодельня с vineyard, olive grove и sculpture trail. Отличный вариант для тех, кто хочет совместить дегустацию, прогулку и красивую визуальную атмосферу.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Paringa Estate',
            type: 'Restaurant',
            desc: 'Известна premium cool-climate wines и сильной ресторанной программой. Хороший выбор для fine dining и более гастрономического тура.',
            hours: 'Daily, 11 AM – 6 PM'
          },
          {
            name: 'Pt. Leo Estate',
            type: 'Wine, food & art',
            desc: 'Сочетает wine, food and art. На территории есть cellar door, ресторан, масштабный sculpture park и впечатляющие виды.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Ten Minutes by Tractor',
            type: 'Fine dining',
            desc: 'Одна из наиболее известных виноделен региона, особенно для Pinot Noir и Chardonnay. Подходит для более intimate tasting experience и ценителей вина.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Foxeys Hangout',
            type: 'Boutique winery',
            desc: 'Расслабленная и дружелюбная атмосфера, handcrafted wines, sparkling wines и cool-climate varietals. Хороший вариант для менее формальной остановки.',
            hours: 'Friday to Sunday, 11 AM – 5 PM'
          }
        ]
      },
      en: {
        description:
          'The perfect blend of wine, ocean views, gastronomy, and coastal atmosphere.',
        detailIntro:
          'South of Melbourne, Mornington Peninsula pairs cool-climate wines with rolling hills, ocean views, and a coastal escape feel — ideal for tastings, beautiful beaches, and great food.',
        details: [
          { icon: 'clock', text: '6–8 hours' },
          { icon: 'grape', text: 'Up to 4 wineries' },
          { icon: 'car', text: 'Private transfer' },
          { icon: 'wave', text: 'Coastal wine experience' }
        ],
        wineries: [
          {
            name: 'Montalto Vineyard & Olive Grove',
            type: 'Estate & sculpture trail',
            desc: 'A winery with vineyards, olive groves, and a sculpture trail — great for combining tasting, a walk, and striking surroundings.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Paringa Estate',
            type: 'Restaurant',
            desc: 'Known for premium cool-climate wines and a strong restaurant program — an excellent choice for fine dining and a more gastronomic tour.',
            hours: 'Daily, 11 AM – 6 PM'
          },
          {
            name: 'Pt. Leo Estate',
            type: 'Wine, food & art',
            desc: 'Combines wine, food, and art with a cellar door, restaurant, large sculpture park, and impressive views.',
            hours: 'Daily, 10 AM – 5 PM'
          },
          {
            name: 'Ten Minutes by Tractor',
            type: 'Fine dining',
            desc: 'One of the region\'s most celebrated wineries, especially for Pinot Noir and Chardonnay — suited to intimate tastings and serious wine lovers.',
            hours: 'Daily, 11 AM – 5 PM'
          },
          {
            name: 'Foxeys Hangout',
            type: 'Boutique winery',
            desc: 'A relaxed, friendly stop with handcrafted wines, sparkling wines, and cool-climate varietals — perfect for a less formal visit.',
            hours: 'Friday to Sunday, 11 AM – 5 PM'
          }
        ]
      }
    }
  };

  window.REGION_CONTENT = {
    yarra: {
      ru: {
        teaser: 'В часе от Мельбурна — шампанское, элегантный пинот и живописные холмы.',
        more: [
          '<p>Всего в часе езды от Мельбурна — один из самых известных винных регионов Австралии. Yarra Valley славится прохладным климатом, утренними туманами и холмистыми пейзажами, благодаря которым здесь рождаются одни из лучших Pinot Noir и Chardonnay в стране. Регион сочетает премиальные винодельни, уютные семейные estate, гастрономию мирового уровня и расслабленную атмосферу австралийской countryside.</p>',
          '<p>Среди самых рекомендуемых виноделен — <a href="https://www.domainechandon.com.au/" target="_blank" rel="noopener noreferrer">Domaine Chandon</a> для игристых в стиле Champagne, <a href="https://www.yeringstation.com/" target="_blank" rel="noopener noreferrer">Yering Station</a> — старейшая винодельня региона с красивым рестораном и мощными Cabernet Sauvignon, <a href="https://www.oakridgewines.com.au/" target="_blank" rel="noopener noreferrer">Oakridge Wines</a> с одним из лучших дегустационных меню в долине, а также <a href="https://www.levantinehill.com.au/" target="_blank" rel="noopener noreferrer">Levantine Hill</a> — роскошное estate с архитектурным рестораном и выдающимися Shiraz и Chardonnay.</p>',
          '<p>Обязательно стоит попробовать местные Pinot Noir — элегантные, с нотами вишни, лесных ягод и специй, прохладноклиматный Chardonnay с минеральностью и цитрусом, а также игристые вина méthode traditionnelle. Любителям более насыщенных вин стоит обратить внимание на Shiraz из северной части долины и выдержанные Cabernet blends.</p>',
          '<p>Помимо вина, Yarra Valley известна сырными фермами, artisan chocolate, локальными рынками и панорамными ресторанами с видами на виноградники. Лучшее время для поездки — март–май, когда начинается австралийская осень: виноградники окрашиваются в золотые и бордовые оттенки, а погода идеально подходит для долгих дегустаций и неспешных обедов на террасах.</p>'
        ]
      },
      en: {
        teaser: 'An hour from Melbourne — sparkling wine, elegant Pinot, and rolling hills.',
        more: [
          '<p>Just an hour\'s drive from Melbourne, Yarra Valley is one of Australia\'s best-known wine regions. Cool climate, morning mist, and hilly landscapes help produce some of the country\'s finest Pinot Noir and Chardonnay. The region combines premium wineries, intimate family estates, world-class dining, and relaxed Australian countryside.</p>',
          '<p>Highly recommended stops include <a href="https://www.domainechandon.com.au/" target="_blank" rel="noopener noreferrer">Domaine Chandon</a> for Champagne-style sparkling wines, <a href="https://www.yeringstation.com/" target="_blank" rel="noopener noreferrer">Yering Station</a> — the region\'s oldest winery with a beautiful restaurant and powerful Cabernet Sauvignon, <a href="https://www.oakridgewines.com.au/" target="_blank" rel="noopener noreferrer">Oakridge Wines</a> with one of the valley\'s best tasting menus, and <a href="https://www.levantinehill.com.au/" target="_blank" rel="noopener noreferrer">Levantine Hill</a> — a luxury estate with striking architecture and outstanding Shiraz and Chardonnay.</p>',
          '<p>Be sure to try local Pinot Noir — elegant, with cherry, forest berry, and spice notes — cool-climate Chardonnay with minerality and citrus, and méthode traditionnelle sparkling wines. Fans of fuller-bodied wines should look to Shiraz from the northern valley and aged Cabernet blends.</p>',
          '<p>Beyond wine, Yarra Valley is known for cheese farms, artisan chocolate, local markets, and panoramic vineyard restaurants. The best time to visit is March–May, when Australian autumn begins: vineyards turn gold and burgundy, and the weather is perfect for long tastings and leisurely terrace lunches.</p>'
        ]
      }
    },
    mornington: {
      ru: {
        teaser: 'Побережье, морской бриз и утончённый пинот нуар у воды.',
        more: [
          '<p>Mornington Peninsula — один из самых живописных винных регионов Виктории, расположенный между заливом Port Phillip Bay и открытым океаном. Благодаря прохладному морскому климату здесь создаются изящные вина с яркой кислотностью, а сама атмосфера сочетает luxury retreat, coastal lifestyle и расслабленный австралийский шик.</p>',
          '<p>Регион особенно знаменит своими Pinot Noir и Chardonnay — свежими, минеральными и очень гастрономичными. Здесь также производят отличные Pinot Gris, Syrah и игристые вина. Винодельни часто расположены среди холмов с видом на океан, а многие estate объединяют cellar door, рестораны и дизайнерские пространства для отдыха.</p>',
          '<p>Среди самых рекомендуемых виноделен — <a href="https://www.montalto.com.au/" target="_blank" rel="noopener noreferrer">Montalto</a> с красивыми садами и современной австралийской кухней, <a href="https://www.tenminutesbytractor.com.au/" target="_blank" rel="noopener noreferrer">Ten Minutes by Tractor</a> — культовая winery с fine dining рестораном, <a href="https://www.ptleoestate.com.au/" target="_blank" rel="noopener noreferrer">Pt. Leo Estate</a> с масштабным sculpture park и панорамными видами на залив, а также <a href="https://polperro.com.au/" target="_blank" rel="noopener noreferrer">Polperro Winery</a> — уютное boutique estate с выдающимся Pinot Noir.</p>',
          '<p>Помимо виноделен, Mornington Peninsula известен термальными источниками <a href="https://www.peninsulahotsprings.com/" target="_blank" rel="noopener noreferrer">Peninsula Hot Springs</a>, прибрежными ресторанами, пляжами и живописными coastal drives. Это идеальное направление для тех, кто хочет совместить премиальные дегустации с отдыхом у моря, долгими обедами на террасах и атмосферой спокойной роскоши.</p>',
          '<p>Лучшее время для поездки — с ноября по апрель, когда полуостров особенно красив: солнечные виноградники, свежий океанский воздух и мягкие вечера создают идеальные условия для wine tasting и отдыха на побережье.</p>'
        ]
      },
      en: {
        teaser: 'Coastline, sea breeze, and refined Pinot Noir by the water.',
        more: [
          '<p>Mornington Peninsula is one of Victoria\'s most scenic wine regions, between Port Phillip Bay and the open ocean. Cool maritime climate yields elegant wines with bright acidity, while the atmosphere blends luxury retreat, coastal lifestyle, and relaxed Australian chic.</p>',
          '<p>The region is especially famous for Pinot Noir and Chardonnay — fresh, mineral, and highly food-friendly. It also produces excellent Pinot Gris, Syrah, and sparkling wines. Wineries often sit on hills overlooking the ocean, and many estates combine cellar doors, restaurants, and designer spaces for relaxation.</p>',
          '<p>Top recommendations include <a href="https://www.montalto.com.au/" target="_blank" rel="noopener noreferrer">Montalto</a> with beautiful gardens and modern Australian cuisine, <a href="https://www.tenminutesbytractor.com.au/" target="_blank" rel="noopener noreferrer">Ten Minutes by Tractor</a> — an iconic winery with a fine-dining restaurant, <a href="https://www.ptleoestate.com.au/" target="_blank" rel="noopener noreferrer">Pt. Leo Estate</a> with a large sculpture park and bay views, and <a href="https://polperro.com.au/" target="_blank" rel="noopener noreferrer">Polperro Winery</a> — a charming boutique estate with outstanding Pinot Noir.</p>',
          '<p>Beyond wineries, Mornington Peninsula is known for <a href="https://www.peninsulahotsprings.com/" target="_blank" rel="noopener noreferrer">Peninsula Hot Springs</a>, coastal restaurants, beaches, and scenic coastal drives. It is ideal for guests who want premium tastings with time by the sea, long terrace lunches, and an atmosphere of calm luxury.</p>',
          '<p>The best time to visit is November through April, when the peninsula is at its most beautiful: sunlit vineyards, fresh ocean air, and mild evenings — perfect for wine tasting and coastal relaxation.</p>'
        ]
      }
    },
    macedon: {
      ru: {
        teaser: 'Прохладный климат, туманные холмы и элегантные Pinot Noir и Chardonnay.',
        more: [
          '<p>Прохладный климат, туманные холмы и элегантные Pinot Noir и Chardonnay. Macedon Ranges — один из самых высокогорных и прохладных винных регионов Австралии, расположенный менее чем в часе от Мельбурна. Здесь виноградники разбросаны среди эвкалиптовых лесов, старинных деревень и зелёных холмов, создавая атмосферу спокойного countryside retreat вдали от городской суеты.</p>',
          '<p>Регион особенно известен своими утончёнными Pinot Noir, минеральными Chardonnay и одними из лучших игристых вин в Виктории. Благодаря прохладным ночам вина получаются свежими, структурными и очень европейскими по стилю. Здесь меньше крупных коммерческих winery и больше boutique estate с камерной атмосферой и персональными дегустациями.</p>',
          '<p>Среди самых рекомендуемых виноделен — <a href="https://bindiwines.com.au/" target="_blank" rel="noopener noreferrer">Bindi Wines</a> — культовое небольшое хозяйство с выдающимся Chardonnay и Pinot Noir, <a href="https://curlyflat.com/" target="_blank" rel="noopener noreferrer">Curly Flat</a> — одно из самых уважаемых Pinot Noir estate Австралии, <a href="https://www.hangingrock.com.au/" target="_blank" rel="noopener noreferrer">Hanging Rock Winery</a> с красивыми видами на вулканические холмы, а также <a href="https://cobawridge.com.au/" target="_blank" rel="noopener noreferrer">Cobaw Ridge</a> — biodynamic winery, известная своими Syrah и натуральным подходом к виноделию.</p>',
          '<p>Обязательно стоит попробовать местные méthode traditionnelle sparkling wines, прохладноклиматный Chardonnay с цитрусовой минеральностью и тонкие Pinot Noir с нотами лесных ягод, специй и землистости. Любителям необычных вин также понравятся Syrah в северно-роданском стиле и небольшие партии натуральных вин от независимых производителей.</p>',
          '<p>Помимо виноделен, Macedon Ranges славится фермерскими рынками, историческими пабами, гастрономическими ресторанами и природными достопримечательностями вроде <a href="https://www.mrsc.vic.gov.au/See-Do/Our-Region/Natural-Attractions/Hanging-Rock" target="_blank" rel="noopener noreferrer">Hanging Rock</a>. Осенью регион особенно красив: золотые виноградники, прохладный воздух и туманные утра делают поездку невероятно атмосферной и идеально подходящей для неспешных дегустаций и weekend getaway.</p>'
        ]
      },
      en: {
        teaser: 'Cool climate, misty hills, and elegant Pinot Noir and Chardonnay.',
        more: [
          '<p>Cool climate, misty hills, and elegant Pinot Noir and Chardonnay. Macedon Ranges is one of Australia\'s highest and coolest wine regions, less than an hour from Melbourne. Vineyards are scattered among eucalyptus forests, historic villages, and green hills — a peaceful countryside retreat away from the city.</p>',
          '<p>The region is especially known for refined Pinot Noir, mineral Chardonnay, and some of Victoria\'s finest sparkling wines. Cool nights produce fresh, structured wines with a distinctly European style. There are fewer large commercial wineries and more boutique estates with intimate tastings.</p>',
          '<p>Top picks include <a href="https://bindiwines.com.au/" target="_blank" rel="noopener noreferrer">Bindi Wines</a> — a cult small producer with outstanding Chardonnay and Pinot Noir, <a href="https://curlyflat.com/" target="_blank" rel="noopener noreferrer">Curly Flat</a> — one of Australia\'s most respected Pinot Noir estates, <a href="https://www.hangingrock.com.au/" target="_blank" rel="noopener noreferrer">Hanging Rock Winery</a> with views over volcanic hills, and <a href="https://cobawridge.com.au/" target="_blank" rel="noopener noreferrer">Cobaw Ridge</a> — a biodynamic winery known for Syrah and a natural approach to winemaking.</p>',
          '<p>Try local méthode traditionnelle sparkling wines, cool-climate Chardonnay with citrus minerality, and delicate Pinot Noir with forest berry, spice, and earthy notes. Wine lovers will also enjoy northern Rhône-style Syrah and small batches of natural wines from independent producers.</p>',
          '<p>Beyond wineries, Macedon Ranges is known for farmers\' markets, historic pubs, gastronomic restaurants, and natural landmarks such as <a href="https://www.mrsc.vic.gov.au/See-Do/Our-Region/Natural-Attractions/Hanging-Rock" target="_blank" rel="noopener noreferrer">Hanging Rock</a>. In autumn the region is especially beautiful: golden vineyards, cool air, and misty mornings — perfect for unhurried tastings and a weekend getaway.</p>'
        ]
      }
    },
    geelong: {
      ru: {
        teaser: 'Побережье Port Phillip Bay, прибрежные вина и relaxed wine weekend у воды.',
        more: [
          '<p>Этот регион, расположенный вдоль побережья Port Phillip Bay к юго-западу от Мельбурна, сочетает морские пейзажи, relaxed coastal atmosphere и одни из самых недооценённых вин Австралии. Здесь виноградники соседствуют с пляжами, яхтенными маринами и небольшими прибрежными городками, создавая идеальное направление для неспешного wine weekend у воды.</p>',
          '<p>Прохладный морской климат делает регион особенно сильным в Pinot Noir, Chardonnay и ароматных Pinot Gris. Вина здесь обычно более мягкие и округлые, чем в Yarra Valley, с выраженной минеральностью и свежестью благодаря постоянному океанскому бризу. Bellarine Peninsula также постепенно становится известным благодаря качественным Shiraz и игристым винам.</p>',
          '<p>Среди самых рекомендуемых виноделен — <a href="https://www.jackrabbitvineyard.com.au/" target="_blank" rel="noopener noreferrer">Jack Rabbit Vineyard</a> с панорамными видами на залив и одним из самых красивых ресторанов региона, <a href="https://www.scotchmans.com.au/" target="_blank" rel="noopener noreferrer">Scotchmans Hill</a> — одно из ведущих estate Bellarine с отличными Chardonnay и Shiraz, <a href="https://www.oakdene.com.au/" target="_blank" rel="noopener noreferrer">Oakdene Vineyards</a> — стильная boutique winery с арт-пространством и атмосферным cellar door, а также <a href="https://bannockburnvineyards.com/" target="_blank" rel="noopener noreferrer">Bannockburn Vineyards</a> — культовое хозяйство Geelong, известное своими сложными Pinot Noir и Chardonnay.</p>',
          '<p>Помимо дегустаций, регион славится coastal drives, свежими морепродуктами, устричными фермами и расслабленной атмосферой приморских townships вроде <a href="https://www.visitgeelongbellarine.com.au/queenscliff-point-lonsdale" target="_blank" rel="noopener noreferrer">Queenscliff</a> и <a href="https://www.visitgeelongbellarine.com.au/the-bellarine/portarlington" target="_blank" rel="noopener noreferrer">Portarlington</a>. Это идеальное направление для тех, кто хочет совместить вино, океан, гастрономию и красивые закаты над заливом.</p>',
          '<p>Лучшее время для поездки — с конца лета до середины осени, когда виноградники особенно красивы, а тёплая погода идеально подходит для долгих обедов на террасах с видом на воду и sunset wine tastings у побережья.</p>'
        ]
      },
      en: {
        teaser: 'Port Phillip Bay coastline, coastal wines, and a relaxed wine weekend by the water.',
        more: [
          '<p>Stretching along Port Phillip Bay southwest of Melbourne, this region combines sea views, a relaxed coastal atmosphere, and some of Australia\'s most underrated wines. Vineyards sit beside beaches, marinas, and small coastal towns — ideal for an easy wine weekend by the water.</p>',
          '<p>Cool maritime climate makes the region especially strong in Pinot Noir, Chardonnay, and aromatic Pinot Gris. Wines here are often softer and rounder than in Yarra Valley, with pronounced minerality and freshness from the constant ocean breeze. Bellarine Peninsula is also gaining recognition for quality Shiraz and sparkling wines.</p>',
          '<p>Highly recommended stops include <a href="https://www.jackrabbitvineyard.com.au/" target="_blank" rel="noopener noreferrer">Jack Rabbit Vineyard</a> with bay panoramas and one of the region\'s most beautiful restaurants, <a href="https://www.scotchmans.com.au/" target="_blank" rel="noopener noreferrer">Scotchmans Hill</a> — a leading Bellarine estate for Chardonnay and Shiraz, <a href="https://www.oakdene.com.au/" target="_blank" rel="noopener noreferrer">Oakdene Vineyards</a> — a stylish boutique winery with art space and an atmospheric cellar door, and <a href="https://bannockburnvineyards.com/" target="_blank" rel="noopener noreferrer">Bannockburn Vineyards</a> — a cult Geelong producer known for complex Pinot Noir and Chardonnay.</p>',
          '<p>Beyond tastings, the region is known for coastal drives, fresh seafood, oyster farms, and relaxed seaside townships such as <a href="https://www.visitgeelongbellarine.com.au/queenscliff-point-lonsdale" target="_blank" rel="noopener noreferrer">Queenscliff</a> and <a href="https://www.visitgeelongbellarine.com.au/the-bellarine/portarlington" target="_blank" rel="noopener noreferrer">Portarlington</a>. It is perfect for guests who want wine, ocean, gastronomy, and beautiful sunsets over the bay.</p>',
          '<p>The best time to visit is from late summer through mid-autumn, when vineyards are at their most beautiful and warm weather suits long terrace lunches overlooking the water and sunset tastings by the coast.</p>'
        ]
      }
    }
  };
})();
