*** Settings ***
Library 	Collections
Library 	String
Resource 	GUI_Common.robot
Resource 	${CURDIR}${/}..${/}Agent${/}CommandLine_Common.robot
Suite Setup 	Set Platform

*** Variables ***
@{robot_data}=	example.robot	Example Test Case
${scenario_name}=	test_scenario

*** Test Cases ***
Test
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	Open Manager GUI
	@{ip_addresses}=	Get IP addresses
	Log To Console	${\n}${ip_addresses}
	FOR  ${ip}  IN  @{ip_addresses}
		@{splitted_ip}=		Split String To Characters	${ip}
		IF  ':' in @{splitted_ip}
			@{agent_options}	Set Variable	-m	http://[${ip}]:8138/
		ELSE
			@{agent_options}	Set Variable	-m	http://${ip}:8138/
		END
		Open Agent	${agent_options}
		${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
		Log To Console	For ${ip}: ${status}
		GUI_Common.Stop Agent
		IF  ${status} is ${True}
			Run Keyword		Close Manager GUI ${platform}
			Open Manager GUI
		END
		Click Tab	Plan
	END
	Run Keyword		Close Manager GUI ${platform}

Verify If the Port Number And Ip Address Get Written To the INI File
	#[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${ipv4}		${ipv6}=		Get IP addresses
	Log To Console		${\n}IPV4 address: ${ipv4} ${\n}IPV6 address: ${ipv6}${\n}
	${manager_ini_file}		Get Manager INI Location
	&{run_settings_data}	Create Dictionary
	...    bind_ip_address=${ipv4}
	...    bind_port_number=8148

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Sleep	2
	Press key.enter 1 Times
	Run Keyword		Close Manager GUI ${platform}
	Sleep	2
	${manager_ini_file_dict}=	Read Ini File	${manager_ini_file}
	Log		manager ini file dict: ${manager_ini_file_dict}		console=True

	Should Be Equal As Strings 	${manager_ini_file_dict}[Server][bindip] 	${run_settings_data}[bind_ip_address]
	Should Be Equal As Strings 	${manager_ini_file_dict}[Server][bindport] 	${run_settings_data}[bind_port_number]

	Log To Console	${\n}The bindip and bindport heve been saved to the ini file, now check if it will be applied to the manager after restarting.${\n}
	Open Manager GUI
	Click Button	runsettings
	Click Button	ok
	Sleep	2
	Press key.enter 1 Times
	Run Keyword		Close Manager GUI ${platform}

	Should Be Equal As Strings 	${manager_ini_file_dict}[Server][bindip] 	${run_settings_data}[bind_ip_address]
	Should Be Equal As Strings 	${manager_ini_file_dict}[Server][bindport] 	${run_settings_data}[bind_port_number]

	# @{agent_options}	Set Variable	-m	http://${run_settings_data}[bind_ip_address]:${run_settings_data}[bind_port_number]/

	[Teardown]	Run Keywords
	...    Change = ${ipv4} With = In ${manager_ini_file}	AND
	...    Change = 8148 With = 8138 In ${manager_ini_file}

Verify If Agent Can't Connect On Old Port Number After Port Number Changed And Can Connect To the New One
	#[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${old_port_number}=		Set Variable	8138
	&{run_settings_data}	Create Dictionary	bind_port_number=8148
	${manager_ini_file}		Get Manager INI Location

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Sleep	2
	Press key.enter 1 Times
	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI

	Log To Console	Check if Agent cant connect to the old port number.
	@{agent_options}	Set Variable	-m	http://localhost:${old_port_number}/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	${status}	Fail
	...    msg=The agent has connected to the old port number. Old port number: ${old_port_number}, new: ${run_settings_data}[bind_port_number].
	Click Tab	Plan
	GUI_Common.Stop Agent

	Log To Console	Check if Agent can connect to the new port number.
	@{agent_options}	Set Variable	-m	http://localhost:${run_settings_data}[bind_port_number]/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	not ${status}	Fail
	...    msg=The agent did not connect to the new port number. Old port number: ${old_port_number}, new: ${run_settings_data}[bind_port_number].
	Click Tab	Plan
	
	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    GUI_Common.Stop Agent							AND
	...    Change = 8148 With = 8138 In ${manager_ini_file}

Verify If Agent Can Only Connect Via the Specified Ip Address And Not Any Ip Address On the Manager's Host
	#[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${ipv4}		${ipv6}=		Get IP addresses
	Log To Console		${\n}IPV4 address: ${ipv4} ${\n}IPV6 address: ${ipv6}${\n}
	# ${manager_ini_file}		Get Manager INI Location
	# &{run_settings_data}	Create Dictionary	bind_ip_address=${ipv4}

	# Click Button	runsettings
	# Change Scenario Wide Settings	${run_settings_data}
	# Sleep	2
	# Press key.enter 1 Times
	# Run Keyword		Close Manager GUI ${platform}
	# Open Manager GUI

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    GUI_Common.Stop Agent							AND
	...    Remove File		${manager_ini_file}

Verify That Files Get Saved With Correct Extension And Names
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #39
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI													AND
	...    Open Agent

	${scenario_name}=	Set Variable	Issue-#39
	Log To Console	Files to check: scenario file, csv result files
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	# !!! csv files are checked in Test Case for Issue #254 !!!
	@{all_files}=	List Files In Directory		${global_path}
	Log To Console	${\n}All manager files: ${all_files}${\n}
	@{scenario_file}=		List Files In Directory		${global_path}		${scenario_name}*
	Length Should Be	${scenario_file}	1	msg=Cant find scenario file. File did not save or saved incorrectly. Check all manager files.
	Should Be Equal As Strings		${scenario_file}[0]		${scenario_name}.rfs
	...    msg=Scenario file name is incorrect: expected "${scenario_name}.rfs", actual: "${scenario_file}[0]"

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}		AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    GUI_Common.Stop Agent

