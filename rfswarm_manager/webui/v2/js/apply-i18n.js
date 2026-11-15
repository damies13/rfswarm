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

        // Sync and theme the language switcher if it is already in the DOM
        initLanguageSwitcher();
    });

// Helper function to sync value, translate options, and apply jQuery UI theming
function initLanguageSwitcher() {
    const $switcher = $('#lang-switcher');
    if (!$switcher.length) return;

    if ($switcher.data('ui-selectmenu')) {
        $switcher.selectmenu('destroy');
    }

    const currentLang = i18next.resolvedLanguage || i18next.language.substring(0, 2);
    $switcher.val(currentLang);
    $switcher.localize();

    $switcher.selectmenu({
        appendTo: "body",
        position: {
            my: "left top",
            at: "left bottom",
            collision: "none"
        },
        classes: {
            "ui-selectmenu-button": "ui-button"
        },
        open: function() {
            // Read the dialog's current incremented z-index and set the menu 10 layers higher
            var dialogZ = parseInt($(".ui-dialog:visible").css("z-index"), 10) || 1000;
            $(this).selectmenu("menuWidget").parent().css("z-index", dialogZ + 10);
        }
    });
}

// Trigger initialization when the dialog opens, AJAX content loads, or translations finish
$(document).on('i18n:complete ajaxSuccess dialogopen', function() {
    initLanguageSwitcher();
});

