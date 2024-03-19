*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Robot Version
	[Documentation] 	Logs the robot framework version used
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Robot_Version} =	Evaluate	robot.__version__ 	modules=robot
	Log 	${\n}Robot Version: ${Robot_Version} 	console=True

Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

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
