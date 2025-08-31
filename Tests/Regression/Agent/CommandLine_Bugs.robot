*** Settings ***
Resource 	resources/CommandLine_Agent.resource
Resource 	../../Common/Directories_and_Files.resource
Resource 	../../Common/INI_PIP_Data.resource
Resource 	../../Common/Logs.resource
Resource 	../../Common/RFS_Components.resource
Resource 	../../Common/RFS_code.resource
Resource 	../../Common/Database.resource

Suite Setup 	Common.Basic Suite Initialization Agent

*** Test Cases ***
Exclude Libraries With Spaces
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #171 	Issue #177
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Run Agent CLI 	-g 	1 	-m 	http://localhost:8138
	Log to console 	${CURDIR}
	# ${scenariofile}= 	Normalize Path 	${CURDIR}${/}..${/}..${/}Demo${/}demo.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
	Log to console 	scenariofile: ${scenariofile}
	Run Manager CLI 	-g 	1 	-s 	${scenariofile} 	-n
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process
	Stop Agent CLI

	${dbfile}= 	Find Result DB
	# Query Result DB 	${dbfile} 	Select * from Results
	# ${result}= 	Query Result DB 	${dbfile} 	Select * from ResultSummary;
	${result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary;
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
	Should Be True	${result[0][0]} > 0
	Should Be Equal As Numbers	${result[0][0]} 	4

Run agent with -x (xml mode)
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #180
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Run Agent CLI 	-g 	1 	-x 	-m 	http://localhost:8138
	Log to console 	${CURDIR}
	# ${scenariofile}= 	Normalize Path 	${CURDIR}${/}..${/}..${/}Demo${/}demo.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
	Log to console 	${scenariofile}
	Run Manager CLI 	-g 	1 	-s 	${scenariofile} 	-d 	${CURDIR}${/}testdata${/}Issue-#171 	-n
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process
	Stop Agent CLI

	${dbfile}= 	Find Result DB 	directory=${CURDIR}${/}testdata${/}Issue-#171 	result_pattern=*_Issue171*
	# Query Result DB 	${dbfile} 	Select * from Results
	# ${result}= 	Query Result DB 	${dbfile} 	Select * from ResultSummary;
	${result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary;
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
	Should Be True	${result[0][0]} > 0
	Should Be Equal As Numbers	${result[0][0]} 	4

Check If The Not Buildin Modules Are Included In The Agent Setup File
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	${imports}	Get Modules From Program .py File That Are Not BuildIn
	...    ${CURDIR}..${/}..${/}..${/}..${/}rfswarm_agent${/}rfswarm_agent.py

	Log	${imports}

	${requires}	Get Install Requires From Setup File
	...    ${CURDIR}..${/}..${/}..${/}..${/}setup-agent.py

	Log	${requires}

	FOR  ${i}  IN  @{imports}
		Run Keyword And Continue On Failure
		...    Should Contain	${requires}	${i}
		...    msg="Some modules are not in Agent setup file"
	END

Verify If Agent Runs With Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Agent Default Save Path
	Run Agent CLI
	Sleep	5
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

	File Should Exist	${location}${/}RFSwarmAgent.ini
	File Should Not Be Empty	${location}${/}RFSwarmAgent.ini
	Log To Console	Running Agent with existing ini file.

	Run Agent CLI
	Sleep	5
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

Verify If Agent Runs With No Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Agent Default Save Path
	Remove File		${location}${/}RFSwarmAgent.ini
	File Should Not Exist	${location}${/}RFSwarmAgent.ini
	Log To Console	Running Agent with no existing ini file.

	Run Agent CLI
	Sleep	5
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

Verify If Agent Runs With Existing INI File From Previous Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Agent Default Save Path
	Remove File		${location}${/}RFSwarmAgent.ini
	File Should Not Exist	${location}${/}RFSwarmAgent.ini
	${v1_0_0_inifile}=		Normalize Path		${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmAgent.ini
	Copy File	${v1_0_0_inifile}		${location}
	File Should Exist	${location}${/}RFSwarmAgent.ini
	File Should Not Be Empty	${location}${/}RFSwarmAgent.ini
	Log To Console	Running Agent with existing ini file.

	Run Agent CLI
	Sleep	5
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

	[Teardown] 	Run Keywords
	...    Remove File 	${location}${/}RFSwarmAgent.ini 	AND
	...    Run Agent CLI 	AND
	...    Sleep 	3 	AND
	...    Stop Agent CLI

Verify If Agent Name Has Been Transferred To the Manager (-a command line switch)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#100${/}command_line
	VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db

	Create Directory 	${test_dir}
	Log To Console	Run Agent CLI with custom agent name.
	Run Agent CLI 		-a 	Issue-#100AGENTNAME
	Run Manager CLI 	-n 	-d 	${test_dir}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager
	Sleep 	30s
	Stop Agent CLI
	Stop Manager CLI

	Log To Console 	Checking PreRun data base.
	${query_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM AgentList WHERE AgentName='Issue-#100AGENTNAME'
	${len}= 	Get Length 	${query_result}
	Should Be True 	${len} > 0
	...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}

	[Teardown]	Run Keywords	Stop Agent CLI	Stop Manager CLI

Verify If Agent Name Has Been Transferred To the Manager (ini file)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#100${/}ini_file
	VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db

	Create Directory 	${test_dir}
	Log To Console	Run Agent CLI with custom agent name.
	Run Agent CLI 		-i 	${CURDIR}${/}testdata${/}Issue-#100${/}RFSwarmAgent.ini
	Run Manager CLI 	-n 	-d 	${test_dir}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager
	Sleep 	30s
	Stop Agent CLI
	Stop Manager CLI

	Log To Console 	Checking PreRun data base.
	${query_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM AgentList WHERE AgentName='Issue-#100AGENTNAME'
	${len}= 	Get Length 	${query_result}
	Should Be True 	${len} > 0
	...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}

	[Teardown]	Run Keywords	Stop Agent CLI	Stop Manager CLI

Run Test Cases With Embedded Variables
	[Tags] 		ubuntu-latest 	macos-latest 	windows-latest 	Issue #156
	[Setup] 	Run Keywords
	...    Create Directory 	${CURDIR}${/}testdata${/}Issue-#156${/}results  AND
	...    Run Agent CLI  -g 3
	
	VAR 	${test_folder} 	${CURDIR}${/}testdata${/}Issue-#156
	VAR 	${scenario_name} 	test_scenario
	VAR 	${robot_test_name} 	Send GET on API \${endpoint} on \${env}
	
	Run Manager CLI  -n  -s  ${test_folder}${/}${scenario_name}.rfs  -d  ${test_folder}${/}results

	Wait Until the Agent Connects to the Manager
	Wait For Manager Process 	timeout=10min
	Stop Agent CLI

	Check Logs 	Manager
	Check Logs 	Agent

	@{scenario_res_dirs}= 	List Directories In Directory 	${test_folder}${/}results  pattern=*${scenario_name}*  absolute=${True}
	@{result_dirs}= 		List Directories In Directory 	${scenario_res_dirs}[0]${/}logs  absolute=${True}

	FOR  ${result_dir}  IN  @{result_dirs}
		@{files}= 	List Files In Directory 	${result_dir}
		Log 	${files}
		# The xml file name is being strangely converted in linux/mac
		@{xml_file}= 	List Files In Directory 	${result_dir}  pattern=*_output.xml  absolute=${True}

		${xml_file_content}= 	Get File 	${xml_file}[0]
		Should Contain 	${xml_file_content}  Send GET on API my endpoint on QAENV
		Should Not Contain 	${xml_file_content}  status="FAIL"
		Should Not Contain 	${xml_file_content}  Do Not Use Test Case
	END

	VAR 	${query} 	SELECT result_name FROM Summary
	@{scenario_DBs}= 	List Files In Directory 	${scenario_res_dirs}[0]  pattern=*.db  absolute=${True}
	@{query_result}= 	Query Result DB 	${scenario_DBs}[0]  ${query}

	Should Be Equal 	${query_result}[0][0] 	Log Data 1
	Should Be Equal 	${query_result}[1][0] 	Log Data 2
	Should Be Equal 	${query_result}[2][0] 	Log Data 3

	[Teardown] 	Run Keywords
	...    Stop Agent CLI  AND  Stop Manager CLI  AND
	...    Clear Result Directory 	RES_DIR=${CURDIR}${/}testdata${/}Issue-#156${/}results
