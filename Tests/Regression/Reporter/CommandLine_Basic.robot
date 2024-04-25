*** Settings ***
Resource 	CommandLine_Common.robot

Suite Setup			Clean Up Old Files

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

Reporter Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -v
	${result}= 	Run 	${cmd_reporter} -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Reporter

Reporter Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -h
	${result}= 	Run 	${cmd_reporter} -h
	Log to console 	${\n}${result}
	Should Contain	${result}	Excel
