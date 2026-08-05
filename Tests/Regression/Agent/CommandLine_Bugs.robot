*** Settings ***
Resource 	../../Resources/CommandLine/Agent/CommandLine_Agent.resource
Resource 	../../Resources/Business/Agent/common.resource

Resource 	../../Resources/Common/RFS_code.resource


Suite Setup 	Common.Basic Suite Initialization Agent

Test Timeout 	10 minutes

*** Test Cases ***
Exclude Libraries With Spaces
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #171 	Issue #177
	Show Test Information

	GROUP  Set Test Variables
		${scenario_path}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
		Log to console 	scenariofile: ${scenario_path}
	END

	Run Agent with Default Settings
	Run Manager with "${scenario_path}" and "${RESULTS_DIR}"
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process
	Stop Agent
	Show Manager Logs
	Show Agent Logs

	GROUP 	Verify Results Database contains expected results
		${dbfile}= 	Find Result DB
		${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
		Should Be True 	${result[0][0]} > 0
		Should Be Equal As Numbers 	${result[0][0]} 	4
	END

Run agent with -x (xml mode)
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #180
	Show Test Information

	GROUP  Set Test Variables
		${scenario_path}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
		VAR 	${url} 	http://localhost:8138
		VAR 	@{agnt_options}= 	-g  1  -m  ${url}  -x
	END

	Run Agent CLI 	@{agnt_options}
	Run Manager with "${scenario_path}" and "${RESULTS_DIR}"
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process
	Stop Agent
	Show Agent Logs
	Show Manager Logs

	GROUP 	Verify Results Database contains expected results
		${dbfile}= 	Find Result DB 	directory=${results_dir} 	result_pattern=*_Issue171*
		${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
		Should Be True	${result[0][0]} > 0
		Should Be Equal As Numbers	${result[0][0]} 	4
	END

Check If The Not Buildin Modules Are Included In The Agent Setup File
	[Documentation] 	This test case is deprecated due to the new implementation of the pyproject.toml
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123 	depracated
	GROUP 	Set Test Variables
		${imports} 		Get Modules From Program .py File That Are Not BuildIn
		...    ${CURDIR}..${/}..${/}..${/}..${/}rfswarm_agent${/}rfswarm_agent.py
		${requires} 	Get Install Requires From Setup File
		...    ${CURDIR}..${/}..${/}..${/}..${/}setup-agent.py
	END

	GROUP 	Show Agent's python imports and requirements
		Log 	${imports}
		Log 	${requires}
	END
	Check if modules are in the Agent setup file 	${imports} 	${requires}

Verify If Agent Runs With Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	GROUP 	Run Agent first time to create INI file
		Run Agent with Default Settings
		Sleep 	5s
		Ensure Agent is running and then terminate
		Check if Agent INI file is not empty
		Check Agent Logs
	END
	GROUP 	Run Agent the second time with the INI file created from the first run.
		Run Agent with Default Settings
		Sleep 	5s
		Ensure Agent is running and then terminate
		Check Agent Logs
	END

	[Teardown] 	Reset Agent INI file

Verify If Agent Runs With No Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	Remove Agent INI File
	GROUP 	Run Agent with no existing ini file
		Run Agent with Default Settings
		Sleep	5
		Ensure Agent is running and then terminate
		Check Agent logs
	END

	[Teardown] 	Reset Agent INI file

Verify If Agent Runs With Existing INI File From Previous Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	Remove Agent INI File
	Replace Agent INI File 	${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmAgent.ini

	GROUP 	Run Agent with existing ini file
		Run Agent with Default Settings
		Sleep	5
		Ensure Agent is running and then terminate
		Check Agent logs
	END

	[Teardown] 	Reset Agent INI file

Verify If Agent Name Has Been Transferred To the Manager (-a command line switch)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	GROUP 	Set Test Variables
		VAR 	${test_dir}= 		${OUTPUT_DIR}${/}testdata${/}Issue-#100${/}command_line
		VAR 	${result_path}= 	${test_dir}
		VAR 	${dbfile}= 			${test_dir}${/}PreRun${/}PreRun.db
		VAR 	${agent_name}= 		Issue-#100AGENTNAME
		VAR 	${query}= 			SELECT * FROM AgentList WHERE AgentName='${agent_name}'
	END

	Create Directory 	${test_dir}
	Run Agent with custom name 	${agent_name}
	Run Manager with Custom Result Directory 	${result_path}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager

	GROUP 	Verify Manager's PreRun data base.
		Wait Until the Query Is Not Empty 		${dbfile}  sql=SELECT * FROM AgentList
		${query_result} 	Query Result DB 	${dbfile}  ${query}
		${len}= 	Get Length 	${query_result}
		Should Be True 	${len} > 0
		...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}
	END

	[Teardown] 	Stop Agent and Manager

Verify If Agent Name Has Been Transferred To the Manager (ini file)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	GROUP 	Set Test Variables
		VAR 	${test_dir}= 		${CURDIR}${/}testdata${/}Issue-#100${/}ini_file
		VAR 	${results_dir}= 	${test_dir}
		VAR 	${dbfile}= 			${test_dir}${/}PreRun${/}PreRun.db
		VAR 	${agent_name}= 		Issue-100AGENTNAME
		VAR 	${ini_file}= 		${CURDIR}${/}testdata${/}Issue-#100${/}RFSwarmAgent.ini
		VAR 	${query}= 			SELECT * FROM AgentList WHERE AgentName='${agent_name}'
	END

	Create Directory 	${test_dir}
	Run Agent with custom INI file 	${ini_file}
	Run Manager with Custom Result Directory 	${results_dir}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager

	GROUP 	Verify Manager's PreRun data base.
		Wait Until the Query Is Not Empty 		${dbfile}  sql=SELECT * FROM AgentList
		${query_result} 	Query Result DB 	${dbfile}  ${query}
		${len}= 	Get Length 	${query_result}
		Should Be True 	${len} > 0
		...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}
	END

	[Teardown] 	Stop Agent and Manager

Verify listener doesn't generate KeyError when using inject sleep
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #392

	GROUP 	Set Test Variables
		VAR 	${test_dir}= 		${CURDIR}${/}testdata${/}Issue-#392
		VAR 	${scenario_path}= 	${test_dir}${/}Issue-#392.rfs
	END

	Run Agent with Default Settings
	Run Manager with "${scenario_path}" and "${RESULTS_DIR}"
	Wait For Manager Process
	Stop Agent

	@{xmlfiles}= 	Get XML Files From Last Run 	result_pattern=*_Issue-#392

	GROUP 	Check for Errors In Agents Robot Logs
		FOR  ${xmlfile}  IN  @{xmlfiles}
			${root}= 	Parse XML 	${xmlfile}
			${errorcount}= 	Get Element Count 	${root} 		.//errors/msg
			IF 	${errorcount} > 0
				${errors}= 	Get Elements 	${root} 		.//errors/msg
				Log  	errors: ${errors} 	console=true
				VAR 	${ftext} 		${EMPTY}
				FOR 	${error} 	IN 		@{errors}
					${etext} = 	Get Element Text 	${error}
					Log  	error: ${etext}
					VAR 	${ftext} 		${ftext}\n${etext}
				END
				Fail  	errors: ${ftext}
			END
		END
	END

	[Teardown]	Stop Agent and Manager

Verify listener doesn't over inject sleeps
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #394

	GROUP 	Set Test Variables
		VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#394
		VAR 	${scenario_path} 	${test_dir}${/}Issue-#394.rfs
	END

	Run Agent with Default Settings
	Run Manager with "${scenario_path}" and "${RESULTS_DIR}"
	Wait For Manager Process
	Stop Agent

	@{xmlfiles}= 	Get XML Files From Last Run 	result_pattern=*_Issue-#394

	GROUP 	Check Counts Of Injected Sleeps In Agents Robot Logs
		FOR  ${xmlfile}  IN  @{xmlfiles}
			${root}= 	Parse XML 	${xmlfile}
			# //kw[arg[text()='Sleep added by RFSwarm']]
			${inj_sleep_count_1}= 	Get Element Count 	${root} 		.//test[1]//kw[arg = 'Sleep added by RFSwarm']
			Log  	Count of injected sleeps for test 1: ${inj_sleep_count_1} 	console=true
			${inj_sleep_count_2}= 	Get Element Count 	${root} 		.//test[2]//kw[arg = 'Sleep added by RFSwarm']
			Log  	Count of injected sleeps for test 2: ${inj_sleep_count_2} 	console=true

			Should Be Equal As Numbers 		${inj_sleep_count_1} 		${inj_sleep_count_2}
		END
	END

	[Teardown]	Stop Agent and Manager

Run Test Cases With Embedded Variables
	[Tags] 		ubuntu-latest 	macos-latest 	windows-latest 	Issue #156

	GROUP 	Set Test Variables
		VAR 	${test_folder}= 		${CURDIR}${/}testdata${/}Issue-#156
		VAR 	${scenario_name}= 		test_scenario
		VAR 	${results_dir}= 		${test_folder}${/}results
		VAR 	${scenario_path}= 		${test_folder}${/}${scenario_name}.rfs
		VAR 	${robot_test_name}= 	Send GET on API \${endpoint} on \${env}
	END

	Create Directory 	${results_dir}
	Run Agent with Default Settings 	debug_lvl=3
	Run Manager with "${scenario_path}" and "${results_dir}"
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process 	timeout=10min
	Stop Agent

	Check Manager logs
	Check Agent logs

	@{xmlfiles}= 	Get XML Files From Last Run 	result_pattern=*${scenario_name}* 	path=${results_dir}
	GROUP 	Check if embedded variables are present in test cases name after Agent executes them
		FOR  ${xmlfile}  IN  @{xmlfiles}
			${xml_file_content}= 	Get File 	${xml_file}
			Should Contain 		${xml_file_content}  Send GET on API my endpoint on QAENV
			Should Not Contain 	${xml_file_content}  status="FAIL"
			Should Not Contain 	${xml_file_content}  Do Not Use Test Case
		END
	END

	GROUP 	Verify Results Database contains expected results
		VAR 	${query} 	SELECT result_name FROM Summary
		${scenario_DBs}= 	Find Result DB 		directory=${results_dir} 	result_pattern=*${scenario_name}*
		@{query_result}= 	Query Result DB 	${scenario_DBs}  ${query}

		Should Be Equal 	${query_result}[0][0] 	Log Data 1
		Should Be Equal 	${query_result}[1][0] 	Log Data 2
		Should Be Equal 	${query_result}[2][0] 	Log Data 3
	END

	[Teardown] 	Run Keywords
	...    Stop Agent and Manager 	AND
	...    Clear Result Directory 	RES_DIR=${CURDIR}${/}testdata${/}Issue-#156${/}results

*** Keywords ***
Check if modules are in the Agent setup file
	[Arguments] 	${imports} 	${requires}
	FOR  ${i}  IN  @{imports}
		Run Keyword And Continue On Failure
		...    Should Contain	${requires}	${i}
		...    msg="Some modules are not in Agent setup file"
	END
