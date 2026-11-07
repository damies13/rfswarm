// 🚀 1. Register the jQuery plugin IMMEDIATELY on script boot
// This guarantees that .localize() always exists right away, avoiding TypeErrors!
jqueryI18next.init(i18next, $, {
    tName: 't',
    i18nName: 'i18n',
    handleName: 'localize', 
    selectorAttr: 'data-i18n',
    optionsAttr: 'i18n-options',
    useOptionsAttr: false,
    parseDefaultValueFromContent: false
});

// Initialize i18next engine configurations
i18next
    .use(i18nextHttpBackend)
    .use(i18nextBrowserLanguageDetector)
    .init({
        fallbackLng: 'en',
        debug: true,
        load: 'all', 
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
            lookupLocalStorage: 'preferred-lang'
        },
        backend: { 
            loadPath: '/locales/{{lng}}/{{ns}}.json' 
        }
    }, function(err, t) {
        if (err) return console.error(err);
        
        // Translate the static index framework elements
        $('body').localize();

        // Sync dropdown language switcher display states
        const currentLang = i18next.resolvedLanguage;
        const switcher = document.getElementById('lang-switcher');
        if (switcher) switcher.value = currentLang;
    });

// Handle the user interaction dropdown lifecycle
$(function() {
    const switcher = document.getElementById('lang-switcher');
    if (switcher) {
        switcher.addEventListener('change', (e) => {
            const selectedLang = e.target.value;
            localStorage.setItem('preferred-lang', selectedLang);
            window.location.reload();
        });
    }
});
