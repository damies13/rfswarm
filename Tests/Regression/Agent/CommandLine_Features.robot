*** Settings ***
Resource 	CommandLine_Common.robot

*** Test Cases ***
Agent Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	${result}= 	Run 	rfswarm-agent -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Agent

Agent Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -h
	${result}= 	Run 	rfswarm-agent -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME