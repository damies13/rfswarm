*** Settings ***
# Library 	Process
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
	# ${result}=	Wait For Process	python3	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py	-v
	${result}= 	Run 	python3	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	# Log to console 	${result.stdout}
	Log to console 	${result}

# Agent Help
	# ${result}=	Run Process	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py	-v	stderr=STDOUT
