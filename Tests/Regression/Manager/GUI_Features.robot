*** Settings ***
Test Tags       Features 	GUI

Library 	Collections
Library 	String
Resource 	GUI_Common.robot
Suite Setup 	GUI_Common.Set Platform

*** Variables ***
@{robot_data}=	example.robot	Example Test Case
${scenario_name}=	test_scenario

*** Test Cases ***
Manager Command Line PORT -p
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	VAR 	&{run_settings_data} 	bind_port_number=8148
	VAR 	@{mngr_options} 		-p 	${run_settings_data}[bind_port_number]
	VAR 	@{agent_options} 		-m 	http://localhost:${run_settings_data}[bind_port_number]/

	Open Manager GUI	${mngr_options}
	Log To Console	Check if Agent can connect to the new port number. New port number: ${run_settings_data}[bind_port_number].
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	not ${status}	Fail
	...    msg=The agent did not connect to the new port number!
	Log To Console	The Agent has connected to the Manager with ${run_settings_data}[bind_port_number] port and this was expected.
	Click Tab	Plan

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line IPADDRESS -e
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${ipv4} 	${ipv6} 	Get IP addresses
	Log To Console		${\n}IPV4 address: ${ipv4} ${\n}IPV6 address: ${ipv6}${\n}
	VAR		@{mngr_options} 		-e	${ipv4}[0]
	VAR		@{agent_options}		-m	http://${ipv4}[0]:8138/

	Open Manager GUI	${mngr_options}
	Log To Console	Check if Agent can connect to the Manager via ${ipv4}[0].
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	not ${status}	Fail
	...    msg=The agent did not connect to the Manager via ${ipv4}[0]!
	Log To Console	The Agent has connected to the Manager via ${ipv4}[0] and this was expected.
	Click Tab	Plan

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line DIR -d
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	VAR		@{mngr_options}		-n	-d	${global_path}${/}Issue-#14

	Create Directory	${global_path}${/}Issue-#14
	Open Manager GUI	${mngr_options}
	@{dir_list}=	List Directories In Directory	${global_path}${/}Issue-#14
	Should Be Equal As Strings	${dir_list}[0]	PreRun	msg=Manager didn't create PreRun directory in the new Results directory!

	[Teardown]	Run Keywords
	...    Terminate Process	${process_manager}	AND
	...    Remove Directory		${global_path}${/}Issue-#14		recursive=${True}

Manager Command Line DIR --dir
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	VAR		@{mngr_options}		-n	--dir	${global_path}${/}Issue-#14

	Create Directory	${global_path}${/}Issue-#14
	Open Manager GUI	${mngr_options}
	@{dir_list}=	List Directories In Directory	${global_path}${/}Issue-#14
	Should Be Equal As Strings	${dir_list}[0]	PreRun	msg=Manager didn't create PreRun directory in the new Results directory!

	[Teardown]	Run Keywords
	...    Terminate Process	${process_manager}	AND
	...    Remove Directory		${global_path}${/}Issue-#14		recursive=${True}

Manager Command Line STARTTIME -t
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${current_date}=	Get Current Date	result_format=%H:%M:%S
	Log To Console	Current time: ${current_date}
	${new_date}=	Subtract Time From Date 	${current_date} 	30 		date_format=%H:%M:%S 	result_format=%H:%M:%S
	VAR		@{mngr_options}		-t 	${new_date}

	Open Manager GUI	${mngr_options}
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Remaining" for scheduled start.

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Manager Command Line STARTTIME --starttime
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${current_date}=	Get Current Date	result_format=%H:%M:%S
	Log To Console	Current time: ${current_date}
	${new_date}=	Subtract Time From Date 	${current_date} 	30 		date_format=%H:%M:%S 	result_format=%H:%M:%S
	VAR		@{mngr_options}		--starttime 	${new_date}

	Open Manager GUI	${mngr_options}
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Remaining" for scheduled start.

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Manager Command Line SCENARIO -s
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	VAR		@{mngr_options}		-s	${scenariofile}

	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Log To Console	Run the example scenario to check that it has been loaded.

	TRY
		Click Button	runplay
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
	EXCEPT
		Press key.enter 1 Times 	# warning message
		Fail	msg=RFSwarm Manager didn't load and run the the example scenario!
	END

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line AGENTS -a
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	VAR		@{mngr_options}		-s	${scenariofile} 	-a	2

	Open Manager GUI	${mngr_options}
	Log To Console	Run Agents only once, but 2 are needed. The Manager should display a special message.
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_warning_label_not_enough_agents.png 	timeout=${10}
	IF	not ${status}
		# Try again with alt screenshot
		${status}=	Run Keyword And Return Status
		...    Wait For	${platform}_warning_label_not_enough_agents2.png 	timeout=${10}
	END

	IF	not ${status}
		Take A Screenshot
		Fail	msg=The manager didn't display expected prompt dialogue that says: Not enough Agents available to run Robots!
	END
	Press key.enter 1 Times

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line RUN -r
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	VAR 	@{mngr_options} 	-s	${scenariofile} 	-r

	Open Agent
	Open Manager GUI	${mngr_options}
	Log To Console	Wait for the Agent to connect, after that the scenario should start automatically.
	TRY
		Wait For	manager_${platform}_button_stoprun.png	timeout=60
	EXCEPT
		Press key.enter 1 Times
		Fail	msg=RFSwarm Manager didn't run the scenario automatically after connecting to the Agent!
	END

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line RUN --run
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	VAR 	@{mngr_options} 	-s	${scenariofile} 	--run

	Open Agent
	Open Manager GUI	${mngr_options}
	Log To Console	Wait for the Agent to connect, after that the scenario should start automatically.
	TRY
		Wait For	manager_${platform}_button_stoprun.png	timeout=60
	EXCEPT
		Press key.enter 1 Times
		Fail	msg=RFSwarm Manager didn't run the scenario automatically after connecting to the Agent!
	END

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Manager Command Line INI -i
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmManager.ini
	VAR		@{mngr_options}		-i	${inifile}

	Open Manager GUI	${mngr_options}
	Log To Console	Run Manager with alternate ini file with variable: display_index = True.
	Click Tab	Run
	Log To Console	Check that Index check box is selected.
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_checkbox_checked_default.png 	timeout=${10}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail
	...    msg=The manager did not load alternate ini file because it cannot find checked check box in the Run tab!

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Manager Command Line INI --ini
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmManager.ini
	VAR		@{mngr_options}		--ini	${inifile}

	Open Manager GUI	${mngr_options}
	Log To Console	Run Manager with alternate ini file with variable: display_index = True.
	Click Tab	Run
	Log To Console	Check that Index check box is selected.
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_checkbox_checked_default.png 	timeout=${10}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail
	...    msg=The manager did not load alternate ini file because it cannot find checked check box in the Run tab!

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Field Validation Is Working In the Manager Plan Screen
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #126
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI													AND
	...    Create Robot File	name=example.robot	file_content=***Test Case***\nExample Test Case\n

	@{scenario_names_list}=	Create List		robots  rampup  run  test  script  all
	&{expected_messages}=	Create Dictionary
	...    robots=Index 1 has no Robots
	...    rampup=Index 1 Ramp Up is < 10 sec
	...    run=Index 1 Run is < 10 sec
	...    test=Index 1 has no Test
	...    script=Index 1 has no Script
	...    all=Index 1 has no Robots Index 1 Ramp Up is < 10 sec Index 1 Run is < 10 sec Index 1 has no Script Index 1 has no Test

	FOR  ${name}  IN  @{scenario_names_list}
		${scenarioname}=	Set Variable	Issue-#126_${name}
		${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#126${/}${scenarioname}.rfs

		Copy File	${scenariofile}		${global_path}
		Click Button	runopen
		Open Scenario File OS DIALOG	${scenario_name}
		Press key.enter 1 Times
		Click Button	runplay
		Sleep	2
		${status}=	Run Keyword And Return Status
		...    Wait For	${platform}_warning_label_no_${name}.png 	timeout=${20}
		Take A Screenshot
		Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed warning label that says: ${expected_messages}[${name}].
		Press key.enter 1 Times
		Delete Scenario File	${scenario_name}

	END

	[Teardown]	Run Keywords
	...    Delete Robot File	${robot_data}[0]			AND
	...    Run Keyword		Close Manager GUI ${platform}

Verify That Files Get Saved With Correct Extension And Names
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #39
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI													AND
	...    Open Agent

	${scenario_name}=	Set Variable	Issue-#39
	Log To Console	Files to check: scenario file, csv result files.
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
	...    Stop Agent

Verify the Time Fields In the Plan Screen For Delay
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{delay_times_in_s} 	Create List		158			1592		5025
	@{updated_delay_times}	Create List		00:02:38	00:26:32	01:23:45
	${len}		Get Length	${delay_times_in_s}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 2 Times
		Take A Screenshot
		Type	${delay_times_in_s}[${i}]
		Press Key.tab 7 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 2 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_delay_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_delay_times}[${i}]	${copied_converted_delay_value}
		...    msg=The updated delay time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 7 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Time Fields In the Plan Screen For Delay: Complex Variations
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{delay_times} 			Create List 	2:56:30   36:91     25:73:81  3:14      1:5:7     8::12     7:43:     :53:9     12::      :38:      ::42
	@{updated_delay_times}	Create List 	02:56:30  00:37:31  26:14:21  00:03:14  01:05:07  08:00:12  07:43:00  00:53:09  12:00:00  00:38:00  00:00:42
	${len}		Get Length	${delay_times}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 2 Times
		Take A Screenshot
		Type	${delay_times}[${i}]
		Press Key.tab 7 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 2 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_delay_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_delay_times}[${i}]	${copied_converted_delay_value}
		...    msg=The updated delay time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 7 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Time Fields In the Plan Screen For Ramp Up
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{ramp_up_times_in_s} 	Create List		158			1592		5025
	@{updated_ramp_up_times}	Create List		00:02:38	00:26:32	01:23:45
	${len}		Get Length	${ramp_up_times_in_s}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 3 Times
		Take A Screenshot
		Type	${ramp_up_times_in_s}[${i}]
		Press Key.tab 6 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  3
		Press Key.tab 3 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_ramp_up_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_ramp_up_times}[${i}]	${copied_converted_ramp_up_value}
		...    msg=The updated ramp up time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 6 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Time Fields In the Plan Screen For Ramp Up: Complex Variations
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{ramp_up_times} 			Create List 	2:56:30   36:91     25:73:81  3:14      1:5:7     8::12     7:43:     :53:9     12::      :38:      ::42
	@{updated_ramp_up_times}	Create List 	02:56:30  00:37:31  26:14:21  00:03:14  01:05:07  08:00:12  07:43:00  00:53:09  12:00:00  00:38:00  00:00:42
	${len}		Get Length	${ramp_up_times}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 3 Times
		Take A Screenshot
		Type	${ramp_up_times}[${i}]
		Press Key.tab 6 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 3 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_ramp_up_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_ramp_up_times}[${i}]	${copied_converted_ramp_up_value}
		...    msg=The updated ramp up time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 6 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Time Fields In the Plan Screen For Run
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{run_times_in_s} 	Create List		158			1592		5025
	@{updated_run_times}	Create List		00:02:38	00:26:32	01:23:45
	${len}		Get Length	${run_times_in_s}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 4 Times
		Take A Screenshot
		Type	${run_times_in_s}[${i}]
		Press Key.tab 5 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  3
		Press Key.tab 4 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_run_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_run_times}[${i}]	${copied_converted_run_value}
		...    msg=The updated run time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 5 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

