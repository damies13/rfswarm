*** Settings ***
Library 	OperatingSystem
Library 	Process

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/Images/file_method
${pyfile}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process}		None

*** Test Cases ***
Open GUI
	[Tags]	macos-latest
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	${process}= 	Start Process 	python3 	${pyfile} 	-g 	5    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Test Variable 	$process 	${process}
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI
	[Tags]	windows-latest
	Set Suite Variable    ${platform}    windows
	Set Confidence		0.9
	${process}= 	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Test Variable 	$process 	${process}
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI
	[Tags]	ubuntu-latest
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	${process}= 	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Test Variable 	$process 	${process}
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Select Run Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Run Tab

Close GUI
	[Tags]	windows-latest		ubuntu-latest
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	${process} 	timeout=60
	IF 	${result} is None
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Fail
	END

Close GUI
	[Tags]	macos-latest
	# Press Combination 	Key.esc
	Press Combination 	q 	Key.command
	${result}= 	Wait For Process 	${process} 	timeout=60
	IF 	${result} is None
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Fail
	END


*** Keywords ***
Click Run Tab

	${img}=	Set Variable		manager_${platform}_run_tab.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=10
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Take A Screenshot
