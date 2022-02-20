*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Agent Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version

Agent Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME
