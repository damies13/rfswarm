// Shared registry of DataTables that need to auto-fit inside jQuery UI tabs
window.AppDataTables = (function() {
	var registeredTables = [];

	// Calculates exact remaining viewport height for any given tab + DataTable
	function resizeSingleTable(tabSelector, dtInstance) {
		var $tab = $(tabSelector);
		if (!$tab.is(':visible') || document.hidden) return;

		var $scrollBody = $tab.find('.dt-scroll-body');
		var scrollBodyEl = $scrollBody.get(0);
		if (!scrollBodyEl) return;

		var $tabsWrapper = $tab.closest('.ui-tabs');
		var tabsWrapperEl = $tabsWrapper.get(0);
		var scrollRect = scrollBodyEl.getBoundingClientRect();

		var wrapperBottomDiff = 0;
		if (tabsWrapperEl) {
			var wrapperRect = tabsWrapperEl.getBoundingClientRect();
			wrapperBottomDiff = Math.max(0, wrapperRect.bottom - scrollRect.bottom);
		}

		var bodyPadBottom = parseFloat($('body').css('padding-bottom')) || 0;
		var bodyMarginBottom = parseFloat($('body').css('margin-bottom')) || 0;
		var totalBottomSpace = wrapperBottomDiff + bodyPadBottom + bodyMarginBottom + 6;

		var viewportHeight = document.documentElement.clientHeight;
		var availableHeight = Math.floor(viewportHeight - scrollRect.top - totalBottomSpace);

		if (availableHeight > 60) {
			var heightPx = availableHeight + 'px';

			var dtSettings = dtInstance.settings().get(0);
			if (dtSettings) {
				if (dtSettings.oInit) dtSettings.oInit.scrollY = heightPx;
				if (dtSettings.oScroll) dtSettings.oScroll.sY = heightPx;
			}

			dtInstance.columns.adjust();

			$scrollBody.css({
				'max-height': heightPx,
				'height': ''
			});
		}
	}

	// Global listeners bound once for all registered tab tables
	$(window).on('resize', function() {
		registeredTables.forEach(function(item) {
			resizeSingleTable(item.tabSelector, item.dtInstance);
		});
	});

	$(document).on('tabsactivate', function(event, ui) {
		registeredTables.forEach(function(item) {
			if (ui.newPanel.is(item.tabSelector)) {
				resizeSingleTable(item.tabSelector, item.dtInstance);
			}
		});
	});

	// Public API exposed to your tab scripts
	return {
		register: function(tabSelector, dtInstance) {
			// Avoid duplicate registrations if a panel reloads
			registeredTables = registeredTables.filter(function(item) {
				return item.tabSelector !== tabSelector;
			});

			registeredTables.push({
				tabSelector: tabSelector,
				dtInstance: dtInstance
			});

			resizeSingleTable(tabSelector, dtInstance);
		},
		resize: function(tabSelector, dtInstance) {
			resizeSingleTable(tabSelector, dtInstance);
		}
	};
})();
