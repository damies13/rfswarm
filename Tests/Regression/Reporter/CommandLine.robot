*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Reporter Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version

Reporter Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME
