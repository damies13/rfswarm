*** Settings ***
Test Tags       Features 	CommandLine

Resource 	CommandLine_Common.robot

Suite Setup 	Set Platform

*** Test Cases ***
Environment Variable Substitution in Robot/Resource files
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #165
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	@{agnt_options}= 	Create List 	-g 	1 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}

	@{expected_files}= 	List Files In Directory And Sub Directories 	${CURDIR}${/}testdata${/}Issue-#165
	Remove Values From List 	${expected_files} 	Issue-#165.rfs

	Set Environment Variable 		RF_DIRECTORY 			${CURDIR}${/}testdata${/}Issue-#165${/}rf_dir
	Set Environment Variable 		RF_MAGICNUM 			Thirteen

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#165${/}Issue-#165.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	# Should Contain 	${stdout_agent} 		Thirteen

	Should Not Contain 	${stdout_agent} 		Robot returned an error
	Should Not Contain 	${stderr_agent} 		Robot returned an error
	Should Not Contain 	${stdout_agent} 		please check the log file
	Should Not Contain 	${stderr_agent} 		please check the log file

	@{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts
	Remove Values From List 	${result_files} 	RFSListener2.py 	RFSListener3.py 	RFSTestRepeater.py

	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager


	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Default Result Name Method
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}default.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*default
	Log 	lst_results_dir: ${lst_results_dir} 	console=true
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	4 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Default Keyword Documentation
	Should Be Equal 	${result[1][0]} 	Doc Keyword Message
	Should Be Equal 	${result[2][0]} 	Doc only keyword From Info Library
	Should Be Equal 	${result[3][0]} 	Message for Info Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Documentation Result Name Method - Tests Defaults
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}documentation_td.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*documentation_td
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	3 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Default Keyword Documentation
	Should Be Equal 	${result[1][0]} 	Doc keyword From Info Library
	Should Be Equal 	${result[2][0]} 	Doc only keyword From Info Library

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Info Result Name Method - Tests Defaults
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}info_td.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*info_td
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	2 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Doc Keyword Message
	Should Be Equal 	${result[1][0]} 	Message for Info Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Keyword Only Result Name Method - Tests Defaults
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}keyword_td.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*keyword_td
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	7 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Argument Keyword
	Should Be Equal 	${result[1][0]} 	Default Keyword Name
	Should Be Equal 	${result[2][0]} 	Doc Keyword
	Should Be Equal 	${result[3][0]} 	Doc Only Keyword
	Should Be Equal 	${result[4][0]} 	Info Keyword
	Should Be Equal 	${result[5][0]} 	Quiet Keyword Name
	Should Be Equal 	${result[6][0]} 	Return Only Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Keyword and Args Result Name Method - Tests Defaults
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}keywordargs_td.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*keywordargs_td
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	7 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Argument Keyword Arg1
	Should Be Equal 	${result[1][0]} 	Default Keyword Name
	Should Be Equal 	${result[2][0]} 	Doc Keyword Doc Keyword Message
	Should Be Equal 	${result[3][0]} 	Doc Only Keyword Doc Keyword Message
	Should Be Equal 	${result[4][0]} 	Info Keyword Message for Info Keyword
	Should Be Equal 	${result[5][0]} 	Quiet Keyword Name
	Should Be Equal 	${result[6][0]} 	Return Only Keyword Hello

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Default Result Name Method - Tests Row
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}default_tr.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*default_tr
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	4 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Default Keyword Documentation
	Should Be Equal 	${result[1][0]} 	Doc Keyword Message
	Should Be Equal 	${result[2][0]} 	Doc only keyword From Info Library
	Should Be Equal 	${result[3][0]} 	Message for Info Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Documentation Result Name Method - Tests Row
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}documentation_tr.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*documentation_tr
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	3 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Default Keyword Documentation
	Should Be Equal 	${result[1][0]} 	Doc keyword From Info Library
	Should Be Equal 	${result[2][0]} 	Doc only keyword From Info Library

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Info Result Name Method - Tests Row
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}info_tr.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*info_tr
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	2 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Doc Keyword Message
	Should Be Equal 	${result[1][0]} 	Message for Info Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Keyword Only Result Name Method - Tests Row
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}keyword_tr.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*keyword_tr
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	7 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Argument Keyword
	Should Be Equal 	${result[1][0]} 	Default Keyword Name
	Should Be Equal 	${result[2][0]} 	Doc Keyword
	Should Be Equal 	${result[3][0]} 	Doc Only Keyword
	Should Be Equal 	${result[4][0]} 	Info Keyword
	Should Be Equal 	${result[5][0]} 	Quiet Keyword Name
	Should Be Equal 	${result[6][0]} 	Return Only Keyword

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Keyword and Args Result Name Method - Tests Row
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #154 	Issue #56
	Run Agent
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}keywordargs_tr.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	List Directory 	${results_dir}
	@{lst_results_dir}= 	List Directories In Directory 	${results_dir} 	*keywordargs_tr
	Copy Directory 	${results_dir}${/}${lst_results_dir}[0] 	${OUTPUT DIR}${/}${TEST NAME}${/}Results
	Copy Directory 	${agent_dir} 	${OUTPUT DIR}${/}${TEST NAME}${/}rfswarm-agent

	@{lst_summary}= 	List Files In Directory 	${results_dir}${/}${lst_results_dir}[0] 	*summary.csv 	absolute=true
	Log 	lst_summary: ${lst_summary} 	console=true
	Length Should Be 	${lst_summary} 	1
	${result}= 	CSV to List 	${lst_summary}[0]

	Sort List 	${result}
	Log 	Found result names from keywords in CSV summary file after scenario run: ${\n}${result} 	console=${True}
	Length Should Be 	${result} 	7 	msg=Unique Result Names number from keywords is incorrect. Check the Logs.
	Should Be Equal 	${result[0][0]} 	Argument Keyword Arg1
	Should Be Equal 	${result[1][0]} 	Default Keyword Name
	Should Be Equal 	${result[2][0]} 	Doc Keyword Doc Keyword Message
	Should Be Equal 	${result[3][0]} 	Doc Only Keyword Doc Keyword Message
	Should Be Equal 	${result[4][0]} 	Info Keyword Message for Info Keyword
	Should Be Equal 	${result[5][0]} 	Quiet Keyword Name
	Should Be Equal 	${result[6][0]} 	Return Only Keyword Hello

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	@{mngr_options}= 	Create List 	-g 	6 	-c 	ICON
	Run Manager CLI 	${mngr_options}
	Sleep    2
	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Check Icon Install

