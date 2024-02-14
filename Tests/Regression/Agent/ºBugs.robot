*** Settings ***
Resource 	ºCommon.robot

*** Test Cases ***
Issue #171
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Run Agent
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}..${/}..${/}Demo${/}demo.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-s 	${scenariofile} 	-n
	Run Manager CLI 	@{mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	stdout_manager.txt
	Show Log 	stdout_agent.txt
