$(document).ready(function() {

	var showcols = {
		index: false,
		iter: false,
		seqce: false
	};

	// 1. Initialize DataTables
	var runtable = $('#runTable').DataTable({
		jQueryUI: true,
		// scrollY: "500px",      // Initial placeholder; resized dynamically by resizeTableInTab()
		scrollY: "80vh",      // Initial placeholder; resized dynamically by resizeTableInTab()
		scrollCollapse: true,
		paging: false,
		searching: false,
		info: false,
		columns: [
			{ data: 'index',      defaultContent: '', visible: showcols.index },
			{ data: 'iter',       defaultContent: '', visible: showcols.iter },
			{ data: 'seqce',      defaultContent: '', visible: showcols.seqce },
			{ data: 'resname',    defaultContent: '' },
			{ data: 'min',        defaultContent: '' },
			{ data: 'avg',        defaultContent: '' },
			{ data: 'percentile', defaultContent: '' },
			{ data: 'max',        defaultContent: '' },
			{ data: 'stddev',     defaultContent: '' },
			{ data: 'pass',       defaultContent: '' },
			{ data: 'fail',       defaultContent: '' },
			{ data: 'other',      defaultContent: '' }
		]
	});

	var rundata = [];
	var pollTimer = null;
	var nextRowId = 1;

	// 2. Direct check using #tab-run's display state and browser visibility
	function isTabActive() {
		var isTabOpen = $('#tab-run').is(':visible');
		return isTabOpen && !document.hidden;
	}

	// 3. Clean height calculation targeting #tab-run directly
	function resizeTableInTab() {
		if (!isTabActive()) return;

		var $tab = $('#tab-run');
		var $scrollBody = $tab.find('.dt-scroll-body');
		var scrollBodyEl = $scrollBody.get(0);
		if (!scrollBodyEl) return;

		var bodyTop = scrollBodyEl.getBoundingClientRect().top;

		// Measure #tab-run bottom padding/border
		var tabPadBottom = parseFloat($tab.css('padding-bottom')) || 0;
		var tabBorderBottom = parseFloat($tab.css('border-bottom-width')) || 0;

		// Measure the outer .ui-tabs wrapper and body bottom spacing
		var $tabsWrapper = $tab.closest('.ui-tabs');
		var wrapperPadBottom = $tabsWrapper.length ? (parseFloat($tabsWrapper.css('padding-bottom')) || 0) : 0;
		var wrapperBorderBottom = $tabsWrapper.length ? (parseFloat($tabsWrapper.css('border-bottom-width')) || 0) : 0;
		var bodyMarginBottom = parseFloat($('body').css('margin-bottom')) || 0;
		var bodyPadBottom = parseFloat($('body').css('padding-bottom')) || 0;

		var totalBottomSpace = tabPadBottom + tabBorderBottom + wrapperPadBottom + wrapperBorderBottom + bodyMarginBottom + bodyPadBottom + 8;
		var availableHeight = Math.floor(window.innerHeight - bodyTop - totalBottomSpace);

		if (availableHeight > 60) {
			var heightPx = availableHeight + 'px';

			var dtSettings = runtable.settings().get(0);
			if (dtSettings) {
				if (dtSettings.oInit) dtSettings.oInit.scrollY = heightPx;
				if (dtSettings.oScroll) dtSettings.oScroll.sY = heightPx;
			}

			runtable.columns.adjust();

			$scrollBody.css({
				'max-height': heightPx,
				'height': ''
			});
		}
	}




	// 4. Full dataset replacement helper (useful when backend returns full table snapshots)
	function updateTableData(DataArray) {
		var $scrollBody = $('#tab-run .dt-scroll-body');
		var currentScrollTop = $scrollBody.scrollTop();

		runtable.column(0).visible(showcols.index, false);
		runtable.column(1).visible(showcols.iter, false);
		runtable.column(2).visible(showcols.seqce, false);

		runtable.clear();
		runtable.rows.add(DataArray);
		runtable.draw(false);

		resizeTableInTab();
		$scrollBody.scrollTop(currentScrollTop);
	}

	// 5. Adaptive polling loop (1s active / 10s inactive)
	function scheduleNextPoll() {
		clearTimeout(pollTimer);
		pollTimer = setTimeout(pollBackendForUpdates, isTabActive() ? 1000 : 10000);
	}

	function pollBackendForUpdates() {
		// --- TEMPORARY MOCK DATA (Matched to your real column keys) ---
		var newRow = {
			index: nextRowId,
			iter: 1,
			seqce: nextRowId * 10,
			resname: "Endpoint_" + nextRowId + " (" + (isTabActive() ? "1s" : "10s") + ")",
			min: (Math.random() * 10 + 5).toFixed(1),
			avg: (Math.random() * 20 + 15).toFixed(1),
			percentile: (Math.random() * 30 + 25).toFixed(1),
			max: (Math.random() * 50 + 40).toFixed(1),
			stddev: (Math.random() * 5).toFixed(2),
			pass: Math.floor(Math.random() * 100),
			fail: Math.floor(Math.random() * 5),
			other: 0
		};
		nextRowId++;

		rundata.push(newRow);
		updateTableData(rundata);
		scheduleNextPoll();
	}

	// 6. Event listeners for tab switches, browser visibility, and window resizing
	$(document).on('tabsactivate', function(event, ui) {
		if (ui.newPanel.is('#tab-run')) {
			resizeTableInTab();
			pollBackendForUpdates(); // Instant update when opening #tab-run
		} else {
			scheduleNextPoll();      // Drops immediately to 10s when leaving #tab-run
		}
	});

	document.addEventListener('visibilitychange', function() {
		if (isTabActive()) {
			pollBackendForUpdates();
		} else {
			scheduleNextPoll();
		}
	});

	$(window).on('resize', resizeTableInTab);

	// Initialize empty state and start polling
	updateTableData(rundata);
	pollBackendForUpdates();

});