Check If the Manager Saves Times and Robots to the Scenario with Example Robot
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600										AND
	...    Open Manager GUI															AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]			AND
	...    Create Robot File

	@{run_robots}	Create List
	@{run_times_in_s}	Create List		#delay,		rump-up,	time
	Click Button	runaddrow
	Click
	FOR  ${i}  IN RANGE  1  4
		Sleep	2
		FOR  ${j}  IN RANGE  1  5
			Press Key.tab 1 Times
			IF  '${j}' == '1'
				Append To List	${run_robots}	${i}${j}${i}
				Take A Screenshot
				Type	${i}${j}${i}
			ELSE
				${time_in_s}=	Evaluate	str(${i}${j} * 60 + ${i}${j})
				Type	${time_in_s}
				Append To List	${run_times_in_s}	${time_in_s}

			END

		END
		Press Key.tab 2 Times
		Click Button	selected_runscriptrow
		Select Robot File OS DIALOG		${robot_data}[0]
		Click Button	selected_select_test_case
		Click Button	select_example
		Press Key.tab 3 Times
	END
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Log		${scenario_name}.rfs
	Log		${scenario_content}
	Log		${run_robots}
	Log		${run_times_in_s}

	Verify Scenario File Robots		${scenario_content_list}	${run_robots}		${1}	${3}
	Verify Scenario File Times		${scenario_content_list}	${run_times_in_s}	${1}	${3}
	Verify Scenario File Robot Data	${scenario_content_list}	${robot_data}		${1}	${3}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If the Manager Saves Settings on the Test Row With Example Robot
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600										AND
	...    Open Manager GUI															AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]			AND
	...    Create Robot File

	@{settings_locations}	Create List
	&{row_settings_data}	Create Dictionary
	...    exclude_libraries=builtin,string,operatingsystem,perftest,collections
	...    robot_options=-v var:examplevariable
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=30
	...    inject_sleep_max=60
	Click Button	runaddrow
	Click
	FOR  ${i}  IN RANGE  1  4
		Sleep	2
		Press Key.tab 6 Times
		Click Button	selected_runscriptrow
		Select Robot File OS DIALOG		${robot_data}[0]
		Click Button	selected_select_test_case
		Click Button	select_example
		Press Key.tab 2 Times
		${settings_coordinates}=
		...    Locate	manager_${platform}_button_selected_runsettingsrow.png
		Append To List	${settings_locations}	${settings_coordinates}
		Press Key.tab 1 Times
	END
	FOR  ${i}  IN RANGE  0  3
		Click To The Above Of	${settings_locations}[${i}]	0
		Change Test Group Settings	${row_settings_data}
	END
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Log		${scenario_name}.rfs
	Log		${scenario_content}
	Log		${row_settings_data}

	Verify Scenario File Robot Data		${scenario_content_list}	${robot_data}			${1}	${3}
	Verify Scenario Test Row Settings	${scenario_content_list}	${row_settings_data}	${1}	${3}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If the Manager Opens Scenario File Correctly With Data From the Test Rows
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	1						AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI		${mngr_options}								AND
	...    Create Robot File

	@{settings_locations}	Create List
	&{row_settings_data}	Create Dictionary
	...    exclude_libraries=builtin,string,operatingsystem,perftest,collections
	...    robot_options=-v var:examplevariable
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=30
	...    inject_sleep_max=60
	Click Button	runaddrow
	Click
	FOR  ${i}  IN RANGE  1  4
		Sleep	2
		FOR  ${j}  IN RANGE  1  5
			Press Key.tab 1 Times
			IF  '${j}' == '1'
				Take A Screenshot
				Type	${i}${j}${i}
			ELSE
				${time_in_s}=	Evaluate	str(${i}${j} * 60 + ${i}${j})
				Type	${time_in_s}

			END

		END
		Press Key.tab 2 Times
		Click Button	selected_runscriptrow
		Select Robot File OS DIALOG		${robot_data}[0]
		Click Button	selected_select_test_case
		Click Button	select_example
		Press Key.tab 2 Times
		${settings_coordinates}=
		...    Locate	manager_${platform}_button_selected_runsettingsrow.png
		Append To List	${settings_locations}	${settings_coordinates}
		Press Key.tab 1 Times
	END
	FOR  ${i}  IN RANGE  0  3
		Click To The Above Of	${settings_locations}[${i}]	0
		Change Test Group Settings	${row_settings_data}
	END
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}

	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI	${mngr_options}
	Check That The Scenario File Opens Correctly	${scenario_name}	${scenario_content}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Verify Scenario File Is Updated Correctly When Scripts Are Removed
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #58
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI													AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Create Robot File	name=example1.robot	file_content=***Test Case***\nExample Test Case1\n	AND
	...    Create Robot File	name=example2.robot	file_content=***Test Case***\nExample Test Case2\n	AND
	...    Create Robot File	name=example3.robot	file_content=***Test Case***\nExample Test Case3\n	AND
	...    Create Robot File	name=example4.robot	file_content=***Test Case***\nExample Test Case4\n	AND
	...    Create Robot File	name=example5.robot	file_content=***Test Case***\nExample Test Case5\n

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#58${/}test_scenario.rfs
	Copy File	${scenariofile}		${global_path}

	@{expected_robot_data3}	Create List		example3.robot	Example Test Case3
	@{expected_run_robots3}	Create List		18
	@{expected_run_times3}	Create List		19	20	21
	&{expected_row_settings_data3}	Create Dictionary
	...    exclude_libraries=row3el
	...    robot_options=row3ro
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=30
	...    inject_sleep_max=60
	...    disablelog_log=True
	...    disablelog_report=True
	...    disablelog_output=True

	@{expected_robot_data5}	Create List		example5.robot	Example Test Case5
	@{expected_run_robots5}	Create List		${None}	26
	@{expected_run_times5}	Create List		${None}	${None}	${None}	27	28	29
	&{expected_row_settings_data5}	Create Dictionary
	...    exclude_libraries=row5el
	...    robot_options=row5ro
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=30
	...    inject_sleep_max=60
	...    disablelog_log=True
	...    disablelog_report=True
	...    disablelog_output=True

	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Click Button	rundelrow
	Click Button	rundelrow
	Click Label With Vertical Offset	button_rundelrow	35
	Click Button	runsave

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario File Robot Data		${scenario_content_list}	${expected_robot_data3}			${1}	${1}
	Verify Scenario File Robots			${scenario_content_list}	${expected_run_robots3}			${1}	${1}
	Verify Scenario File Times			${scenario_content_list}	${expected_run_times3}			${1}	${1}
	Verify Scenario Test Row Settings	${scenario_content_list}	${expected_row_settings_data3}	${1}	${1}

	Verify Scenario File Robot Data		${scenario_content_list}	${expected_robot_data5}			${2}	${2}
	Verify Scenario File Robots			${scenario_content_list}	${expected_run_robots5}			${2}	${2}
	Verify Scenario File Times			${scenario_content_list}	${expected_run_times5}			${2}	${2}
	Verify Scenario Test Row Settings	${scenario_content_list}	${expected_row_settings_data5}	${2}	${2}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Robot File	name=example1.robot			AND
	...    Delete Robot File	name=example2.robot			AND
	...    Delete Robot File	name=example3.robot			AND
	...    Delete Robot File	name=example4.robot			AND
	...    Delete Robot File	name=example5.robot			AND
	...    Delete Scenario File		${scenario_name}

