*** Settings ***
Library 	OperatingSystem
Library 	Process

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/Images
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

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
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Intentional Fail
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
	...								Ensure this is commented out before release or pull request
	Fail

*** Keywords ***
