*** Settings ***
Library 	Collections
Library 	String
Resource 	GUI_Common.robot
Suite Setup 	Set Platform

*** Variables ***
@{run_robots}
@{run_times_in_s}	#delay,		rump-up,	time
@{robot_data}=	Example Test Case	example.robot
@{row_settings_data}=	BuiltIn,String,OperatingSystem,perftest,Collections
...    		-v var:examplevariable
...    		True
${scenario_name}=	test_scenario
${scenario_content}

*** Test Cases ***
Insert Example Data To Manager
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Set INI Window Size		1200	600
	Open Manager GUI
	Set Global Filename And Default Save Path	${robot_data}[1]
	Create Robot File

	Click Button	runaddrow
	Click
	FOR  ${i}  IN RANGE  1  4
		Sleep	2
		FOR  ${j}  IN RANGE  1  5
			Take A Screenshot	#delete later
			IF 	"${platform}" == "macos" and '${j}' == '1'
				Click Button	default_robots
				Take A Screenshot	#delete later
			ELSE
				Click Tab 1 Times
			END
			IF  '${j}' == '1' 
				Append To List	${run_robots}	${i}${j}${i}
				Type	${i}${j}${i}
			ELSE
				Type	00:${i}${j}:${i}${j}
				${time_in_s}=	Evaluate	str(${i}${j} * 60 + ${i}${j})
				Append To List	${run_times_in_s}	${time_in_s}
				
			END
			
		END
		Click Tab 2 Times
		Take A Screenshot	#delete later
		Click Button	selected_runscriptrow
		Select Robot File	@{robot_data}
		Take A Screenshot	#delete later
		Click Button	selected_select_test_case
		Take A Screenshot	#delete later
		Click Button	select_example
		Click Tab 2 Times
		Take A Screenshot	#delete later
		Click Button	selected_runsettingsrow
		Change Test Group Settings		@{row_settings_data}
		Take A Screenshot	#delete later
		Click Tab 1 Times
		Take A Screenshot	#delete later
	END

Save Example Data To Scenario
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Click Button	runsave
	Save Scenario File	${scenario_name}
	Run Keyword		Close Manager GUI ${platform}

Set Scenario File Content And Show Example Data
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Set Global Filename And Default Save Path	${robot_data}[1]
	${scenario_content}=	Get scenario file content	${scenario_name}
	${scenario_content}=	Split String	${scenario_content}
	Set Suite Variable		${scenario_content} 	${scenario_content}

	Log		${scenario_name}.rfs
	Log		${scenario_content}
	Log		${run_robots}
	Log		${run_times_in_s}
	Log		${robot_data}
	Log		${row_settings_data}

Verify Scenario File Robots
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content}		${row}
		Log		${row}

		${robots_offset}		Set Variable	${i + 1}
		Should Be Equal		robots	${scenario_content}[${robots_offset}]
		Should Be Equal		${run_robots}[${rows - 1}]	${scenario_content}[${robots_offset + 2}]
	END

Verify Scenario File Times
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content}		${row}
		Log		${row}
		${time_indx}=	Evaluate	${rows - 1}*3

		${delay_offset}		Set Variable	${i + 4}
		Should Be Equal		delay	${scenario_content}[${delay_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx}]		${scenario_content}[${delay_offset + 2}]

		${rampup_offset}		Set Variable	${delay_offset + 3}
		Should Be Equal		rampup	${scenario_content}[${rampup_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx + 1}]		${scenario_content}[${rampup_offset + 2}]

		${run_offset}		Set Variable	${rampup_offset + 3}
		Should Be Equal		run		${scenario_content}[${run_offset}]
		Should Be Equal		${run_times_in_s}[${time_indx + 2}]		${scenario_content}[${run_offset + 2}]
	END

Verify Scenario File Robot Data
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content}		${row}
		Log		${row}

		${test_offset}		Set Variable	${i + 13}
		Should Be Equal		test	${scenario_content}[${test_offset}]
		${test_name}=	Catenate	
		...    ${scenario_content[${test_offset + 2}]}	
		...    ${scenario_content[${test_offset + 3}]}	
		...    ${scenario_content[${test_offset + 4}]}
		Should Be Equal		${robot_data}[0]	${test_name}

		${script_offset}		Set Variable	${i + 18}
		Should Be Equal		script	${scenario_content}[${script_offset}]
		Should Be Equal		${robot_data}[1]	${scenario_content}[${script_offset + 2}]
	END

Verify Scenario File Settings
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1

	FOR  ${rows}  IN RANGE  1	4
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content}		${row}
		Log		${row}

		${exlibraries_offset}		Set Variable	${i + 21}
		Should Be Equal		excludelibraries	${scenario_content}[${exlibraries_offset}]
		Should Be Equal		${row_settings_data}[0]		${scenario_content}[${exlibraries_offset + 2}]

		${robot_options_offset}		Set Variable	${i + 24}
		Should Be Equal		robotoptions	${scenario_content}[${robot_options_offset}]
		${robot_options}=	Catenate	
		...    ${scenario_content[${robot_options_offset + 2}]}	
		...    ${scenario_content[${robot_options_offset + 3}]}
		Should Be Equal		${row_settings_data}[1]		${robot_options}

		${repeater_offset}		Set Variable	${i + 28}
		Should Be Equal		testrepeater	${scenario_content}[${repeater_offset}]
		Should Be Equal		${row_settings_data}[2]		${scenario_content}[${repeater_offset + 2}]
	END

Chceck That The Scenario File Opens Correctly
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Open Manager GUI
	Set Global Filename And Default Save Path	${robot_data}[1]
	Click Button	runsave
	${scenario_content_reopened}=	Get scenario file content	${scenario_name}
	${scenario_content_reopened}=	Split String	${scenario_content_reopened}
	Log		${scenario_content}
	Log		${scenario_content_reopened}
	Should Be Equal		${scenario_content}		${scenario_content_reopened}	msg=Scenario files are not equal!

Clean Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	Run Keyword		Close Manager GUI ${platform}
	Set Global Filename And Default Save Path	${robot_data}[1]
	Delete Robot File
	Delete Scenario File	${scenario_name}