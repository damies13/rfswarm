*** Settings ***
Test Tags       Basic 	GUI

Resource 	GUI_Common.robot

Library 	OperatingSystem
Library 	Process
Library 	String

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

*** Variables ***
${default_image_timeout} 	${120}
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm-manager
${IMAGE_DIR} 	${CURDIR}/Images/file_method
${pyfile}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process}		None

*** Test Cases ***
Open GUI
	[Tags]	macos-latest
	# Press Escape and move mouse because on linux the screen save had kicked in
	Press Combination 	Key.esc
	Wiggle Mouse

	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}Open_GUI_stdout.txt 	stderr=${OUTPUT DIR}${/}Open_GUI_stderr.txt
	Set Test Variable 	$process 	${process}
	# Sleep 	10 			# not needed now we wait for the agents tab to be visible
	Set Screenshot Folder 	${OUTPUT DIR}

	Handle Donation Reminder

	${img}=	Set Variable		manager_${platform}_tab_agents.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

Open GUI
	[Tags]	windows-latest
	# Press Escape and move mouse because on linux the screen save had kicked in
	Press Combination 	Key.esc
	Wiggle Mouse

	Set Suite Variable    ${platform}    windows
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}Open_GUI_stdout.txt 	stderr=${OUTPUT DIR}${/}Open_GUI_stderr.txt
	Set Test Variable 	$process 	${process}
	# Sleep 	10 			# not needed now we wait for the agents tab to be visible
	Set Screenshot Folder 	${OUTPUT DIR}

	Handle Donation Reminder

	${img}=	Set Variable		manager_${platform}_tab_agents.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

Open GUI
	[Tags]	ubuntu-latest
	# Press Escape and move mouse because on linux the screen save had kicked in
	Press Combination 	Key.esc
	Wiggle Mouse

	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}Open_GUI_stdout.txt 	stderr=${OUTPUT DIR}${/}Open_GUI_stderr.txt
	Set Test Variable 	$process 	${process}
	# Sleep 	10 			# not needed now we wait for the agents tab to be visible
	Set Screenshot Folder 	${OUTPUT DIR}

	Handle Donation Reminder

	${img}=	Set Variable		manager_${platform}_tab_agents.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

Select Run Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Tab 	 Run
	Sleep 	5

Select Agents Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Tab 	 Agents
	Sleep 	5

Select About Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Tab 	 About
	Sleep 	5

Select Plan Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Click Tab 	 Plan
	Sleep 	5

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
	Kill Manager If Still Running

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
	Kill Manager If Still Running

# Intentional Fail
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
# 	...								Ensure this is commented out before release or pull request
# 	Fail


*** Keywords ***
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