Verify the Time Fields In the Plan Screen For Run: Complex Variations
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #82
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Manager GUI

	@{run_times} 			Create List 	2:56:30   36:91     25:73:81  3:14      1:5:7     8::12     7:43:     :53:9     12::      :38:      ::42
	@{updated_run_times}	Create List 	02:56:30  00:37:31  26:14:21  00:03:14  01:05:07  08:00:12  07:43:00  00:53:09  12:00:00  00:38:00  00:00:42
	${len}		Get Length	${run_times}

	Click Button	runaddrow
	FOR  ${i}  IN RANGE  0  ${len - 2}
		Click
	END

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 4 Times
		Take A Screenshot
		Type	${run_times}[${i}]
		Press Key.tab 5 Times
	END

	Click Button	runaddrow

	FOR  ${i}  IN RANGE  0  ${len}
		Press Key.tab 4 Times
		Take A Screenshot
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_run_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_run_times}[${i}]	${copied_converted_run_value}
		...    msg=The updated run time did not convert to the time as expected [ Expected != Converted ]
		Press Key.tab 5 Times
	END

	[Teardown]	Run Keyword		Close Manager GUI ${platform}

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
	${img}=		Set Variable	manager_${platform}_button_rundelrow.png
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	35
	#Click Label With Vertical Offset	button_rundelrow	35
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
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot

Verify If the Agent Can Connect To the Manager And Download/Send Files - URL Has Trailing
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #98
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Agent

	${agent_def_path}=	Get Agent Default Save Path
	${agent_ini_file_content}=	Get File	${agent_def_path}${/}RFSwarmAgent.ini
	Should Contain	${agent_ini_file_content}	swarmmanager = http://localhost:8138/

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#98${/}Issue-#98.rfs
	VAR 	${agent_script_dir} 	${agent_dir}${/}scripts
	VAR 	@{mngr_options} 		-d 	${results_dir} 	-s 	${scenariofile}

	Open Manager GUI		${mngr_options}
	Wait Agent Ready
	Sleep	10s
	Should Exist	${agent_script_dir}${/}Issue-#98.robot
	Should Not Be Empty 	${agent_script_dir}${/}Issue-#98.robot
	Click Tab	Plan
	Click Button	runplay

	Log To Console	Started run, now wait 40s. Check if Agent will send results to the Manager.
	Sleep	40	#rampup=10
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_Issue-#98*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num}=	Get Length	${run_logs}
	Log To Console	Uploaded logs number after 40s: ${logs_num}
	Should Be True	${logs_num} >= 1
	...    msg=Agent is not uploading logs immediately! Should be at least 1 after ~ 40s. Actual number:${logs_num}.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}		AND
	...    Stop Agent											AND
	...    Remove File 	${agent_script_dir}${/}Issue-#98.robot	AND
	...    Remove Directory 	${run_result_dirs}[0]	resursive=${True}

Verify If the Agent Can Connect To the Manager And Download/Send Files - URL Has No Trailing
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #98
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Agent

	${agent_def_path}=	Get Agent Default Save Path
	Change http://localhost:8138/ With http://localhost:8138 In ${agent_def_path}${/}RFSwarmAgent.ini
	${agent_ini_file_content}=	Get File	${agent_def_path}${/}RFSwarmAgent.ini
	Should Contain	${agent_ini_file_content}	swarmmanager = http://localhost:8138

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#98${/}Issue-#98.rfs
	VAR 	${agent_script_dir} 	${agent_dir}${/}scripts
	VAR 	@{mngr_options} 		-d 	${results_dir} 	-s 	${scenariofile}

	Open Manager GUI		${mngr_options}
	Wait Agent Ready
	Sleep	10s
	Should Exist	${agent_script_dir}${/}Issue-#98.robot
	Should Not Be Empty 	${agent_script_dir}${/}Issue-#98.robot
	Click Tab	Plan
	Click Button	runplay

	Log To Console	Started run, now wait 40s. Check if Agent will send results to the Manager.
	Sleep	40	#rampup=10
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_Issue-#98*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num}=	Get Length	${run_logs}
	Log To Console	Uploaded logs number after 40s: ${logs_num}
	Should Be True	${logs_num} >= 1
	...    msg=Agent is not uploading logs immediately! Should be at least 1 after ~ 40s. Actual number:${logs_num}.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}		AND
	...    Stop Agent											AND
	...    Change http://localhost:8138 With http://localhost:8138/ In ${agent_def_path}${/}RFSwarmAgent.ini	AND
	...    Remove File 	${agent_script_dir}${/}Issue-#98.robot	AND
	...    Remove Directory 	${run_result_dirs}[0]	resursive=${True}

Verify If the Port Number And Ip Address Get Written To the INI File
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${ipv4}		${ipv6}		Get IP addresses
	Log To Console		${\n}IPV4 address: ${ipv4} ${\n}IPV6 address: ${ipv6}${\n}
	${manager_ini_file}		Get Manager INI Location
	&{run_settings_data}	Create Dictionary
	...    bind_ip_address=${ipv4}[0]
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

	[Teardown]	Run Keywords
	...    Change = ${ipv4}[0] With =${SPACE} In ${manager_ini_file}	AND
	...    Change = 8148 With = 8138 In ${manager_ini_file}

Verify If Agent Can't Connect On Old Port Number After Port Number Changed And Can Connect To the New One
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${old_port_number}=		Set Variable	8138
	&{run_settings_data}	Create Dictionary	bind_port_number=8148
	${manager_ini_file}		Get Manager INI Location

	Log To Console	Writing bindport=${run_settings_data}[bind_port_number] to the manager settings.
	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Sleep	2
	Press key.enter 1 Times
	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI

	Log To Console	Check if Agent cant connect to the old port number, Old port number: ${old_port_number}.
	@{agent_options}	Set Variable	-m	http://localhost:${old_port_number}/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	${status}	Fail
	...    msg=The agent has connected to the old port number but should not!
	Log To Console	The Agent did not connect to the Manager with ${old_port_number} port and this was expected.
	Click Tab	Plan
	Stop Agent

	Log To Console	Check if Agent can connect to the new port number. New port number: ${run_settings_data}[bind_port_number].
	@{agent_options}	Set Variable	-m	http://localhost:${run_settings_data}[bind_port_number]/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	not ${status}	Fail
	...    msg=The agent did not connect to the new port number!
	Log To Console	The Agent has connected to the Manager with ${run_settings_data}[bind_port_number] port and this was expected.
	Click Tab	Plan

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent							AND
	...    Change = 8148 With = 8138 In ${manager_ini_file}

Verify If Agent Can Only Connect Via the Specified Ip Address And Not Any Ip Address On the Manager's Host
	[Tags]	windows-latest 	ubuntu-latest 	macos-latest 	Issue #16
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Set Test Variable	@{mngr_options}	-g	0						AND
	...    Open Manager GUI		${mngr_options}

	${ipv4}		${ipv6}		Get IP addresses
	Log To Console		${\n}IPV4 address: ${ipv4} ${\n}IPV6 address: ${ipv6}${\n}
	${manager_ini_file}		Get Manager INI Location
	&{run_settings_data}	Create Dictionary	bind_ip_address=${ipv4}[0]

	Log To Console	Writing bindip=${ipv4}[0] to the manager settings.
	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Sleep	2
	Press key.enter 1 Times
	Run Keyword		Close Manager GUI ${platform}
	Open Manager GUI

	# ${altip}= 	Set Variable    ${ipv4} [1]
	${altip}= 	Set Variable    127.0.0.1
	Log To Console	Check if Agent cant connect to the Manager via ${altip} instead of ${ipv4}[0].
	@{agent_options}	Set Variable	-m	http://${altip}:8138/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	${status}	Fail
	...    msg=The agent has connected to the Manager via ${altip} but should not!
	Log To Console	The Agent did not connect to the Manager via ${altip} and this was expected.
	Click Tab	Plan
	Stop Agent

	Log To Console	Check if Agent can connect to the Manager via ${ipv4}[0].
	@{agent_options}	Set Variable	-m	http://${ipv4}[0]:8138/
	Open Agent	${agent_options}
	${status}=	Run Keyword And Return Status	Check If The Agent Is Ready		30
	Run Keyword If	not ${status}	Fail
	...    msg=The agent did not connect to the Manager via ${ipv4}[0]!
	Log To Console	The Agent has connected to the Manager via ${ipv4}[0] and this was expected.
	Click Tab	Plan

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent							AND
	...    Change = ${ipv4}[0] With =${SPACE} In ${manager_ini_file}

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

Verify If Agent Copies Every File From Manager. FORMAT: '.{/}dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    Open Agent	${agent_options}													AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main1.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths} 	${M_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${CURDIR}${/}testdata${/}Issue-52${/}example
	Log 	${M_absolute_paths}
	Log 	${M_file_names}

	Copy Directory	${CURDIR}${/}testdata${/}Issue-52${/}example	${global_path}
	Copy File	${CURDIR}${/}testdata${/}Issue-52${/}test_scenario.rfs	${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	test_scenario
	Check If The Agent Is Ready
	Sleep	30

	@{excluded_files}=	Create List  RFSListener3.py  RFSListener2.py  RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
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
	...    Stop Agent																AND
	...    Close Manager GUI ${platform}

Verify If Agent Copies Every File From Manager. FORMAT: '{CURDIR}{/}dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    Open Agent	${agent_options}													AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main2.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths}	${M_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${CURDIR}${/}testdata${/}Issue-52${/}example
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

	@{excluded_files}=	Create List  RFSListener3.py  RFSListener2.py  RFSTestRepeater.py
	${A_absolute_paths} 	${A_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
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
	...    Stop Agent																AND
	...    Close Manager GUI ${platform}

Verify If Agent Copies Every File From Manager. FORMAT: 'dir1{/}'
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #52	Issue #53
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600												AND
	...    Set Test Variable	@{agent_options}	-d	${TEMPDIR}${/}agent_temp_issue52	AND
	...    Open Agent	${agent_options}													AND
	...    Open Manager GUI																	AND
	...    Set Global Filename And Default Save Path	main								AND
	...    Move File	${CURDIR}${/}testdata${/}Issue-52${/}main3.robot	${CURDIR}${/}testdata${/}Issue-52${/}example${/}main

	${M_absolute_paths} 	${M_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${CURDIR}${/}testdata${/}Issue-52${/}example
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

	@{excluded_files}=	Create List  RFSListener3.py  RFSListener2.py  RFSTestRepeater.py
	${A_absolute_paths}	${A_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${TEMPDIR}${/}agent_temp_issue52	@{excluded_files}
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
	...    Stop Agent																AND
	...    Close Manager GUI ${platform}

Verify If __init__.robot Files Get Transfered To the Agent Along With Robot/Resuorce File
	[Tags]	windows-latest	macos-latest	ubuntu-latest	Issue #90
	[Setup]	Run Keywords
	...    Set INI Window Size		800		600		AND
	...    Set Global Filename And Default Save Path	main

	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#90${/}test_scenario.rfs
	VAR 	@{mngr_options} 	-s 	${scenariofile}
	VAR 	@{agent_options} 	-d 	${TEMPDIR}${/}agent_temp_issue90

	Open Agent	${agent_options}
	Open Manager GUI	${mngr_options}

	${example_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#90${/}example
	${M_absolute_paths} 	${M_file_names} 	Find Absolute Paths And Names For Files In Directory	${example_dir}
	Log 	${M_absolute_paths}
	Log 	${M_file_names}

	Check If The Agent Is Ready
	Sleep	30

	Log To Console	Verify if all __init__.robot files get transfered to the Agent script folder
	@{excluded_files}=	Create List  RFSListener3.py  RFSListener2.py  RFSTestRepeater.py
	${A_absolute_paths} 	${A_file_names} 	Find Absolute Paths And Names For Files In Directory
	...    ${TEMPDIR}${/}agent_temp_issue90 	@{excluded_files}
	Log 	${A_absolute_paths}
	Log 	${A_file_names}

	${M_rel_paths}= 		Get Relative Paths 		${CURDIR}${/}testdata${/}Issue-#90${/}example${/}main 		${M_absolute_paths}
	${A_rel_paths}= 		Get Relative Paths 		${TEMPDIR}${/}agent_temp_issue90${/}scripts 	${A_absolute_paths}
	Diff Lists 		${M_rel_paths} 		${A_rel_paths} 	Files are not transferred correctly! List A - Manager, List B - Agent, Check report for more information.

	Log To Console	Verify content of the __init__.robot files
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}__init__.robot
	Should Contain	${init_file}	example
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}dir4${/}__init__.robot
	Should Contain	${init_file}	dir4
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}scripts${/}__init__.robot
	Should Contain	${init_file}	main
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}scripts${/}dir1${/}__init__.robot
	Should Contain	${init_file}	dir1
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}scripts${/}dir1${/}dir2${/}__init__.robot
	Should Contain	${init_file}	dir2
	${init_file}=	Get File	${TEMPDIR}${/}agent_temp_issue90${/}scripts${/}dir1${/}dir2${/}dir3${/}__init__.robot
	Should Contain	${init_file}	dir3

	[Teardown]	Run Keywords
	...    Remove Directory 	${TEMPDIR}${/}agent_temp_issue90	recursive=${True}	AND
	...    Stop Agent																	AND
	...    Close Manager GUI ${platform}

Check If The CSV Report Button Works In the Manager Before There Are Any Results
	[Tags]	windows-latest	macos-latest	ubuntu-latest	Issue #128
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600		AND
	...    Open Agent

	# !!! Checking that the CSV report button works in the manager after results is being checked in Test Case for Issue #254 !!!
	${test_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#128
	@{mngr_options}= 	Create List 	-d	${test_dir}	-s 	${test_dir}${/}Issue-#128.rfs
	Open Manager GUI 		${mngr_options}
	Check If The Agent Is Ready

	Click Tab	Run
	Log To Console	Clicking CSV report button before there are any results.
	Click Button	csv_report
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_warning_label_no_report_data.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed warning label that says: No report data to save.
	Press key.enter 1 Times
	@{test_results_dir}=	List Directories In Directory	${test_dir}		absolute=${True}	pattern=*Issue-#128
	Length Should Be	${test_results_dir}		0	msg=Manager should not create any result directory.

	Click Tab	Plan
	Click Button	runplay
	Sleep	45
	Log To Console	Clicking CSV report button before end of the test.
	Click Button	csv_report
	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_reportdatasavesto.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed info label that says: Report data saved to:...
	Press key.enter 1 Times

	@{test_results_dir}=	List Directories In Directory	${test_dir}		absolute=${True}	pattern=*Issue-#128
	@{csv_files}=		List Files In Directory		${test_results_dir}[0]	*.csv
	Log To Console	${\n}Generated CSV report files before end of a test run: ${\n}${csv_files}
	${len}=		Get Length		${csv_files}
	Should Be True	${len} > 0	msg=Manager didn't generate any CSV report files. Should generate at least 1 most likely agent_data.csv.

	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Check If The CSV Report Button Works In The Manager After There Are Results
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
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.
	Click Button	csv_report

	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_reportdatasavesto.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed info label that says: Report data saved to:...

	# Take A Screenshot
	Press key.enter 1 Times
	# Click Button 	ok
	# Click Dialog Button 	ok
	Sleep	5
	# Take A Screenshot

	@{test_results_dir}=	List Directories In Directory	${test_dir}		absolute=${True}	pattern=*Issue-#254
	@{csv_files}=		List Files In Directory		${test_results_dir}[0]	*.csv

	${len}=		Get Length		${csv_files}
	@{expected_csv_report_files}	Create List		agent_data.csv  raw_result_data.csv  summary.csv
	@{csv_report_files}	Create List
	FOR  ${i}  IN RANGE  0  ${len}
		Log To Console	${\n}CSV report file found: ${csv_files}[${i}]
		${csv_report_file_type}=	Split String From Right		${csv_files}[${i}]	separator=_Issue-#254_	max_split=1
		${csv_report_file_type}=	Set Variable	${csv_report_file_type}[-1]
		Append To List	${csv_report_files}	${csv_report_file_type}
	END
	Diff Lists	${csv_report_files}	${expected_csv_report_files}
	...    message=CSV Test Report Files are not generated correctly! List A - Generated CSV Files, List B - Expected CSV Files, Check report for more information.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Verify If Manager Displays Prompt Dialogue When No Agents Available To Run Robots
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #31
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI													AND
	...    Create Robot File
	...    file_content=***Test Cases***\nExample Test Case\n\tTest\n***Keywords***\nTest\n\t[Documentation]\tFail this\n\tSleep\t10\n\tFail\n

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#31${/}Issue-#31.rfs
	${scenario_name}=	Set Variable	Issue-#31
	Copy File	${scenariofile}		${global_path}
	Click Button	runopen
	Open Scenario File OS DIALOG	${scenario_name}
	Click Button	runplay

	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_warning_label_not_enough_agents.png 	timeout=${10}
	IF	not ${status}
		# Try again with alt screenshot
		${status}=	Run Keyword And Return Status
		...    Wait For	${platform}_warning_label_not_enough_agents2.png 	timeout=${10}
	END

	IF	not ${status}
		Take A Screenshot
		Fail	msg=The manager didn't display expected prompt dialogue that says: Not enough Agents available to run Robots!
	END

	Press key.enter 1 Times
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_abort 	timeout=${10}
	Run Keyword If	not ${status}	Fail	msg=The manager is not in waiting for agent status.

	Log To Console	${\n}The manager displayed the expected message. It is now waiting for the agent.${\n}

	Open Agent
	Check If The Agent Is Ready
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_info_label_enough_agents_available.png 	timeout=${15}
	Run Keyword If	not ${status}	Fail
	...    msg=The manager didn't display expected prompt dialogue that says: Enough Agent available to run Robots, test will now resume!
	Press key.enter 1 Times
	Click Tab	Run

	Log To Console	${\n}The manager displayed the expected message. Agent is ready. Test will now resume.${\n}

	Sleep	5
	Click Button	abort
	Press Key.tab 2 Times
	Move To	10	10
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	Click Tab	Plan
	Click Button	runplay
	${status}=	Run Keyword And Return Status
	...    Wait For	${platform}_warning_label_not_enough_agents.png 	timeout=${10}

	IF	not ${status}
		# Try again with alt screenshot
		${status}=	Run Keyword And Return Status
		...    Wait For	${platform}_warning_label_not_enough_agents2.png 	timeout=${10}
	END

	IF	${status}
		Take A Screenshot
		Fail	msg=The manager have displaed prompt dialogue that says: Not enough Agents available to run Robots! but that was not expected!
	END

	Sleep	5
	Click Button	stoprun
	Sleep	2
	Click
	Press Key.enter 1 Times
	Press Key.tab 2 Times
	Move To		10	10
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${300}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}		AND
	...    Delete Robot File								AND
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}

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

			@{expected_status}	Create List  Ready  Running  Critical  Stopping  Warning  Offline?
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
	...    Stop Agent

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
	...    Stop Agent					AND
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
	...    Stop Agent					AND
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
	...    Stop Agent							AND
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
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove File		${global_path}${/}example.robot

Verify the Iteration Counters Get Reset When a New Test Starts On the Agent
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #41
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${scenario_path}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#41${/}Issue-#41.rfs
	VAR 	@{mngr_options} 	-s 	${scenario_path}	-d 	${results_dir}

	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${360}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	Check If The Agent Is Ready
	Log To Console 	Running scenario one more time to test if iteration counter get reset.
	Click Tab	Plan
	Click Button	runplay
	Sleep	10
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${360}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.
	Check If The Agent Is Ready

	Log To Console 	Checking second run Database.
	${dbfile}= 	Find Result DB 		result_pattern=*_Issue-#41*
	${db_iterations}= 	Query Result DB 	${dbfile}
	...    SELECT DISTINCT MetricValue FROM MetricData WHERE SecondaryMetric='iteration' ORDER BY MetricValue
	Log 	Found iterations in MetricData after scenario second run: ${db_iterations}	console=${True}

	${first_iter}= 		Query Result DB 	${dbfile}	SELECT count(*) FROM Results WHERE iteration='1'
	${second_iter}= 	Query Result DB 	${dbfile}	SELECT count(*) FROM Results WHERE iteration='2'
	${third_iter}= 		Query Result DB 	${dbfile}	SELECT count(*) FROM Results WHERE iteration='3'
	Should Be Equal 	${first_iter}[0][0] 	${3}
	Should Be Equal 	${second_iter}[0][0] 	${3}
	Should Be Equal 	${third_iter}[0][0] 	${3}

	Log To Console 	Checking second run logs.
	@{run_result_dirs}= 	List Directories In Directory	${results_dir}	pattern=*_Issue-#41*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[-1]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]

	VAR 	@{iterations}
	FOR  ${log}  IN  @{run_logs}
		@{splitted_log}= 	Split String	${log}	separator=_
		VAR 	${iteration_number} 	${splitted_log}[-2]
		Append To List	${iterations}	${iteration_number}
	END
	${iterations_set}=	Evaluate	set(${iterations})
	Log 	Found iterations in logs after scenario second run: ${iterations_set}	console=${True}

	${first_iter} 	Count Values In List	${iterations}	1
	${second_iter} 	Count Values In List	${iterations}	2
	${third_iter} 	Count Values In List	${iterations}	3
	Should Be Equal 	${first_iter} 	${3}
	Should Be Equal 	${second_iter} 	${3}
	Should Be Equal 	${third_iter} 	${3}

	[Teardown]	Run Keywords
	...    Close Manager GUI ${platform}	AND
	...    Stop Agent

Verify the Robot Count Reduces When Stop Agent While Test Is Running
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #57	Issue #269
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${scenario_path}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#57${/}Issue-#57.rfs
	@{mngr_options}=	Create List		-s		${scenario_path}

	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay
	Sleep	60
	Set Confidence	0.95	#sometimes cant find 10 robots image
	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_robots_10.png 	timeout=${60}
	Run Keyword If	not ${status}	Fail	msg=Manager could not reach 10 robots after 60s.

	Log To Console	Stopping agent while test is running.
	Stop Agent
	Click Tab	Agents
	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_agents_offline.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Agent did not get marked as "offline?".
	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_agents_blank.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Agent did not disconnect form Manager completly. It is still connected.

	Log To Console	Checking if robot count will reduce to 0 after shuting down Agent.
	Click Tab	Run
	${status}=	Run Keyword And Return Status
	...    Wait For		manager_${platform}_robots_0.png 	timeout=${60}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail	msg=Manager didnt reduce robot count form 10 to 0 in 60s after disconnecting Agent.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${120}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent							AND
	...    Set Confidence	0.9

Verify the Files Referenced In the Scenario Are All Using Relative Paths
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #54
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${test_data_path}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#54
	${scenario_path}=	Normalize Path 	${test_data_path}${/}${scenario_name}.rfs
	Copy File	${test_data_path}${/}${scenario_name}_original.rfs	${scenario_path}
	@{paths}=			Create List
	...    ${test_data_path}  ${test_data_path}${/}robots  ${results_dir}  ${results_dir}${/}robots
	@{robot_names}=		Create List		robot_rel_1  robot_rel_2  robot_rel_3  robot_rel_4
	@{robot_paths}=		Create List
	...    ${paths}[0]${/}${robot_names}[0].robot
	...    ${paths}[1]${/}${robot_names}[1].robot
	...    ${paths}[2]${/}${robot_names}[2].robot
	...    ${paths}[3]${/}${robot_names}[3].robot
	@{rel_robot_paths}=		Get Relative Paths	${test_data_path}	${robot_paths}
	Log To Console	Robot relative paths to ${test_data_path}: ${\n}${\n}${rel_robot_paths}${\n}

	Create Robot File	path=${paths}[0]	name=${robot_names}[0].robot
	Create Robot File	path=${paths}[1]	name=${robot_names}[1].robot
	Create Robot File	path=${paths}[2]	name=${robot_names}[2].robot
	Create Robot File	path=${paths}[3]	name=${robot_names}[3].robot

	@{mngr_options}=	Create List		-s		${scenario_path}

	FOR  ${i}  IN RANGE  1  4	#skip first robot because it is in the same folder as the scenario
		Open Manager GUI	${mngr_options}

		Log To Console		Saving ${rel_robot_paths}[${i}] to the scenario.
		Click Button	runscriptrow
		File Open Dialogue Select File		${robot_paths}[${i}]
		Sleep	10
		Select 1 Robot Test Case
		Click Button	runsave
		Sleep	2
		${scenario_file_dict}=		Read Ini File 	${scenario_path}
		Log To Console		Scenario file with relative path: ${scenario_file_dict}
		Run Keyword And Warn On Failure		Should Be Equal As Strings		${scenario_file_dict}[1][script] 	${rel_robot_paths}[${i}]

		Run Keyword If  ${i} != 3		Close Manager GUI ${platform}
		Delete Scenario File		${scenario_name}
	END

	[Teardown]	Run Keywords
	...    Delete Robot File	path=${paths}[0]	name=${robot_names}[0].robot	AND
	...    Delete Robot File	path=${paths}[1]	name=${robot_names}[1].robot	AND
	...    Delete Robot File	path=${paths}[2]	name=${robot_names}[2].robot	AND
	...    Delete Robot File	path=${paths}[3]	name=${robot_names}[3].robot	AND
	...    Remove File			${scenario_path}									AND
	...    Close Manager GUI ${platform}

Verify If Upload logs=Immediately Is Being Saved To The Scenario And Read Back Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI

	&{run_settings_data}	Create Dictionary
	...    upload_logs=immediately

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_path}= 	Normalize Path 	${global_path}${/}${scenario_name}.rfs
	${scenario_file_content}= 		Read Ini File		${scenario_path}
	Log To Console	Scenario file content: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		imm

	Log To Console	${\n}Manager is now being restarted. Check if Upload logs=Immediately is read back correctly
	Run Keyword		Close Manager GUI ${platform}
	@{mngr_options}=	Set Variable	-s	${scenario_path}
	Open Manager GUI	${mngr_options}
	Click Button	runsave
	Log To Console	Scenario file content after Manager restart: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		imm

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}	AND
	...    Run Keyword		Close Manager GUI ${platform}

Verify If Upload logs=Error Only Is Being Saved To The Scenario And Read Back Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI

	&{run_settings_data}	Create Dictionary
	...    upload_logs=on_error_only

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_path}= 	Normalize Path 	${global_path}${/}${scenario_name}.rfs
	${scenario_file_content}= 		Read Ini File		${scenario_path}
	Log To Console	Scenario file content: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		err

	Log To Console	${\n}Manager is now being restarted. Check if Upload logs=Error Only is read back correctly
	Run Keyword		Close Manager GUI ${platform}
	@{mngr_options}=	Set Variable	-s	${scenario_path}
	Open Manager GUI	${mngr_options}
	Click Button	runsave
	Log To Console	Scenario file content after Manager restart: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		err

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}	AND
	...    Run Keyword		Close Manager GUI ${platform}

Verify If Upload logs=All Deferred Is Being Saved To The Scenario And Read Back Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI

	&{run_settings_data}	Create Dictionary
	...    upload_logs=all_deferred

	Click Button	runsettings
	Change Scenario Wide Settings	${run_settings_data}
	Click Button	runsave
	Save Scenario File OS DIALOG	${scenario_name}

	${scenario_path}= 	Normalize Path 	${global_path}${/}${scenario_name}.rfs
	${scenario_file_content}= 		Read Ini File		${scenario_path}
	Log To Console	Scenario file content: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		def

	Log To Console	${\n}Manager is now being restarted. Check if Upload logs=All Deferred is read back correctly
	Run Keyword		Close Manager GUI ${platform}
	@{mngr_options}=	Set Variable	-s	${scenario_path}
	Open Manager GUI	${mngr_options}
	Click Button	runsave
	Log To Console	Scenario file content after Manager restart: ${scenario_file_content}
	Dictionary Should Contain Key	${scenario_file_content}		Scenario
	Dictionary Should Contain Key	${scenario_file_content}[Scenario]		uploadmode
	Should Be Equal As Strings 	${scenario_file_content}[Scenario][uploadmode]		def

	[Teardown]	Run Keywords
	...    Delete Scenario File		${scenario_name}	AND
	...    Run Keyword		Close Manager GUI ${platform}

Verify If Upload logs=Immediately Uploads Logs As Soon As Robot Finishes Regardless Of Robot Passes Or Fails
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${scenarioname}=	Set Variable	immediately.rfs
	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${scenarioname}
	${robotname}=		Set Variable	immediately.robot
	${robotfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${robotname}

	Copy File	${scenariofile}		${global_path}
	Copy File	${robotfile}		${global_path}
	@{mngr_options}=	Set Variable	-s	${scenariofile}	-d	${results_dir}
	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Log To Console	Started run, now wait 40s.
	Sleep	40	#rampup=15 run=50
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_immediately*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num}=	Get Length	${run_logs}
	Log To Console	Uploaded logs number after 40s: ${logs_num}
	Should Be True	${logs_num} >= 1
	...    msg=Agent is not uploading logs immediately! Should be at least 1 after ~ 40s. Actual number:${logs_num}.

	Press key.enter 1 Times
	Check If The Agent Is Ready
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num2}=	Get Length	${run_logs}
	Log To Console	Number of logs at the end of the test: ${logs_num2}
	Log To Console	This number should be just bigger than the previos one: ${logs_num}. If not the agent stopped uploading logs after 40s.
	Should Be True	${logs_num2} > ${logs_num}
	...    msg=Agent did not continue to uploud logs after test is finished! Should be greater than previous number:${logs_num}. Actual number:${logs_num2}.

	[Teardown]	Run Keywords
	...    Remove File	${global_path}${/}${robotname}		AND
	...    Remove File	${global_path}${/}${scenarioname}	AND
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove Directory		${run_result_dirs}[0]	recursive=${True}

Verify If Upload logs=Error Only Uploads Logs As Soon As Robot Finishes Only When Robot Fails
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${scenarioname}=	Set Variable	error_only.rfs
	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${scenarioname}
	${robotname}=		Set Variable	error_only.robot
	${robotfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${robotname}

	Copy File	${scenariofile}		${global_path}
	Copy File	${robotfile}		${global_path}
	@{mngr_options}=	Set Variable	-s	${scenariofile}	-d	${results_dir}
	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Log To Console	Started run, now wait 65s.
	Sleep	65	#rampup=15 run=60
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_error_only*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num}=	Get Length	${run_logs}
	Log To Console	Uploaded logs number after 65s: ${logs_num}
	Should Be True	${logs_num} >= 1
	...    msg=Agent is not uploading logs on error only! Should be at least 1 after ~ 65s. Actual number:${logs_num}.
	Should Be True	${logs_num} <= 15
	...    msg=Agent is uploading every logs but should upload only fail ones! Should be max 15 after ~ 65s. Actual number:${logs_num}.

	Press key.enter 1 Times
	Check If The Agent Is Ready
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num2}=	Get Length	${run_logs}
	Log To Console	Number of logs at the end of the test: ${logs_num2}
	Log To Console	This number should be at least 30 because those that fail are unlikely to surpass 20 + the second test case that just sleep for 5s.
	Should Be True	${logs_num2} > 30
	...    msg=Agent did not continue to uploud logs after test is finished! Should be at least 30. Actual number:${logs_num2}.

	[Teardown]	Run Keywords
	...    Remove File	${global_path}${/}${robotname}		AND
	...    Remove File	${global_path}${/}${scenarioname}	AND
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove Directory		${run_result_dirs}[0]	recursive=${True}