Run Mnager with JSON Configuration and JSON Scenario
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #172

	# By telling the agent to connect on the port we specified in the JSON configuration file (RFSwarmManager.json)
	# we can infer that the manager read the configuration correctly if the agent connects sucessfully
	VAR 	${managerurl} 		http://localhost:8152
	@{agnt_options}= 	Create List 	-g 	1 	-m 	${managerurl}
	Run Agent 	${agnt_options}

	${configfile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}RFSwarmManager.json
	Log 	configfile: ${configfile} 		console=true
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}NewStyle_small_json.json
	Log 	scenariofile: ${scenariofile} 		console=true
	@{mngr_options}= 	Create List 	-g 	1 	-i 	${configfile} 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	Stop Agent

	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	# can't get stdout in windows
	# IF 	"${platform}" != "windows"
	# Check the manager thinks it's listening on the port from the configuration file
	# for some reason the manager stdout is blank, but we can confirm what we need from the agent
	# Should Contain 		${stdout_manager} 		Starting Agent Manager ${managerurl}

	# Check the agent connected to the manager on the port from the configuration file
	Should Contain 		${stdout_agent} 		Manager Connected ${managerurl}
	# Check the agent got the script files specifed in the scenaio, infers the manager read the scenario file
	Should Contain 		${stdout_agent} 		AppTests-json.robot
	Should Contain 		${stdout_agent} 		monitoring-json.robot
	# sometimes the agent doesn't get to disconnected state, could make this pass by making test slower but not needed
	# Should Contain 		${stdout_agent} 		Manager Disconnected ${managerurl}
	# END

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager


Run Mnager with Yaml Configuration and Yaml Scenario
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #172

	# By telling the agent to connect on the port we specified in the Yaml configuration file (RFSwarmManager.yaml)
	# we can infer that the manager read the configuration correctly if the agent connects sucessfully
	VAR 	${managerurl} 		http://localhost:8141
	@{agnt_options}= 	Create List 	-g 	1 	-m 	${managerurl}
	Run Agent 	${agnt_options}

	${configfile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}RFSwarmManager.yaml
	Log 	configfile: ${configfile} 		console=true
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}NewStyle_small_yaml.yaml
	Log 	scenariofile: ${scenariofile} 		console=true
	@{mngr_options}= 	Create List 	-g 	1 	-i 	${configfile} 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	Stop Agent

	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	# can't get stdout in windows
	# IF 	"${platform}" != "windows"
	# Check the manager thinks it's listening on the port from the configuration file
	# for some reason the manager stdout is blank, but we can confirm what we need from the agent
	# Should Contain 		${stdout_manager} 		Starting Agent Manager ${managerurl}

	# Check the agent connected to the manager on the port from the configuration file
	Should Contain 		${stdout_agent} 		Manager Connected ${managerurl}
	# Check the agent got the script files specifed in the scenaio, infers the manager read the scenario file
	Should Contain 		${stdout_agent} 		AppTests-yaml.robot
	Should Contain 		${stdout_agent} 		monitoring-yaml.robot
	# sometimes the agent doesn't get to disconnected state, could make this pass by making test slower but not needed
	# Should Contain 		${stdout_agent} 		Manager Disconnected ${managerurl}
	# END

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Run Mnager with yml Configuration and yml Scenario
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #172

	# By telling the agent to connect on the port we specified in the yml configuration file (RFSwarmManager.yml)
	# we can infer that the manager read the configuration correctly if the agent connects sucessfully
	VAR 	${managerurl} 		http://localhost:8171
	@{agnt_options}= 	Create List 	-g 	1 	-m 	${managerurl}
	Run Agent 	${agnt_options}

	${configfile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}RFSwarmManager.yml
	Log 	configfile: ${configfile} 		console=true
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#172${/}NewStyle_small_yml.yml
	Log 	scenariofile: ${scenariofile} 		console=true
	@{mngr_options}= 	Create List 	-g 	1 	-i 	${configfile} 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager

	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	Stop Agent

	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	# can't get stdout in windows
	# IF 	"${platform}" != "windows"
	# Check the manager thinks it's listening on the port from the configuration file
	# for some reason the manager stdout is blank, but we can confirm what we need from the agent
	# Should Contain 		${stdout_manager} 		Starting Agent Manager ${managerurl}

	# Check the agent connected to the manager on the port from the configuration file
	Should Contain 		${stdout_agent} 		Manager Connected ${managerurl}
	# Check the agent got the script files specifed in the scenaio, infers the manager read the scenario file
	Should Contain 		${stdout_agent} 		AppTests-yml.robot
	Should Contain 		${stdout_agent} 		monitoring-yml.robot
	# sometimes the agent doesn't get to disconnected state, could make this pass by making test slower but not needed
	# Should Contain 		${stdout_agent} 		Manager Disconnected ${managerurl}
	# END

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager
