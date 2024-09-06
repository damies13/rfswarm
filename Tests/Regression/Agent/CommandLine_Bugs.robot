*** Settings ***
Resource 	CommandLine_Common.robot
Suite Setup 	Set Platform

*** Test Cases ***
Exclude Libraries With Spaces
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #171 	Issue #177
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	@{agnt_options}= 	Create List 	-g 	1 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Log to console 	${CURDIR}
	# ${scenariofile}= 	Normalize Path 	${CURDIR}${/}..${/}..${/}Demo${/}demo.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
	Log to console 	scenariofile: ${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

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
	@{agnt_options}= 	Create List 	-g 	1 	-x 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Log to console 	${CURDIR}
	# ${scenariofile}= 	Normalize Path 	${CURDIR}${/}..${/}..${/}Demo${/}demo.rfs
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#171${/}Issue171.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	${dbfile}= 	Find Result DB
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
	Run Agent
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

	Run Agent
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

	Run Agent
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

	Run Agent
	Sleep	5
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

	[Teardown] 	Run Keywords
	...    Remove File 	${location}${/}RFSwarmAgent.ini 	AND
	...    Run Agent 	AND
	...    Sleep 	3 	AND
	...    Stop Agent

Verify If Agent Name Has Been Transferred To the Manager (-a command line switch)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#100${/}command_line
	VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db
	VAR 	@{agnt_options} 	-a 	Issue-#100AGENTNAME
	VAR 	@{mngr_options} 	-n 	-d 	${test_dir}

	Create Directory 	${test_dir}
	Log To Console	Run Agent with custom agent name.
	Run Agent 	${agnt_options}
	Run Manager CLI 	${mngr_options}
	Sleep	20s
	Stop Agent
	Stop Manager

	Log To Console 	Checking PreRun data base.
	${query_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM AgentList WHERE AgentName='Issue-#100AGENTNAME'
	${len}= 	Get Length 	${query_result}
	Should Be True 	${len} > 0
	...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}

	[Teardown]	Run Keywords	Stop Agent	Stop Manager

Verify If Agent Name Has Been Transferred To the Manager (ini file)
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #100

	VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#100${/}ini_file
	VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db
	VAR 	@{agnt_options} 	-i 	${CURDIR}${/}testdata${/}Issue-#100${/}RFSwarmAgent.ini
	VAR 	@{mngr_options} 	-n 	-d 	${test_dir}

	Create Directory 	${test_dir}
	Log To Console	Run Agent with custom agent name.
	Run Agent 	${agnt_options}
	Run Manager CLI 	${mngr_options}
	Sleep	20s
	Stop Agent
	Stop Manager

	Log To Console 	Checking PreRun data base.
	${query_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM AgentList WHERE AgentName='Issue-#100AGENTNAME'
	${len}= 	Get Length 	${query_result}
	Should Be True 	${len} > 0
	...    msg=Custom Agent name not found in PreRun db. ${\n}Query Result: ${query_result}

	[Teardown]	Run Keywords	Stop Agent	Stop Manager