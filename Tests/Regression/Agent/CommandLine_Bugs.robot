*** Settings ***
Resource 	CommandLine_Common.robot

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
	${result}= 	Query Result DB 	${dbfile} 	Select Name from ResultSummary;
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from ResultSummary;
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
	${result}= 	Query Result DB 	${dbfile} 	Select Name from ResultSummary;
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from ResultSummary;
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
