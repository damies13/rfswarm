*** Settings ***
Library 	OperatingSystem
Library 	Process

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/img

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Set Suite Variable    ${platform}    macos
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py 	-g 	5    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

GUI Runs and Closes
	[Tags]	windows-latest
	Set Suite Variable    ${platform}    windows
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


*** Keywords ***