Verify If Upload logs=All Deferred Doesn't Upload Any Logs During the Test
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #91
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600								AND
	...    Set Global Filename And Default Save Path	${robot_data}[0]

	${scenarioname}=	Set Variable	all_deferred.rfs
	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${scenarioname}
	${robotname}=		Set Variable	all_deferred.robot
	${robotfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#91${/}${robotname}

	Copy File	${scenariofile}		${global_path}
	Copy File	${robotfile}		${global_path}
	@{mngr_options}=	Set Variable	-s	${scenariofile}	-d	${results_dir}
	Open Manager GUI	${mngr_options}
	Open Agent
	Check If The Agent Is Ready
	Click Tab	Plan
	Click Button	runplay

	Log To Console	Started run, now wait 60s.
	Sleep	60	#rampup=15 run=50
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_all_deferred*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	${logs_dir_num}=	Get Length	${logs_dir}
	IF  ${logs_dir_num} == 0
		Log To Console	Manager did not create Logs directory after 60s and this is expected.
	ELSE
		@{run_logs}=	List Directories In Directory	${logs_dir}[0]
		${logs_num}=	Get Length	${run_logs}
		Log To Console	Uploaded logs number after 40s: ${logs_num}
		Length Should Be	${run_logs}		0	msg=Agent uploaded logs but should not. Should be 0 logs. Actual number:${logs_num}.
	END

	Press key.enter 1 Times
	Check If The Agent Is Ready
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	pattern=*_all_deferred*	absolute=${True}
	Log To Console	${\n}All run result directories: ${run_result_dirs}${\n}
	@{logs_dir}=	List Directories In Directory	${run_result_dirs}[0]	absolute=${True}
	@{run_logs}=	List Directories In Directory	${logs_dir}[0]
	${logs_num2}=	Get Length	${run_logs}
	Log To Console	Number of logs at the end of the test: ${logs_num2}
	Should Be True	${logs_num2} > 10
	...    msg=Agent did not continue to uploud logs after test is finished! Should be at least 10. Actual number:${logs_num2}.

	[Teardown]	Run Keywords
	...    Remove File	${global_path}${/}${robotname}		AND
	...    Remove File	${global_path}${/}${scenarioname}	AND
	...    Stop Agent							AND
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Remove Directory		${run_result_dirs}[0]	recursive=${True}

Verify Result Name - Test Defaults
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #154  Issue #154-GUI
	${testkey}= 	Set Variable 		resultnamemode
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}default.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}Issue-#154-GUI-TD.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	${EMPTY} 	console=True
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore}
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Selected Option Should Be 	Default
	Click Label With Horizontal Offset 	result_name 	100
	Select Option 	Documentation
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][${testkey}] 	doco
	Log 	Documentation 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Selected Option Should Be 	Documentation
	Click Label With Horizontal Offset 	result_name 	100
	Select Option 	Information
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][${testkey}] 	info
	Log 	Information 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Selected Option Should Be 	Information
	Click Label With Horizontal Offset 	result_name 	100
	Select Option 	Keyword
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][${testkey}] 	kywrd
	Log 	Keyword 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Selected Option Should Be 	Keyword
	Click Label With Horizontal Offset 	result_name 	100
	Select Option 	KeywordArgs
	Click Dialog Button 	ok
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[Script Defaults] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[Script Defaults][${testkey}] 	kywrdargs
	Log 	Keyword & Argsuments 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	runsettings
	Selected Option Should Be 	KeywordArgs
	Click Label With Horizontal Offset 	result_name 	100
	Select Option 	Default
	Click Dialog Button 	ok
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2}
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Log 	Default 	console=True
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify Result Name - Test Row
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #154  Issue #154-GUI
	${testkey}= 	Set Variable 		resultnamemode
	${sourcefile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}default.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#154${/}Issue-#154-GUI-TR.rfs
	Copy File 	${sourcefile} 	${scenariofile}
	Log 	scenariofile: ${scenariofile} 	console=True

	${scenariofilebefore}= 		Read Ini File 	${scenariofile}
	Log 	scenariofilebefore: ${scenariofilebefore}
	Dictionary Should Not Contain Key 	${scenariofilebefore} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofilebefore}[1] 	${testkey}

	@{mngr_options}= 	Create List 	-s 	${scenariofile}
	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Selected Option Should Be 	Default
	Click Label With Vertical Offset 	result_name 	20
	Select Option 	Documentation
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	doco
	Log 	Documentation 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Selected Option Should Be 	Documentation
	Click Label With Vertical Offset 	result_name 	20
	Select Option 	Information
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	info
	Log 	Information 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Selected Option Should Be 	Information
	Click Label With Vertical Offset 	result_name 	20
	Select Option 	Keyword
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	kywrd
	Log 	Keyword 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Selected Option Should Be 	Keyword
	Click Label With Vertical Offset 	result_name 	20
	Select Option 	KeywordArgs
	Test Group Save Settings
	Click Button 	runsave

	Run Keyword		Close Manager GUI ${platform}

	${scenariofileafter1}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter: ${scenariofileafter1}
	Dictionary Should Not Contain Key 	${scenariofileafter1} 	Script Defaults
	Dictionary Should Contain Key 	${scenariofileafter1}[1] 	${testkey}
	Should Be Equal As Strings 	${scenariofileafter1}[1][${testkey}] 	kywrdargs
	Log 	Keyword & Argsuments 	console=True

	Open Manager GUI 		${mngr_options}
	Click Button	trsettings
	Selected Option Should Be 	KeywordArgs
	Click Label With Vertical Offset 	result_name 	20
	Select Option 	Default
	Test Group Save Settings
	Click Button 	runsave

	${scenariofileafter2}= 		Read Ini File 	${scenariofile}
	Log 	scenariofileafter2: ${scenariofileafter2}
	Dictionary Should Not Contain Key 	${scenariofileafter2} 	Script Defaults
	Dictionary Should Not Contain Key 	${scenariofileafter2}[1] 	${testkey}
	Log 	Default 	console=True
	[Teardown] 	Run Keyword		Close Manager GUI ${platform}

Verify That Time Gets Correctly Validated For Schelduled Start
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600 	AND
	...    Open Manager GUI

	VAR 	@{start_times} 			2:56:30   1:50:2    17:5:1  8:3:12     7:43      53:9      12::      :38:      ::42
	VAR 	@{updated_start_times}	02:56:30  01:50:02  17:05:01  08:03:12  07:43:00  53:09:00  12:00:00  00:38:00  00:00:42
	${len}		Get Length	${start_times}

	Click Button	runschedule
	Click RadioBtn	default
	Click Label With Horizontal Offset	schedule_time	100
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Double Click
	END
	FOR  ${i}  IN RANGE  0  ${len}
		Evaluate	clipboard.copy("${start_times}[${i}]")	modules=clipboard
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.v
		ELSE
			Press Combination	KEY.ctrl		KEY.v
		END
		Press key.tab 1 Times
		Sleep	1
		Click Label With Horizontal Offset	schedule_time	100
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Sleep	1
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.c
		ELSE
			Press Combination	KEY.ctrl		KEY.c
		END
		${copied_converted_start_time_value}=		Evaluate	clipboard.paste()	modules=clipboard
		Should Be Equal 	${updated_start_times}[${i}]	${copied_converted_start_time_value}
		...    msg=The "Schedule Time" did not convert to the time as expected [ Expected != Converted ]

	END

	[Teardown]	Run Keywords	Close Manager GUI ${platform}

Verify Schedule Date And Time Are Always In the Future
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600 	AND
	...    Open Manager GUI

	Click Button	runschedule
	Click RadioBtn	default
	${current_time}=	Get Current Date	result_format=%H:%M:%S

	Click Label With Horizontal Offset	schedule_time	100
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Double Click
	END
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.c
	ELSE
		Press Combination	KEY.ctrl		KEY.c
	END
	${copied_start_time_value}= 	Evaluate	clipboard.paste()	modules=clipboard
	${time_diff}=	Subtract Date From Date 	${copied_start_time_value} 	${current_time} 	date1_format=%H:%M:%S 	date2_format=%H:%M:%S
	Log To Console	Time diff: ${time_diff} between current time and copied default time from "Schedule Time" filed.
	Should Be True	${time_diff} >= 300 	msg=The Time diff should be at least grater than 5 minutes. Should be in the future.

	Log To Console	Default time: ${copied_start_time_value} this should be always in the future.
	Log To Console	Current time: ${current_time}
	${copied_start_time_value}= 	Get Substring	${copied_start_time_value} 	0	6
	Log To Console	Applied time: ${copied_start_time_value}
	Evaluate	clipboard.copy("${copied_start_time_value}")	modules=clipboard
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.v
	ELSE
		Press Combination	KEY.ctrl		KEY.v
	END
	Sleep	2
	Press key.tab 2 Times

	Click Label With Horizontal Offset	schedule_date	100
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Double Click
	END
	IF  "${platform}" == "macos"
		Press Combination	KEY.command 	KEY.c
	ELSE
		Press Combination	KEY.ctrl		KEY.c
	END
	${current_date}=	Get Current Date	result_format=%Y-%m-%d
	${copied_converted_start_date_value}=		Evaluate	clipboard.paste()	modules=clipboard
	Log To Console	Converted date: ${copied_converted_start_date_value} should be the same as today's date.
	Should Be Equal 	${current_date} 	${copied_converted_start_date_value}
	...    msg=The "Schedule Date" did not convert to the current date [ Current Date != Converted ]

	Click Dialog Button 	ok
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Remaining" for scheduled start.

	[Teardown]	Run Keywords	Close Manager GUI ${platform}

Verify That When Time Is Entered In the Past It Becomes the Next Day
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600 	AND
	...    Open Manager GUI

	Click Button	runschedule
	Click RadioBtn	default
	Click Label With Horizontal Offset	schedule_time	100
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Double Click
	END
	${current_time}=	Get Current Date	result_format=%H:%M:
	${new_time}=	Subtract Time From Date 	${current_time} 	120 		date_format=%H:%M: 	result_format=%H:%M:
	Log To Console	Current time: ${current_time}
	Log To Console	Applied time that is in the past: ${new_time}
	Evaluate	clipboard.copy("${new_time}")	modules=clipboard
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.v
	ELSE
		Press Combination	KEY.ctrl		KEY.v
	END
	Sleep	2
	Press key.tab 2 Times

	Click Label With Horizontal Offset	schedule_date	100
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Double Click
	END
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.c
	ELSE
		Press Combination	KEY.ctrl		KEY.c
	END
	${current_date}=	Get Current Date	result_format=%Y-%m-%d
	${next_date}=		Add Time To Date 	${current_date} 	1 day 		date_format=%Y-%m-%d 	result_format=%Y-%m-%d
	${copied_converted_start_date_value}=		Evaluate	clipboard.paste()	modules=clipboard
	Log To Console	Converted time: ${copied_converted_start_date_value}
	Should Be Equal 	${next_date} 	${copied_converted_start_date_value}
	...    msg=The "Schedule Date" did not convert to the next date [ Next Date != Converted ]

	Click Dialog Button 	ok
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Remaining" for scheduled start.

	[Teardown]	Run Keywords	Close Manager GUI ${platform}

Verify Test Doesn't Start Until Scheduled To Start And Will Start After the Time Has Elapsed
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Run Keywords
	...    Set INI Window Size		1200	600 	AND
	...    Open Agent

	${current_time}=	Get Current Date	result_format=%H:%M:%S
	${new_time}=	Add Time To Date 	${current_time} 	105 		date_format=%H:%M:%S 	result_format=%H:%M:%S
	${scenariofile}=	Normalize Path	${CURDIR}${/}testdata${/}Issue-#89${/}Issue-#89.rfs
	VAR 	@{mngr_options} 	-s 	${scenariofile} 	-t 	${new_time}

	Open Manager GUI	${mngr_options}
	${status}=	Run Keyword And Return Status	Wait For	manager_${platform}_button_stoprun.png	timeout=30
	Run Keyword If	${status}	Fail
	...    msg=The Manager started script before the scheduled start-up!
	Log To Console	Scenario should start soon.
	${status}=	Run Keyword And Return Status	Wait For	manager_${platform}_button_stoprun.png	timeout=60
	Run Keyword If	not ${status}	Fail
	...    msg=The Manager did not started script after the scheduled time has elapsed!

	[Teardown]	Run Keywords
	...    Run Keyword		Close Manager GUI ${platform}	AND
	...    Stop Agent

Verify the Start Time Is Displayed On the Plan Screen
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Set INI Window Size		1200	600

	${current_time}=	Get Current Date	result_format=%H
	IF  '${current_time}' == '${3}'
		VAR 	${scheduled_time}	15:00:00
		VAR 	${expected_time_image}	15_00_00
	ELSE
		VAR 	${scheduled_time}	3:00:00
		VAR 	${expected_time_image}	3_00_00
	END
	VAR		@{mngr_options}		-t 	${scheduled_time}

	Open Manager GUI	${mngr_options}
	Take A Screenshot
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_${expected_time_image}.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed "${scheduled_time}" for scheduled start.

	[Teardown]	Run Keyword 	Close Manager GUI ${platform}

Verify the Remaining Time Is Displayed On the Plan Screen
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Set INI Window Size		1200	600

	${current_time}=	Get Current Date	result_format=%H:%M:%S
	#adding 10m:20s
	${new_time}=	Add Time To Date 	${current_time} 	680 		date_format=%H:%M:%S 	result_format=%H:%M:%S
	VAR		@{mngr_options}		-t 	${new_time}

	Open Manager GUI	${mngr_options}
	Take A Screenshot
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed "Remaining" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_10_00.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't displayed "10:00" for scheduled start.

	[Teardown]	Run Keyword 	Close Manager GUI ${platform}

Verify That the Start Time And Time Remaining Are Removed From Plan Screen When Scheduled Start Is Disabled
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #89
	[Setup]	Set INI Window Size		1200	600

	${current_time}=	Get Current Date	result_format=%H:%M:%S
	#adding 10m:20s
	${new_time}=	Add Time To Date 	${current_time} 	620 		date_format=%H:%M:%S 	result_format=%H:%M:%S
	VAR		@{mngr_options}		-t 	${new_time}

	Open Manager GUI	${mngr_options}
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Start Time" for scheduled start.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${20}
	Run Keyword If	not ${status}	Fail	msg=Manager didn't set a "Remaining" for scheduled start.

	Log To Console	Disabling Scheduled Start
	Click Button	runschedule
	Click RadioBtn	default
	Click Dialog Button 	ok
	Sleep 	1
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_start_time.png 	timeout=${10}
	Run Keyword If	${status}	Fail	msg=Manager didn't unset a "Start Time" for scheduled start after disabling it.
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_label_remaining.png 	timeout=${10}
	Run Keyword If	${status}	Fail	msg=Manager didn't unset a "Remaining" for scheduled start after disabling it.

	[Teardown]	Run Keywords	Close Manager GUI ${platform}

Check Application Icon or Desktop Shortcut in GUI
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	# ${result}= 	Run 	${cmd_agent} -c ICON
	# Log 		${result}

	${result}= 	Run 	${cmd_manager} -g 6 -c ICON
	Log 		${result}
	Sleep    5

	Navigate to and check Desktop Icon

	[Teardown]	Type 	KEY.ESC 	KEY.ESC 	KEY.ESC


#
