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

	// scenariosettings
	$( "#dialogue-scenariosettings #upload-logs" ).selectmenu();

    $( "#dialogue-scenariosettings input[type='checkbox']" ).checkboxradio({
		icon: false
    });	

    $( "#percentile" ).spinner({
		min: 1,
		max: 99,
		step: 1,
		start: 90
    });

	// test defaults settings

	// manager settings
	const ipv4Regex = /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
	const ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:))$/;

	$('#bindip').on('input', function() {
		let val = $(this).val();

		// 1. Strip any character not valid in IPv4 or IPv6
		val = val.replace(/[^0-9a-fA-F.:]/g, '');

		// 2. Prevent multiple consecutive dots (invalid in both formats)
		val = val.replace(/\.{2,}/g, '.');

		// 3. Prevent more than two consecutive colons (only '::' is valid in IPv6)
		val = val.replace(/:{3,}/g, '::');

		$(this).val(val);

		// 4. Validate and display detected format
		if (val === '') {
			$('#bindip').text('');
		} else if (ipv4Regex.test(val)) {
			// $('#bindip').text('Valid IPv4').css('color', 'green');
			$('#bindip').text('Valid IPv4').css('color', '');
		} else if (ipv6Regex.test(val)) {
			// $('#bindip').text('Valid IPv6').css('color', 'green');
			$('#bindip').text('Valid IPv6').css('color', '');
		} else {
			$('#bindip').text('Invalid IP format').css('color', 'red');
		}
	});


    $( "#bindport" ).spinner({
		min: 1024,
		max: 65535,
		step: 1,
		start: 8138
    });

	$('#resultsloc-browse').on('click', function() {
		// let inputValue = $('#myTextbox').val();
		alert('open file browser');
	});

	// browser settings
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
