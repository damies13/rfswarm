
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
    // 1. Initialize the theme selector element dropdown state
    const themeSwitcher = document.getElementById('theme-switcher');
    if (themeSwitcher) {
        // Read current local storage key and map the active selection option visually
        const savedTheme = localStorage.getItem('preferred-theme') || 'auto';
        themeSwitcher.value = savedTheme;

        // Convert the element natively using your patched selectmenu widget configurations
        $(themeSwitcher).selectmenu({
            classes: {
                "ui-selectmenu-button": "ui-button"
            },
            change: function(event, ui) {
                const selectedTheme = ui.item.value;
                
                // Save explicit choice string into local memory registry cache bounds
                localStorage.setItem('preferred-theme', selectedTheme);
                
                // 🚀 Force clean reload pass to let widgets redraw with zero layout dimension shifts
                window.location.reload();
            }
        });
    }
    
    // ... (your existing language switcher listener script continues undisturbed here)
});