Verify the Manager Handles Corrupted Scenario Files And Repairs It
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #58
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI													AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Create Robot File	name=example4.robot	file_content=***Test Case***\nExample Test Case4\n	AND
	...    Create Robot File	name=example7.robot	file_content=***Test Case***\nExample Test Case7\n

	${scenario_name}=	Set Variable	test_scenario_corrupted
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#58${/}test_scenario_corrupted.rfs
	Copy File	${scenariofile}		${global_path}

	@{expected_robot_data4}	Create List		example4.robot	Example Test Case4
	@{expected_run_robots4}	Create List		22
	@{expected_run_times4}	Create List		23	24	25
	&{expected_row_settings_data4}	Create Dictionary
	...    exclude_libraries=row4el
	...    robot_options=row4ro
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=70
	...    inject_sleep_max=75
	...    disablelog_log=True
	...    disablelog_report=True
	...    disablelog_output=True

	@{expected_robot_data7}	Create List		example7.robot	Example Test Case7
	@{expected_run_robots7}	Create List		${None}	71
	@{expected_run_times7}	Create List		${None}	${None}	${None}	72	73	74
	&{expected_row_settings_data7}	Create Dictionary
	...    exclude_libraries=row7el
	...    robot_options=row7ro
	...    test_repeater=True
	...    inject_sleep=True
	...    inject_sleep_min=30
	...    inject_sleep_max=60
	...    disablelog_log=True
	...    disablelog_report=True
	...    disablelog_output=True

	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Click Button	runsave

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario File Robot Data		${scenario_content_list}	${expected_robot_data4}			${1}	${1}
	Verify Scenario File Robots			${scenario_content_list}	${expected_run_robots4}			${1}	${1}
	Verify Scenario File Times			${scenario_content_list}	${expected_run_times4}			${1}	${1}
	Verify Scenario Test Row Settings	${scenario_content_list}	${expected_row_settings_data4}	${1}	${1}

	Verify Scenario File Robot Data		${scenario_content_list}	${expected_robot_data7}			${2}	${2}
	Verify Scenario File Robots			${scenario_content_list}	${expected_run_robots7}			${2}	${2}
	Verify Scenario File Times			${scenario_content_list}	${expected_run_times7}			${2}	${2}
	Verify Scenario Test Row Settings	${scenario_content_list}	${expected_row_settings_data7}	${2}	${2}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Robot File								AND
	...    Delete Scenario File		${scenario_name}

Verify the Manager Handles Scenario Files With Missing Scripts Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #241
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	1						AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI		${mngr_options}								AND
	...    Create Robot File	name=example.robot	file_content=***Test Case***\nExample Test Case\n

	${scenario_name}=	Set Variable	test_scenario_missing_file
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#241${/}test_scenario_missing_file.rfs
	Copy File	${scenariofile}		${global_path}

	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}

	Wait For	${platform}_warning_label.png	timeout=30
	Take A Screenshot
	Press key.enter 1 Times
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Fail	RFSwarm manager crashed!
	END
	TRY
		Click Tab	Run
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
		Click Tab	Plan
	EXCEPT
		Fail	msg=RFSwarm Manager is not responding!
	END

	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI		${mngr_options}

	Wait For	${platform}_warning_label.png	timeout=30
	Press key.enter 1 Times
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Fail	RFSwarm Manager crashed!
	END
	TRY
		Click Tab	Run
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
		Click Tab	Plan
	EXCEPT
		Fail	msg=RFSwarm Manager is not responding!
	END

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Robot File								AND
	...    Delete Scenario File		${scenario_name}

Verify If Manager Saves Inject Sleep From Scenario Wide Settings
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600										AND
	...    Open Manager GUI															AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]			AND
	...    Create Robot File

	@{inject_sleep_values}	Create List		11	22
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario Wide Settings Data	${scenario_content_list}	${run_settings_data}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If the Manager Reopens Inject Sleep From Scenario Wide Settings Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600										AND
	...    Open Manager GUI															AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]			AND
	...    Create Robot File

	@{inject_sleep_values}	Create List		999	9999
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario Wide Settings Data	${scenario_content_list}	${run_settings_data}

	Click Button	runopen
	Sleep	2
	Press key.enter 1 Times
	Open Scenario File OS DIALOG	${scenario_name}
	Check That The Scenario File Opens Correctly	${scenario_name}	${scenario_content}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If the Manager (after was closed) Opens Inject Sleep From Scenario Wide Settings Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	1					AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI		${mngr_options}							AND
	...    Create Robot File

	@{inject_sleep_values}	Create List		11	22
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario Wide Settings Data	${scenario_content_list}	${run_settings_data}

	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI	${mngr_options}
	Check That The Scenario File Opens Correctly	${scenario_name}	${scenario_content}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Verify If Row Specific Settings Override Inject Sleep From Scenario Wide Settings
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600										AND
	...    Open Manager GUI															AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]			AND
	...    Create Robot File

	@{settings_locations}	Create List
	@{inject_sleep_values}	Create List		11	22	13	24	15	26
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Click Button	runaddrow
	Click
	Sleep	3
	FOR  ${i}  IN RANGE  1  4
		Press Key.tab 8 Times
		${settings_coordinates}=
		...    Locate	manager_${platform}_button_selected_runsettingsrow.png
		Append To List	${settings_locations}	${settings_coordinates}
		Press Key.tab 1 Times
	END
	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}

	Click To The Above Of	${settings_locations}[0]	0
	&{first_row_settings_data}	Create Dictionary	inject_sleep=False	inject_sleep_min=${inject_sleep_values}[2]	inject_sleep_max=${inject_sleep_values}[3]
	Change Test Group Settings	${first_row_settings_data}
	Click To The Above Of	${settings_locations}[2]	0
	&{third_row_settings_data}	Create Dictionary	inject_sleep=False	inject_sleep_min=${inject_sleep_values}[4]	inject_sleep_max=${inject_sleep_values}[5]
	Change Test Group Settings	${third_row_settings_data}

	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	@{scenario_content_list}=	Split String	${scenario_content}

	Verify Scenario Wide Settings Data	${scenario_content_list}	${run_settings_data}
	Verify Scenario Test Row Settings	${scenario_content_list}	${first_row_settings_data}	${1}	${1}
	Verify Scenario Test Row Settings	${scenario_content_list}	${third_row_settings_data}	${3}	${3}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If Inject Sleep Option Was Executed in the Test
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Remove Directory	${results_dir}	recursive=${True}				AND
	...    Create Directory	${results_dir}									AND
	...    Sleep	3														AND
	...    Set Test Variable	@{agent_options}	-d	${OUTPUT DIR}${/}rfswarm-agent-Test-1	AND
	...    Open Agent	${agent_options}														AND
	...    Open Manager GUI													AND
	...    Create Robot File	file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t9s\n\tSleep\t9\n

	@{inject_sleep_values}	Create List		10	15

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#174${/}test_scenario.rfs
	Copy File	${scenariofile}	${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	Sleep	10
	Check If The Agent Is Ready

	@{excluded_files}=	Create List		Example_Test_Case.log	log.html	report.html		Example.log
	${result_absolute_paths}	${result_file_names}
	...    Find Absolute Paths And Names For Files In Directory		${results_dir}	@{excluded_files}

	Log		${result_file_names}
	FOR  ${result_file}  IN  @{result_absolute_paths}
		${file_extenstion}	Get Substring	${result_file}	-3
		IF  '${file_extenstion}' == 'xml'
			${xml_file_content}		Get File	${result_file}
			Log		${xml_file_content}
			BREAK
		END
	END
	Variable Should Exist	${xml_file_content}		msg="Not xml file found in manager result directory!"
	Should Not Be Empty		${xml_file_content}		msg=The xml file is empty!
	TRY
		${root}		Parse XML	${xml_file_content}
	EXCEPT
		Fail	msg=The xml file is invalid!
	END

	${test_element}	Get Element	${root}	suite/test
	@{keyword_elements}	Get Elements	${test_element}	kw
	FOR  ${upper_keywords}  IN  @{keyword_elements}
		@{inside_keyword_elements}	Get Elements	${upper_keywords}	kw
		Append To List		${keyword_elements}		@{inside_keyword_elements}
	END

	${dont_fail}	Set Variable	${False}
	FOR  ${keyword}  IN  @{keyword_elements}
		@{msg_elements}	Get Elements	 ${keyword}	msg
		FOR  ${msg}  IN  @{msg_elements}
			IF  '${msg.text}' == 'Sleep added by RFSwarm'
				Log To Console	Sleep keyword added by RFSwarm found.
				Log To Console	${msg.text}

				@{rfswarm_sleep_value}	Get Elements	${keyword}	arg
				${sleep_value_by_rfswarm}	Set Variable	${rfswarm_sleep_value}[0]
				Log To Console	RFSwarm Sleep value: ${sleep_value_by_rfswarm.text}
				Should Be True	${sleep_value_by_rfswarm.text} >= ${inject_sleep_values}[0] and ${sleep_value_by_rfswarm.text} <= ${inject_sleep_values}[1]
				...    msg=Sleep time is not correct! Should be in <${inject_sleep_values}[0];${inject_sleep_values}[1]>

				${dont_fail}	Set Variable	${True}
				BREAK
			END
		END
	END

	Run Keyword If	${dont_fail} == ${False}	Fail	msg="Cant find sleep keyword injected by RFSwarm"

	[Teardown]	Run Keywords
	...    Delete Scenario File	test_scenario				AND
	...    GUI_Common.Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot

Verify Disable log.html - Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-sl.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	unchecked 	loghtml
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	disableloglog
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][disableloglog] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	checked 	loghtml
	Click Dialog Button 	ok
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Disable report.html - Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-sr.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	unchecked 	reporthtml
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	disablelogreport
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][disablelogreport] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	checked 	reporthtml
	Click Dialog Button 	ok
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Disable output.xml - Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-so.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	unchecked 	outputxml
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	disablelogoutput
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][disablelogoutput] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Click CheckBox 	checked 	outputxml
	Click Dialog Button 	ok
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Disable log.html - Test Row
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${testkey}= 	Set Variable 		disableloglog
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-trl.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofilebefore}[1] 	${testkey}

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	unchecked 	loghtml
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	checked 	loghtml
	Test Group Save Settings
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofileafter2}[1] 	${testkey}
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Disable report.html - Test Row
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${testkey}= 	Set Variable 		disablelogreport
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-trl.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofilebefore}[1] 	${testkey}

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	unchecked 	reporthtml
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	checked 	reporthtml
	Test Group Save Settings
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofileafter2}[1] 	${testkey}
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Disable output.xml - Test Row
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #151
	${testkey}= 	Set Variable 		disablelogoutput
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#151${/}Issue-#151-trl.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore} 	console=True
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofilebefore}[1] 	${testkey}

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	unchecked 	outputxml
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Click CheckBox 	checked 	outputxml
	Test Group Save Settings
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofileafter2}[1] 	${testkey}
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

# Issue #16 here

Verify If Agent Copies Every File From Manager. FORMAT: '.{/}dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    CommandLine_Common.Run Agent	${agent_options}									AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main1.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths}	${M_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${CURDIR}${/}testdata${/}Issue-52${/}example
	Log 	${M_absolute_paths}
	Log 	${M_file_names}

	Copy Directory	${CURDIR}${/}testdata${/}Issue-52${/}example	${global_path}
	Copy File	${CURDIR}${/}testdata${/}Issue-52${/}test_scenario.rfs	${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	test_scenario
	Check If The Agent Is Ready
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	# Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	# Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	${M_rel_paths}= 		Get Relative Paths 		${CURDIR}${/}testdata${/}Issue-52${/}example${/}main 		${M_absolute_paths}
	${A_rel_paths}= 		Get Relative Paths 		${TEMPDIR}${/}agent_temp_issue52${/}scripts		${A_absolute_paths}
	Diff Lists 		${M_rel_paths} 		${A_rel_paths} 	Files are not transferred correctly! List A - Manager, List B - Agent, Check report for more information.

	[Teardown]	Run Keywords
	...    Delete Scenario File	test_scenario										AND
	...    Remove Directory	${global_path}${/}example	recursive=${True}			AND
	...    Remove Directory	${TEMPDIR}${/}agent_temp_issue52	recursive=${True}	AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main${/}main1.robot	${CURDIR}${/}testdata${/}Issue-52	AND
	...    CommandLine_Common.Stop Agent											AND
	...    CommandLine_Common.Stop Manager

Verify If Agent Copies Every File From Manager. FORMAT: '{CURDIR}{/}dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    CommandLine_Common.Run Agent	${agent_options}									AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main2.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths}	${M_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${CURDIR}${/}testdata${/}Issue-52${/}example
	Log 	${M_absolute_paths}
	Log 	${M_file_names}

	Copy Directory	${CURDIR}${/}testdata${/}Issue-52${/}example	${global_path}
	Copy File	${CURDIR}${/}testdata${/}Issue-52${/}test_scenario.rfs	${global_path}
	${scenario_path}	Set Variable	${global_path}${/}test_scenario.rfs
	Change main1 With main2 In ${scenario_path}

	Click Button	runopen
	Open Scenario File OS DIALOG	test_scenario
	Check If The Agent Is Ready
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	# Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	# Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	${M_rel_paths}= 		Get Relative Paths 		${CURDIR}${/}testdata${/}Issue-52${/}example${/}main 		${M_absolute_paths}
	${A_rel_paths}= 		Get Relative Paths 		${TEMPDIR}${/}agent_temp_issue52${/}scripts		${A_absolute_paths}
	Diff Lists 		${M_rel_paths} 		${A_rel_paths} 	Files are not transferred correctly! List A - Manager, List B - Agent, Check report for more information.

	[Teardown]	Run Keywords
	...    Delete Scenario File	test_scenario										AND
	...    Remove Directory	${global_path}${/}example	recursive=${True}			AND
	...    Remove Directory	${TEMPDIR}${/}agent_temp_issue52	recursive=${True}	AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main${/}main2.robot	${CURDIR}${/}testdata${/}Issue-52	AND
	...    CommandLine_Common.Stop Agent											AND
	...    CommandLine_Common.Stop Manager

Verify If Agent Copies Every File From Manager. FORMAT: 'dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    CommandLine_Common.Run Agent	${agent_options}									AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main3.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths}	${M_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${CURDIR}${/}testdata${/}Issue-52${/}example
	Log 	${M_absolute_paths}
	Log 	${M_file_names}

	Copy Directory	${CURDIR}${/}testdata${/}Issue-52${/}example	${global_path}
	Copy File	${CURDIR}${/}testdata${/}Issue-52${/}test_scenario.rfs	${global_path}
	${scenario_path}	Set Variable	${global_path}${/}test_scenario.rfs
	Change main1 With main3 In ${scenario_path}

	Click Button	runopen
	Open Scenario File OS DIALOG	test_scenario
	Check If The Agent Is Ready
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	# Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	# Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	${M_rel_paths}= 		Get Relative Paths 		${CURDIR}${/}testdata${/}Issue-52${/}example${/}main 		${M_absolute_paths}
	${A_rel_paths}= 		Get Relative Paths 		${TEMPDIR}${/}agent_temp_issue52${/}scripts		${A_absolute_paths}
	Diff Lists 		${M_rel_paths} 		${A_rel_paths} 	Files are not transferred correctly! List A - Manager, List B - Agent, Check report for more information.

	[Teardown]	Run Keywords
	...    Delete Scenario File	test_scenario										AND
	...    Remove Directory	${global_path}${/}example	recursive=${True}			AND
	...    Remove Directory	${TEMPDIR}${/}agent_temp_issue52	recursive=${True}	AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main${/}main3.robot	${CURDIR}${/}testdata${/}Issue-52	AND
	...    CommandLine_Common.Stop Agent											AND
	...    CommandLine_Common.Stop Manager

Check If The CSV Report Button Works In The Manager
	[Tags]	windows-latest	macos-latest	ubuntu-latest	Issue #254
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Agent

	${test_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#254
	@{mngr_options}= 	Create List 	-d	${test_dir}	-s 	${test_dir}${/}Issue-#254.rfs
	Open Manager GUI 		${mngr_options}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.
	Click Button	csv_report

	Wait For	manager_${platform}_reportdatasavesto.png 	timeout=${300}

	# Take A Screenshot
	Press key.enter 1 Times
	# Click Button 	ok
	# Click Dialog Button 	ok
	Sleep	5
	# Take A Screenshot

	@{test_results_dir}=	List Directories In Directory	${test_dir}		absolute=${True}	pattern=*Issue-#254
	@{csv_file_paths}=		List Files In Directory		${test_results_dir}[0]	*.csv

	${len}=		Get Length		${csv_file_paths}
	@{expected_csv_report_files}	Create List		agent_data.csv  raw_result_data.csv  summary.csv
	@{csv_report_files}	Create List
	FOR  ${i}  IN RANGE  0  ${len}
		Log To Console	${\n}CSV report file found: ${csv_file_paths}[${i}]
		${csv_report_file_type}=	Split String From Right		${csv_file_paths}[${i}]	separator=_Issue-#254_	max_split=1
		${csv_report_file_type}=	Set Variable	${csv_report_file_type}[-1]
		Append To List	${csv_report_files}	${csv_report_file_type}
	END
	Diff Lists	${csv_report_files}	${expected_csv_report_files}
	...    message=CSV Test Report Files are not generated correctly! List A - Generated CSV Files, List B - Expected CSV Files, Check report for more information.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    GUI_Common.Stop Agent

Check If Scenario Csv Report Files Contain Correct Data From The Test
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #17
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Agent

	${test_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#17
	@{mngr_options}= 	Create List 	-d	${test_dir}	-s 	${test_dir}${/}Issue-#17.rfs
	Open Manager GUI 		${mngr_options}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.
	Click Button	csv_report
	Press key.enter 1 Times
	Sleep	3
	
	@{test_results}=	List Directories In Directory	${test_dir}		absolute=${True}	pattern=*Issue-#17
	@{csv_file_paths}=		List Files In Directory		${test_results}[0]	*.csv	absolute=${True}
	Length Should Be	${csv_file_paths}	3	msg=Some test report csv files are missing!

	# Verify CSV report files content:
	FOR  ${i}  IN RANGE  0  3
		${csv_rows_content_list}=	Convert CSV File Cells To a List		${csv_file_paths}[${i}]		csv_separator=,
		Log To Console	${\n}CSV report file found: ${csv_file_paths}[${i}]
		Log 	${csv_rows_content_list}

		${csv_report_file_type}=	Split String From Right		${csv_file_paths}[${i}]	separator=_Issue-#17_	max_split=1
		${csv_report_file_type}=	Set Variable	${csv_report_file_type}[-1]
		IF  '${csv_report_file_type}' == 'summary.csv'
			Length Should Be	${csv_rows_content_list}	2	msg=Some rows in summary.csv are missing, should be 2!

			@{header_row_list}=		Set Variable	${csv_rows_content_list}[0]
			Log To Console	summary.csv: ${header_row_list}
			@{expected_header_row_list}	Create List		Result Name  Min  Avg  90%ile  Max  Stdev  Pass  Fail  Other
			Diff Lists		${header_row_list}		${expected_header_row_list}
			...    message=CSV Report Files are not generated correctly! List A - CSV summary file header row, List B - Expected header row values.

			@{second_row}=		Set Variable	${csv_rows_content_list}[1]
			Log		${second_row}
			Should Be Equal		${second_row}[0]	10 seconds
			...    msg=CSV summary File did not save correctly in the Result Name column, second row!

			Length Should Be	${second_row}	9	msg=Some columns in summary.csv are missing in second row, should be 9 of them!

		ELSE IF  '${csv_report_file_type}' == 'raw_result_data.csv'
			${len}=		Get Length	${csv_rows_content_list}
			Should Be True	${len} >= ${3}		msg=Some rows in raw_result_data.csv are missing, should be at least 3!

			@{header_row_list}=		Set Variable	${csv_rows_content_list}[0]
			Log To Console	raw_result_data.csv: ${header_row_list}
			@{expected_header_row_list}	Create List		Script Index  Robot  Iteration  Agent  Sequence  Result Name  Result  Elapsed Time  Start Time  End Time
			Diff Lists		${header_row_list}		${expected_header_row_list}
			...    message=CSV Report Files are not generated correctly! List A - CSV raw_result_data file header row, List B - Expected header row values.

			@{first_data_row}=	Set Variable	${csv_rows_content_list}[1]
			${Agent_name}=	Set Variable	${first_data_row}[3]
			FOR  ${j}  IN RANGE  1  ${len}
				@{data_row}=	Set Variable	${csv_rows_content_list}[${j}]
				Log		${data_row}

				Should Be Equal		${data_row}[0]	1
				...    msg=CSV raw_result_data File did not save correctly in the Script Index column, ${j+1} row!
				Should Be True		${${data_row}[1]} >= ${1} and ${${data_row}[1]} <= ${10}
				...    msg=CSV raw_result_data File did not save correctly in the Robot column, ${j+1} row!
				Should Be True		${${data_row}[0]} <= ${3}
				...    msg=CSV raw_result_data File did not save correctly in the Iteration column, ${j+1} row!
				Should Be Equal		${data_row}[3]	${Agent_name}
				...    msg=CSV raw_result_data File did not save correctly in the Agent column, ${j+1} row!
				Should Be Equal		${data_row}[4]	1
				...    msg=CSV raw_result_data File did not save correctly in the Sequence column, ${j+1} row!
				Should Be Equal		${data_row}[5]	10 seconds
				...    msg=CSV raw_result_data File did not save correctly in the Result Name column, ${j+1} row!

				Length Should Be	${data_row}	10	msg=Some columns in raw_result_data.csv are missing in ${j+1}nd row, should be 10 of them!
			END

		ELSE IF  '${csv_report_file_type}' == 'agent_data.csv'
			${len}=		Get Length	${csv_rows_content_list}
			Should Be True	${len} >= ${3}		msg=Some rows in agent_data.csv are missing, should be at least 3!

			@{header_row_list}=		Set Variable	${csv_rows_content_list}[0]
			Log To Console	agent_data.csv: ${header_row_list}
			@{expected_header_row_list}	Create List		Agentname  Agentstatus  Agentlastseen  Agentassigned  Agentrobots  Agentload  Agentcpu  Agentmem  Agentnet
			Diff Lists		${header_row_list}		${expected_header_row_list}
			...    message=CSV Report Files are not generated correctly! List A - CSV agent_data file header row, List B - Expected header row values.

			@{expected_status}	Create List  Ready  Running  Critical  Stopping
			@{first_data_row}=	Set Variable	${csv_rows_content_list}[1]
			${Agent_name}=	Set Variable	${first_data_row}[0]
			FOR  ${j}  IN RANGE  1  ${len}
				@{data_row}=	Set Variable	${csv_rows_content_list}[${j}]
				Log		${data_row}

				Should Be Equal		${data_row}[0]	${Agent_name}
				...    msg=CSV agent_data File did not save correctly in the Agentname column, ${j+1} row!
				IF  '${data_row}[1]' not in @{expected_status}
					Fail	msg=CSV agent_data File did not save correctly in the Agentstatus column, ${j+1} row! ${data_row}[1] not in ${expected_status}.
				END
				Should Be True		${${data_row}[3]} >= ${0} and ${${data_row}[3]} <= ${10}
				...    msg=CSV agent_data File did not save correctly in the Agentassigned column, ${j+1} row!
				Should Be True		${${data_row}[4]} >= ${0} and ${${data_row}[4]} <= ${10}
				...    msg=CSV agent_data File did not save correctly in the Agentrobots column, ${j+1} row!

				Length Should Be	${data_row}		9	msg=Some columns in agent_data.csv are missing in ${j+1}nd row, should be 9 of them!
			END

		ELSE
			Fail	msg=Unexpected csv file found: ${csv_file_paths}[${i}].
		END
	END

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    GUI_Common.Stop Agent

Verify the Results Directory And db File Gets Created Correctly With Scenario Also After a Restart
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #35	Issue #69
	[Setup]	Run Keywords
	...    Clear Manager Result Directory									AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI													AND
	...    Open Agent														AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Create Robot File
	...    file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\tFail this\n\tSleep\t10\n\tFail\n

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#35_#69${/}Issue-#35_#69.rfs
	${scenario_name}	Set Variable	Issue-#35_#69
	Copy File	${scenariofile}		${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Wait For	manager_${platform}_button_stoprun.png 	timeout=${300}
	${current_date}=	Get Current Date
	Log To Console	Current time: ${current_date}

	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_*
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	Length Should Be	${run_result_dirs}	1	msg=The test run result dir was not created or created unexpected directories!

	Sleep	5
	Verify Test Result Directory Name	${run_result_dirs}[0]	${scenario_name}	${current_date}
	Verify Generated Run Result Files	${run_result_dirs}[0]	${scenario_name}

	Log To Console	${\n}${\n}All verifications passed. The test run is now being restarted.${\n}${\n}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Wait For	manager_${platform}_button_stoprun.png 	timeout=${300}
	${current_date}=	Get Current Date
	Log To Console	Current time: ${current_date}

	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	${previous_result_dir}=		Set Variable	${run_result_dirs}[0]
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_*
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	Length Should Be	${run_result_dirs}	2	msg=The second test run result dir was not created or created unexpected directories!
	FOR  ${dir}  IN  @{run_result_dirs}
		IF  '${dir}' != '${previous_result_dir}'
			${result_dir_name}	Set Variable	${dir}
		END
	END

	Sleep	5
	Verify Test Result Directory Name	${result_dir_name}		${scenario_name}	${current_date}
	Verify Generated Run Result Files	${result_dir_name}		${scenario_name}

	[Teardown]	Run Keywords
	...    Delete Robot File						AND
	...    Delete Scenario File	${scenario_name}	AND
	...    GUI_Common.Stop Agent					AND
	...    Run Keyword		Close Manager GUI ${platform}

Verify the Results Directory And db File Gets Created Correctly Without Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #35	Issue #69
	[Setup]	Run Keywords
	...    Clear Manager Result Directory									AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI													AND
	...    Open Agent														AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Create Robot File
	...    file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\tFail this\n\tSleep\t10\n\tFail\n

	${scenario_name}	Set Variable	Scenario
	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	30
	Click Button	runscriptrow
	# Select Robot File	${robot_data}[0]
	Select Robot File OS DIALOG 	${robot_data}[0]
	Select 1 Robot Test Case
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Wait For	manager_${platform}_button_stoprun.png 	timeout=${300}
	${current_date}=	Get Current Date
	Log To Console	Current time: ${current_date}

	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_*
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	Length Should Be	${run_result_dirs}	1	msg=The test run result dir was not created or created unexpected directories!

	Sleep	5
	Verify Test Result Directory Name	${run_result_dirs}[0]	${scenario_name}	${current_date}
	Verify Generated Run Result Files	${run_result_dirs}[0]	${scenario_name}

	[Teardown]	Run Keywords
	...    Delete Robot File						AND
	...    GUI_Common.Stop Agent					AND
	...    Run Keyword		Close Manager GUI ${platform}

Check If Test Scenario Run Will Stop Fast (Agent sends terminate singal to the robots)
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	example.robot	AND
	...    Set INI Window Size		1200	600							AND
	...    Set Test Variable	@{agent_options}	-d	${OUTPUT DIR}${/}rfswarm-agent-Test-2	AND
	...    Open Agent	${agent_options}														AND
	...    Open Manager GUI												AND
	...    Create Robot File
	...    file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t60s\n\tSleep\t15\n\tSleep\t15\n\tSleep\t15\n\tSleep\t15\n

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#70${/}test_scenario.rfs
	Copy File	${scenariofile}		${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	Stop Test Scenario Run Quickly	${15}	${60}

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}		AND
	...    Set Confidence	0.9								AND
	...    GUI_Common.Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot

Check If Test Scenario Run Will Stop Gradually
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	example.robot							AND
	...    Set INI Window Size		1200	600													AND
	...    Set Test Variable	@{agent_options}	-d	${OUTPUT DIR}${/}rfswarm-agent-Test-3	AND
	...    Open Agent	${agent_options}														AND
	...    Open Manager GUI																		AND
	...    Create Robot File	file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t60s\n\tSleep\t60\n

	Utilisation Stats
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#70${/}test_scenario.rfs
	Copy File	${scenariofile}		${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	Stop Test Scenario Run Gradually	${15}	${60}

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}		AND
	...    Set Confidence	0.9								AND
	...    GUI_Common.Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot
