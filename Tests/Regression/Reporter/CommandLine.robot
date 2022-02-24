*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Reporter Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Reporter

Reporter Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	Excel
