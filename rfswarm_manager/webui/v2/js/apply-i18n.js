// Register the jQuery plugin IMMEDIATELY on script boot
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

        ns: ['translation', 'native-names'],
        defaultNS: 'translation',
        fallbackNS: 'native-names', // Ensures it falls back to native-names safely

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

        // 🌟 SAFETY GAP SYNC: Check if the language switcher is already present in the DOM on cold boot
        syncLanguageSwitcherDropdown();
    });

// 🌟 HELPER FUNCTION: Safely aligns the dropdown view value with our active dictionary code
function syncLanguageSwitcherDropdown() {
    const currentLang = i18next.resolvedLanguage || i18next.language.substring(0, 2);
    const switcher = document.getElementById('lang-switcher');
    if (switcher) {
        switcher.value = currentLang;
    }
}

// 🚀 THE BULLETPROOF EVENT DECOUPPLER: 
// We use jQuery document delegation to monitor changes globally. This guarantees it will 
// catch your change events even if the dropdown is dynamically loaded later inside a dialogue container!
$(document).on('change', '#lang-switcher', function(e) {
    const selectedLang = e.target.value;
    localStorage.setItem('preferred-lang', selectedLang);
    window.location.reload();
});

// 🚀 DIALOG PANEL BOOT HOOK:
// If you use standard jQuery UI .dialog() or a framework to open your scenario settings,
// we listen for any network asset injections to synchronize the display selector value instantly.
$(document).on('i18n:complete ajaxSuccess dialogopen', function() {
    syncLanguageSwitcherDropdown();
});
