*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}


*** Variables ***
${IMAGE_DIR} 	${CURDIR}/Images/file_method
${pyfile_manager}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${pyfile_agent}			${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${process_manager}		None
${process_agent}		None

*** Keywords ***
Set Platform
	# [Arguments]		${ostag}
	Log 	${OPTIONS}
	Log 	${OPTIONS}['include']
	${ostag}= 	Set Variable 	${OPTIONS}['include']

	IF 	${ostag} == macos-latest
		Set Suite Variable    ${platform}    macos
	END
	IF 	${ostag} == windows-latest
		Set Suite Variable    ${platform}    windows
	END
	IF 	${ostag} == ubuntu-latest
		Set Suite Variable    ${platform}    ubuntu
	END

Open Agent
	# [Arguments]		${options}
	${process}= 	Start Process 	python3 	${pyfile_agent}    alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Open Manager GUI
	# [Arguments]		${options}
	Set Confidence		0.9
	${process}= 	Start Process 	python3 	${pyfile_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}
	Sleep 	10
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Close Manager GUI ubuntu
	Close Manager GUI

Close Manager GUI windows
	Close Manager GUI

Close Manager GUI
	[Tags]	windows-latest		ubuntu-latest
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	${process_manager} 	timeout=60
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Fail
	END

Close Manager GUI macos
	[Tags]	macos-latest
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		manager_${platform}_menu_python3.png
	Click Image		manager_${platform}_button_closewindow.png
	Take A Screenshot
	${result}= 	Wait For Process 	${process_manager} 	timeout=60
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Fail
	END

Stop Agent
	${result} = 	Terminate Process		${process_agent}
	Should Be Equal As Integers 	${result.rc} 	0

Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		manager_${platform}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot
