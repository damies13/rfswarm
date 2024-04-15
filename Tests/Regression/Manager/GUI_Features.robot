*** Settings ***
Library 	Collections
Library 	String
Resource 	GUI_Common.robot
Resource 	${CURDIR}${/}..${/}Agent${/}CommandLine_Common.robot
Suite Setup 	Set Platform

*** Variables ***
@{run_robots}
@{run_times_in_s}	#delay,		rump-up,	time
@{robot_data}=	example.robot	Example Test Case
&{row_settings_data}=	
...    excludelibraries=builtin,string,operatingsystem,perftest,collections	
...    robot_options=-v var:examplevariable	
...    test_repeater=True
@{settings_locations}
${scenario_name}=	test_scenario
${scenario_content}
${scenario_content_list}

*** Test Cases ***
Check If Run Will Stop Gradually
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600							AND
	...    CommandLine_Common.Run Agent									AND
	...    Open Manager GUI												AND
	...    Set Global Filename And Default Save Path	example.robot	AND
	...    Create Robot File	file_content=***Test Case***\nExample Test Case\n\t[Documentation]\tI am sleeping 10s\n\tSleep\t10

	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	30
	Click Button	runscriptrow
	Select Robot File	${robot_data}[0]
	Select 1 Robot Test Case
	Check If The Agent Has Connected To The Manager
	Click Tab	Plan
	Click Button	runplay
	Stop Agent Robots Gradually	${15}	${10}

	[Teardown]	Run Keywords
	...    Remove File	${global_path}${/}example.robot	AND
	...    CommandLine_Common.Stop Agent				AND
	...    CommandLine_Common.Stop Manager

Check If Run Will Stop With Terminate Signal (Ctrl + C)
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #70
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600							AND
	...    CommandLine_Common.Run Agent									AND
	...    Open Manager GUI												AND
	...    Set Global Filename And Default Save Path	example.robot	AND
	...    Create Robot File	file_content=***Test Case***\nExample Test Case\n\t[Documentation]\tI am sleeping 300s\n\tSleep\t300

	Press Key.tab 4 Times
	Type	15
	Press Key.tab 1 Times
	Type	30
	Click Button	runscriptrow
	Select Robot File	${robot_data}[0]
	Select 1 Robot Test Case
	Check If The Agent Has Connected To The Manager
	Click Tab	Plan
	Click Button	runplay
	Stop Agent With Terminate Signal	${15}

	[Teardown]	Run Keywords
	...    Remove File	${global_path}${/}example.robot	AND
	...    CommandLine_Common.Stop Agent				AND
	...    CommandLine_Common.Stop Manager

Insert Example Data To Manager
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Set INI Window Size		1200	600
	Open Manager GUI
	Set Global Filename And Default Save Path	${robot_data}[0]
	Create Robot File

	Click Button	runaddrow
	Click
	FOR  ${i}  IN RANGE  1  4
		Sleep	2
		FOR  ${j}  IN RANGE  1  5
			Press Key.tab 1 Times
			IF  '${j}' == '1' 
				Append To List	${run_robots}	${i}${j}${i}
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
		Press Key.tab 2 Times
		${settings_coordinates}=	
		...    Locate	manager_${platform}_button_selected_runsettingsrow.png
		Append To List	${settings_locations}	${settings_coordinates}
		Press Key.tab 1 Times
	END
	FOR  ${i}  IN RANGE  0  3
		Click To The Above Of	${settings_locations}[${i}]	0
		Change Test Group Settings		&{row_settings_data}
	END

Save Example Data To Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Click Button	runsave
	Save Scenario File	${scenario_name}
	Run Keyword		Close Manager GUI ${platform}

Set Scenario File Content And Show Example Data
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Set Global Filename And Default Save Path	${robot_data}[0]
	${scenario_content}=	Get scenario file content	${global_path}	${scenario_name}
	Set Suite Variable		${scenario_content} 	${scenario_content}
	${scenario_content_list}=	Split String	${scenario_content}
	Set Suite Variable		${scenario_content_list} 	${scenario_content_list}

	Log		${scenario_name}.rfs
	Log		${scenario_content}
	Log		${run_robots}
	Log		${run_times_in_s}
	Log		${robot_data}
	Log		${row_settings_data}

Verify Scenario File Robots
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]	#[1], [2], [3]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		Log		${row}

		${robots_offset}		Set Variable	${i + 1}
		Should Be Equal		robots	${scenario_content_list}[${robots_offset}]
		Should Be Equal		${run_robots}[${rows - 1}]	${scenario_content_list}[${robots_offset + 2}]
	END

