*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Agent Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Agent

Agent Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME
