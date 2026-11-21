$(document).ready(function() {

	// Exit immediately if #tbl-agents was already initialized on an earlier i18next 'loaded' event
	if (DataTable.isDataTable('#tbl-agents')) {
		return;
	}

	// 1. Initialize DataTables
	var agentstable = $('#tbl-agents').DataTable({
		jQueryUI: true,
		scrollY: "80vh",      // Initial placeholder; resized dynamically by AppDataTables
		scrollCollapse: true,
		paging: false,
		searching: false,
		info: false,
		columns: [
			{
				data: 'status',
				defaultContent: '',
				render: function(data, type, row) {
					if (!data) return '';
					// Only translate for visual display; keep raw status code for sorting/filtering
					if (type === 'display') {
						// Example key path: "agent.status.online" -> falls back to raw 'data' if missing
						return i18next.t('tabs.agents.statuses.' + data.toLowerCase(), { defaultValue: data });
					}
					return data;
				}
			},
			{ data: 'agent',				defaultContent: '' },
			{ data: 'lastseen',				defaultContent: '' },
			{ data: 'robotsassigned',		defaultContent: '' },
			{ data: 'robots',				defaultContent: '' },
			{ data: 'monitorassigned',		defaultContent: '' },
			{ data: 'monitor',				defaultContent: '' },
			{ data: 'load',					defaultContent: '' },
			{ data: 'percentilecpu',		defaultContent: '' },
			{ data: 'percentilememory',		defaultContent: '' },
			{ data: 'percentilenetwork',	defaultContent: '' },
			{ data: 'version',				defaultContent: '', className: 'dt-center' },
			{ data: 'libraries',			defaultContent: '' }
		]
	});

	// Register this tab and table with the shared resize utility
	AppDataTables.register('#tab-agents', agentstable);

	var agentsdata = [];
	var pollTimer = null;
	var nextRowId = 1;

	// 2. Direct check using #tab-agents's display state and browser visibility
	function isTabActive() {
		var isTabOpen = $('#tab-agents').is(':visible');
		return isTabOpen && !document.hidden;
	}

	// 3. Full dataset replacement helper (useful when backend returns full table snapshots)
	function updateTableData(DataArray) {
		var $scrollBody = $('#tab-agents .dt-scroll-body');
		var currentScrollTop = $scrollBody.scrollTop();

		agentstable.clear();
		agentstable.rows.add(DataArray);
		agentstable.draw(false);

		AppDataTables.resize('#tab-agents', agentstable);
		$scrollBody.scrollTop(currentScrollTop);
	}

	// 4. Adaptive polling loop (1s active / 10s inactive)
	function scheduleNextPoll() {
		clearTimeout(pollTimer);
		pollTimer = setTimeout(pollBackendForUpdates, isTabActive() ? 5000 : 20000);
	}

	function pollBackendForUpdates() {
		// --- TEMPORARY MOCK DATA (Matched to your real column keys) ---
		var lastsee = new Date().toLocaleString('sv-SE');

		var newRow = {
			status: "ready",
			agent: "Agent " + nextRowId,
			lastseen: lastsee,
			robotsassigned: 15,
			robots: 13,
			monitorassigned: 5,
			monitor: 3,
			load: (Math.random() * 100).toFixed(1),
			percentilecpu: (Math.random() * 100).toFixed(1),
			percentilememory: (Math.random() * 100).toFixed(1),
			percentilenetwork: (Math.random() * 100).toFixed(1),
			version: "2.0.0",
			libraries: "imagehorizonlibrary, assertion, pythonlibcore, requests, database, httpctrl, ocrlibrary"
		};
		nextRowId++;

		agentsdata.push(newRow);
		updateTableData(agentsdata);
		scheduleNextPoll();
	}

	// 5. Event listeners for tab switches and browser visibility (window resize is now handled by AppDataTables)
	$(document).on('tabsactivate', function(event, ui) {
		if (ui.newPanel.is('#tab-agents')) {
			pollBackendForUpdates(); // Instant update when opening #tab-agents
		} else {
			scheduleNextPoll();      // Drops immediately to 10s when leaving #tab-agents
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
	updateTableData(agentsdata);
	pollBackendForUpdates();

});