Verify Scenario File Times
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		Log		${row}
		${time_indx}=	Evaluate	${rows - 1}*3

		${delay_offset}		Set Variable	${i + 4}
		Should Be Equal		delay	${scenario_content_list}[${delay_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx}]		${scenario_content_list}[${delay_offset + 2}]

		${rampup_offset}		Set Variable	${delay_offset + 3}
		Should Be Equal		rampup	${scenario_content_list}[${rampup_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx + 1}]		${scenario_content_list}[${rampup_offset + 2}]

		${run_offset}		Set Variable	${rampup_offset + 3}
		Should Be Equal		run		${scenario_content_list}[${run_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx + 2}]		${scenario_content_list}[${run_offset + 2}]
	END

Verify Scenario File Robot Data
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		Log		${row}

		${test_offset}		Set Variable	${i + 13}
		Should Be Equal		test	${scenario_content_list}[${test_offset}]
		${test_name}=	Catenate	
		...    ${scenario_content_list[${test_offset + 2}]}	
		...    ${scenario_content_list[${test_offset + 3}]}	
		...    ${scenario_content_list[${test_offset + 4}]}
		Should Be Equal		${robot_data}[1]	${test_name}

		${script_offset}		Set Variable	${i + 18}
		Should Be Equal		script	${scenario_content_list}[${script_offset}]
		Should Be Equal		${robot_data}[0]	${scenario_content_list}[${script_offset + 2}]
	END

Verify Scenario File Settings
	[Tags]	windows-latest	ubuntu	latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		Log		${row}

		IF  'excludelibraries' in ${row_settings_data}
			${exlibraries_offset}		Set Variable	${i + 21}
			Should Be Equal		excludelibraries	${scenario_content_list}[${exlibraries_offset}]
			Should Be Equal		${row_settings_data['excludelibraries']}	${scenario_content_list}[${exlibraries_offset + 2}]
		END

		IF  'robot_options' in ${row_settings_data}
			${robot_options_offset}		Set Variable	${i + 24}
			Should Be Equal		robotoptions	${scenario_content_list}[${robot_options_offset}]
			${robot_options}=	Catenate	
			...    ${scenario_content_list[${robot_options_offset + 2}]}	
			...    ${scenario_content_list[${robot_options_offset + 3}]}
			Should Be Equal		${row_settings_data['robot_options']}	${robot_options}
		END

		IF  'test_repeater' in ${row_settings_data}
			${repeater_offset}		Set Variable	${i + 28}
			Should Be Equal		testrepeater	${scenario_content_list}[${repeater_offset}]
			Should Be Equal		${row_settings_data['test_repeater']}	${scenario_content_list}[${repeater_offset + 2}]
		END
	END

Chceck That The Scenario File Opens Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Open Manager GUI
	Set Global Filename And Default Save Path	${robot_data}[0]
	Click Button	runsave
	${scenario_content_reopened}=	Get scenario file content	${global_path}	${scenario_name}
	Log		${scenario_content}
	Log		${scenario_content_reopened}
	Should Be Equal		${scenario_content}		${scenario_content_reopened}	msg=Scenario files are not equal!

Clean Issue #1 Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Run Keyword		Close Manager GUI ${platform}
	Set Global Filename And Default Save Path	${robot_data}[0]
	Delete Robot File
	Delete Scenario File	${scenario_name}

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
	Open Scenario File	test_scenario
	Check If The Agent Has Connected To The Manager
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}	
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	
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
	Open Scenario File	test_scenario
	Check If The Agent Has Connected To The Manager
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}	
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	
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
	Open Scenario File	test_scenario
	Check If The Agent Has Connected To The Manager
	Sleep	30

	@{excluded_files}=	Create List	RFSListener3.py	RFSListener2.py	RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names}	
	...    Find Absolute Paths And Names For Files In Directory	${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	Compare Manager and Agent Files	${M_file_names}	${A_file_names}
	Compare Manager and Agent Files Content	${M_absolute_paths}	${A_absolute_paths}
	
	[Teardown]	Run Keywords	
	...    Delete Scenario File	test_scenario										AND	
	...    Remove Directory	${global_path}${/}example	recursive=${True}			AND	
	...    Remove Directory	${TEMPDIR}${/}agent_temp_issue52	recursive=${True}	AND	
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main${/}main3.robot	${CURDIR}${/}testdata${/}Issue-52	AND
	...    CommandLine_Common.Stop Agent											AND	
	...    CommandLine_Common.Stop Manager
