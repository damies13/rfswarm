*** Settings ***
Library 	OperatingSystem

Suite Setup			Clean Up Old Files

*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm

*** Test Cases ***
Robot Version
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Robot_Version} =	Evaluate	robot.__version__ 	modules=robot
	Log to console 	${\n}Robot Version: ${Robot_Version}

Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Manager Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -v
	${result}= 	Run 	${cmd_manager} -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Manager

Manager Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -h
	${result}=	Run 	${cmd_manager} -h
	Log to console 	${\n}${result}
	Should Contain	${result}	IPADDRESS

*** Keywords ***
Clean Up Old Files
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# cleanup previous output
	Log To Console    ${OUTPUT DIR}
	Remove File    ${OUTPUT DIR}${/}*.txt
	Remove File    ${OUTPUT DIR}${/}*.png
	# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*
