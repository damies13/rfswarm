*** Settings ***
Library 	OperatingSystem
Library 	Process

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/Images
${pyfile}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	Start Process 	python3 	${pyfile} 	-g 	5    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

GUI Runs and Closes
	[Tags]	windows-latest
	Set Suite Variable    ${platform}    windows
	Set Confidence		0.9
	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	Manager
	Should Be Equal As Integers 	${result.rc} 	0


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Select Run Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Run Tab

*** Keywords ***
Click Run Tab
	Wait For 	Run Tab 	 timeout=10
	@{coordinates}= 	Locate		Run Tab
	Click Image		Run Tab
	Take A Screenshot
