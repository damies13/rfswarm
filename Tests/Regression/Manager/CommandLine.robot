*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Manager Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version

Manager Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME
