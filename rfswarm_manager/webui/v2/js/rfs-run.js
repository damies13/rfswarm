$(document).ready(function() {

	// Exit immediately if #tbl-run was already initialized on an earlier i18next 'loaded' event
	if (DataTable.isDataTable('#tbl-run')) {
		return;
	}

	var showcols = {
		index: false,
		iter: false,
		seqce: false
	};

	// 1. Initialize DataTables
	var runtable = $('#tbl-run').DataTable({
		jQueryUI: true,
		scrollY: "80vh",      // Initial placeholder; resized dynamically by AppDataTables
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

	// Register this tab and table with the shared resize utility
	AppDataTables.register('#tab-run', runtable);

	var rundata = [];
	var pollTimer = null;
	var nextRowId = 1;

	// 2. Direct check using #tab-run's display state and browser visibility
	function isTabActive() {
		var isTabOpen = $('#tab-run').is(':visible');
		return isTabOpen && !document.hidden;
	}

	// 3. Full dataset replacement helper (useful when backend returns full table snapshots)
	function updateTableData(DataArray) {
		var $scrollBody = $('#tab-run .dt-scroll-body');
		var currentScrollTop = $scrollBody.scrollTop();

		runtable.column(0).visible(showcols.index, false);
		runtable.column(1).visible(showcols.iter, false);
		runtable.column(2).visible(showcols.seqce, false);

		runtable.clear();
		runtable.rows.add(DataArray);
		runtable.draw(false);

		AppDataTables.resize('#tab-run', runtable);
		$scrollBody.scrollTop(currentScrollTop);
	}

	// 4. Adaptive polling loop (1s active / 10s inactive)
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

	// 5. Event listeners for tab switches and browser visibility (window resize is now handled by AppDataTables)
	$(document).on('tabsactivate', function(event, ui) {
		if (ui.newPanel.is('#tab-run')) {
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

	// Initialize empty state and start polling
	updateTableData(rundata);
	pollBackendForUpdates();

});
