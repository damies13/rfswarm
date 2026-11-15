$(function() {
    const $dialog = $("#dialogue-scenariosettings");

    $dialog.dialog({
        autoOpen: false,
        close: function() {
            // Revert dropdowns back to saved values if closed via Cancel, Esc, or the X button
            const savedTheme = localStorage.getItem('preferred-theme') || 'tbar-auto';
            const savedLang = localStorage.getItem('preferred-lang') || i18next.resolvedLanguage || i18next.language.substring(0, 2);

            if ($('#theme-switcher').data('ui-selectmenu')) {
                $('#theme-switcher').val(savedTheme).selectmenu('refresh');
            }
            if ($('#lang-switcher').data('ui-selectmenu')) {
                $('#lang-switcher').val(savedLang).selectmenu('refresh');
            }
        }
    });

    // Apply jQuery UI theming to your HTML buttons
    $("#btn-scenariosettings-ok, #btn-scenariosettings-cancel").button();

    // Save button click handler
    $("#btn-scenariosettings-ok").on("click", function() {
        const currentTheme = localStorage.getItem('preferred-theme') || 'tbar-auto';
        const currentLang = localStorage.getItem('preferred-lang') || i18next.resolvedLanguage || 'en';

        const selectedTheme = $('#theme-switcher').val();
        const selectedLang = $('#lang-switcher').val();

        let needsReload = false;

        if (selectedTheme && selectedTheme !== currentTheme) {
            localStorage.setItem('preferred-theme', selectedTheme);
            needsReload = true;
        }

        if (selectedLang && selectedLang !== currentLang) {
            localStorage.setItem('preferred-lang', selectedLang);
            needsReload = true;
        }

        $dialog.dialog("close");

        if (needsReload) {
            window.location.reload();
        }
    });

    // Cancel button click handler
    $("#btn-scenariosettings-cancel").on("click", function() {
        $dialog.dialog("close");
    });

    const tabtestdefaults = 1;
    const savedTab = localStorage.getItem('scenariosettings-active-tab');
    const initialTab = savedTab !== null ? parseInt(savedTab, 10) : tabtestdefaults;

    $("#scenariosettings-tabs").tabs({
        active: initialTab,
        activate: function(event, ui) {
            localStorage.setItem('scenariosettings-active-tab', ui.newTab.index());
        }
    });
});
