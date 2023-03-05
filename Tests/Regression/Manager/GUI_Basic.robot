*** Settings ***
Library 	OperatingSystem
Library 	Process

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/img
${pyfile}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.8
	Start Process 	python3 	${pyfile} 	-g 	5    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

GUI Runs and Closes
	[Tags]	windows-latest
	Set Suite Variable    ${platform}    windows
	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Select Run Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Run Tab

*** Keywords ***
Click Run Tab
	Wait For 	manager_${platform}_run_tab.png 	 timeout=10
	@{coordinates}= 	Locate		manager_${platform}_run_tab.png
	Click Image		manager_${platform}_run_tab.png
	Take A Screenshot
