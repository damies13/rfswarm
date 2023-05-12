*** Settings ***
Library 	OperatingSystem
Library 	Process

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/Images
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	Start Process 	python3 	${pyfile} 	-g 	5    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

GUI Runs and Closes
	[Tags]	windows-latest
	Set Suite Variable    ${platform}    windows
	Set Confidence		0.9
	Start Process 	python3 	${pyfile}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	Start Process 	python3 	${pyfile}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Close GUI
	[Tags]	windows-latest		ubuntu-latest
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	${process} 	timeout=60
	${running}= 	Is Process Running 	${process}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Fail
	END

Close GUI
	[Tags]	macos-latest
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		manager_${platform}_menu_python3.png
	Click Image		manager_${platform}_button_closewindow.png
	Take A Screenshot
	${result}= 	Wait For Process 	${process} 	timeout=60
	${running}= 	Is Process Running 	${process}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Fail
	END


Intentional Fail
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
	...								Ensure this is commented out before release or pull request
	Fail

*** Keywords ***
