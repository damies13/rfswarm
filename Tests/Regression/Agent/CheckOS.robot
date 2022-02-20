
*** Test Cases ***

Check OS
	${uname}= 	Evaluate 	sys.platform		sys
	Log 	${uname}
	Log to console 	${uname}

Check Dir
	Log to console 	${CURDIR}
	Log to console 	${EXECDIR}

Agent Version
	${result}=	Run Process	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py	-v
	Log to console	${result.stdout}

# Agent Help
	# ${result}=	Run Process	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py	-v	stderr=STDOUT
