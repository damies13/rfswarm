*** Settings ***
Library 	OperatingSystem

*** Test Cases ***

Check OS
	${uname}= 	Evaluate 	sys.platform		sys
	Log 	${uname}
	Log to console 	${uname}

Check Dir
	Log to console 	${CURDIR}
	Log to console 	${EXECDIR}

Agent Version
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version

Agent Help
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py	-h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME
