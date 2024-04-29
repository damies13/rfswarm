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
		Select Robot File	${robot_data}[0]
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
	...    Delete Scenario File	test_scenario				AND
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
		Select Robot File	${robot_data}[0]
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
	...    Set Test Variable	@{manager_options}	-g	1					AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI		${manager_options}							AND
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
		Select Robot File	${robot_data}[0]
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
	Open Manager GUI	${manager_options}
	Check That The Scenario File Opens Correctly	${scenario_name}	${scenario_content}

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

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
	...    Set Test Variable	@{manager_options}	-g	1					AND
	...    Set INI Window Size		1200	600								AND
	...    Open Manager GUI		${manager_options}							AND
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
	Open Manager GUI	${manager_options}
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

	@{inject_sleep_values}	Create List		11	22	13	24	15	26
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Click Button	runaddrow
	Click
	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}

	Click Button	runsettingsrow
	&{first_row_settings_data}	Create Dictionary	inject_sleep=False	inject_sleep_min=${inject_sleep_values}[2]	inject_sleep_max=${inject_sleep_values}[3]
	Change Test Group Settings	${first_row_settings_data}
	Click Label With Vertical Offset	button_runsettingsrow	25
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
	...    Delete Scenario File	test_scenario				AND
	...    Delete Robot File								AND
	...    Delete Scenario File	${scenario_name}

Check If Inject Sleep Option Was Executed in the Test
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #174
	[Setup]	Run Keywords
	...    Remove Directory	${results_dir}	recursive=${True}				AND
	...    Create Directory	${results_dir}									AND
	...    Sleep	3														AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set INI Window Size		1200	600								AND
	...    Open Agent														AND
	...    Open Manager GUI													AND
	...    Create Robot File	file_content=***Test Case***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t10s\n\tSleep\t10\n

	@{inject_sleep_values}	Create List		10	15
	&{run_settings_data}	Create Dictionary
	...    inject_sleep=True
	...    inject_sleep_min=${inject_sleep_values}[0]
	...    inject_sleep_max=${inject_sleep_values}[1]

	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	30
	Click Button	runscriptrow
	Select Robot File	${robot_data}[0]
	Select 1 Robot Test Case
	Click Button	runsettingsrow
	Change Test Group Settings	${run_settings_data}
	Check If The Agent Has Connected To The Manager
	Click Tab	Plan
	Click Button	runplay
	
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	@{excluded_files}=	Create List		Example_Test_Case.log	log.html	report.html		Example.log
	${xml_absolute_paths}	${xml_file_names}
	...    Find Absolute Paths And Names For Files In Directory	${results_dir}	@{excluded_files}

	Log	${xml_file_names}

	${xml_file_content}		Get File	${xml_absolute_paths}[1]
	${root}		Parse XML	${xml_file_content}
	@{rfswarm_sleep_value}	Get Elements	${root}	suite/test/kw[@name="Sleep"]/arg

	${sleep_by_rfswarm}			Set Variable	${rfswarm_sleep_value}[1]
	${sleep_value_by_rfswarm}	Set Variable	${rfswarm_sleep_value}[0]
	Log To Console	RFSwarm Sleep value: ${sleep_value_by_rfswarm}
	Should Be Equal	${sleep_by_rfswarm.text}		Sleep added by RFSwarm		msg=xml data != Expected name
	Should Be True	${sleep_value_by_rfswarm.text} >= ${inject_sleep_values}[0] and ${sleep_value_by_rfswarm.text} <= ${inject_sleep_values}[1]
	...    msg=Sleep time is not correct!

	[Teardown]	Run Keywords
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

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults


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

	Run Keyword		Close Manager GUI ${platform}

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

	Run Keyword		Close Manager GUI ${platform}

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

	Run Keyword		Close Manager GUI ${platform}

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

	Run Keyword		Close Manager GUI ${platform}

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

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2} 	console=True
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofileafter2}[1] 	${testkey}
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

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
	Check If The Agent Has Connected To The Manager
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
	Check If The Agent Has Connected To The Manager
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
	Check If The Agent Has Connected To The Manager
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

Check If Test Scenario Run Will Stop Fast (Agent sends terminate singal to the robots)
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	example.robot	AND
	...    Set INI Window Size		1200	600							AND
	...    Open Agent													AND
	...    Open Manager GUI												AND
	...    Create Robot File
	...    file_content=***Test Case***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t60s\n\tSleep\t15\n\tSleep\t15\n\tSleep\t15\n\tSleep\t15\n

	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	60
	Click Button	runscriptrow
	Select Robot File	${robot_data}[0]
	Select 1 Robot Test Case
	Check If The Agent Has Connected To The Manager
	Click Tab	Plan
	Click Button	runplay
	Stop Test Scenario Run Quickly	${15}	${60}

	[Teardown]	Run Keywords
	...    Set Confidence	0.9								AND
	...    GUI_Common.Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot

Check If Test Scenario Run Will Stop Gradually
	#[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	example.robot	AND
	...    Set INI Window Size		1200	600							AND
	...    Open Agent													AND
	...    Open Manager GUI												AND
	...    Create Robot File	file_content=***Test Case***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\t60s\n\tSleep\t60\n

	Utilisation Stats
	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	60
	Click Button	runscriptrow
	Select Robot File	${robot_data}[0]
	Select 1 Robot Test Case
	Check If The Agent Has Connected To The Manager
	Click Tab	Plan
	Click Button	runplay
	Stop Test Scenario Run Gradually	${15}	${60}

	[Teardown]	Run Keywords
	...    Set Confidence	0.9								AND
	...    GUI_Common.Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot
