

(function() {
    var lightThemeUrl = "https://code.jquery.com/ui/1.13.3/themes/base/jquery-ui.css";
    var darkThemeUrl  = "https://code.jquery.com/ui/1.13.3/themes/vader/jquery-ui.css";

    // 1. Evaluate explicit choice overrides from local registry cache bounds
    var preferredTheme = localStorage.getItem('preferred-theme') || 'tbar-auto';
    var useDark = false;

    if (preferredTheme === 'tbar-dark') {
        useDark = true;
    } else if (preferredTheme === 'tbar-light') {
        useDark = false;
    } else {
        // If set to 'auto', fall back to auto-detecting the browser's native dark profile setting
        useDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // 2. Write a static link element tag directly into the document compilation pipeline
    // This removes the need for checking element IDs or managing delayed timing variables entirely
    document.write('<link rel="stylesheet" href="' + (useDark ? darkThemeUrl : lightThemeUrl) + '">');
})();

$(function() {
    function initThemeSwitcher() {
        const $themeSwitcher = $('#theme-switcher');
        if (!$themeSwitcher.length) return;

        // Destroy any existing instance so old settings don't get stuck
        if ($themeSwitcher.data('ui-selectmenu')) {
            $themeSwitcher.selectmenu('destroy');
        }

        // Set the dropdown value to match localStorage
        const savedTheme = localStorage.getItem('preferred-theme') || 'tbar-auto';
        $themeSwitcher.val(savedTheme);

        // Initialize fresh with the exact same layering rules as #lang-switcher
        $themeSwitcher.selectmenu({
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
                var dialogZ = parseInt($(".ui-dialog:visible").css("z-index"), 10) || 1000;
                $(this).selectmenu("menuWidget").parent().css("z-index", dialogZ + 10);
            }
        });
    }

    // Run on page load and whenever the dialog opens or AJAX loads
    initThemeSwitcher();
    $(document).on('ajaxSuccess dialogopen', function() {
        initThemeSwitcher();
    });

	$( "input[title]" ).tooltip();

});


