# https://rainmanwy.github.io/robotframework-SikuliLibrary/doc/SikuliLibrary.html
# https://rainmanwy.github.io/robotframework-SikuliLibrary/
# https://github.com/rainmanwy/robotframework-SikuliLibrary

*** Settings ***
# Test Setup        Sikili Setup
Suite Setup       Sikili Setup
# Test Teardown     Stop Remote Server
Suite Teardown    Stop Remote Server
Library           SikuliLibrary
Library			  OperatingSystem

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/img
${SS_DIR} 		${CURDIR}/screenshots
${PrefixOS} 	MacOS
${RFS_Release} 	v0.8.0


*** Test Cases ***
Plan New
	# Make rfswarm Active
	Click New
	Take SS 	Plan 	New
	Click Settings
	Take SS 	Plan 	Test_Settings
	Click Cancel

Filter Rules
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/100u_test.rfs
	Click Settings
	Take SS 	Plan 	Test_Settings_Filter_Rules
	Click Cancel

150 robots 25 per 10 min
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/150 users stepped in groups of 25.rfs
	Take SS 	Plan 	150u_25per10min

saved opened
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/test2.rfs
	Take SS 	Plan 	saved_opened

20 robots delay example
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/Simple_delay.rfs
	Take SS 	Plan 	20u_delay_example

Agents Ready
	Click New
	Click Agents
	Take SS 	Agents 	Ready

About Screen
	Click About
	Take SS 	About 	About

Aborted Run
	Run Keyword And Ignore Error	Click Plan
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/30u5r20m.rfs
	Click Agents
	2 Agents Ready
	Click Plan
	Click Play
	Sleep 	5
	Take SS 	Run 	Start_5s
	Sleep 	55
	Take SS 	Run 	Start_60s
	Click Agents
	Take SS 	Agents 	Running
	Click Run
	Click Stop
	Take SS 	Run 	Bomb_Run
	Sleep 	10
	Click Agents
	Take SS 	Agents 	Stopping
	Click Run
	Click Abort
	Take SS 	Run 	Abort_Dialogue
	Click Yes
	Click Aborted
	Take SS 	Run 	Aborted

Graphs
	Run Keyword And Ignore Error	Click Plan
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/30u5r20m.rfs
	Click Agents
	2 Agents Ready
	Click Plan

	Open Graphs Menu
	Take SS 	Graphs 	Menu
	Click Index 1
	Open Graphs Menu Examples
	Take SS 	Graphs 	Menu_Examples
	Click Index 1

	Click Play
	Sleep 	7m

	Open SS Close New Graph
	Open SS Close Graph 	Agent_Load
	Open SS Close Graph 	Response_Time
	Open SS Close Graph 	Running_Robots


2 Hour Test
	Run Keyword And Ignore Error	Click Plan
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/100u_test_nf.rfs
	Click Agents
	2 Agents Ready
	Click Plan
	Click Play
	Sleep 	18m
	Click Agents
	Take SS 	Agents 	Warning_1
	Sleep 	1m
	Take SS 	Agents 	Warning_2
	Sleep 	1m
	Take SS 	Agents 	Warning_3
	Sleep 	1m
	Take SS 	Agents 	Warning_4
	Sleep 	1m
	Take SS 	Agents 	Warning_5
	Click Run
	Take SS 	Run 	100_Robots
	Sleep 	1h 55m
	Take SS 	Run 	2h
	Wait until screen contain 	rfwasrm_mac_Agents_Uploading_1.png 	1200 	# 20m
	Take SS 	Agents 	Uploading_1
	Sleep 	1m
	Take SS 	Agents 	Uploading_2
	Sleep 	1m
	Take SS 	Agents 	Uploading_3
	Sleep 	1m
	Take SS 	Agents 	Uploading_4
	Sleep 	1m
	Take SS 	Agents 	Uploading_5
	Sleep 	15m
	Click Run
	Take SS 	Run 	Finished




*** Keywords ***
Sikili Setup
	Add Image Path    ${IMAGE_DIR}
	Make rfswarm Active

Take SS
	[Arguments]		${Catagory} 	${Name}
	${screenshotname}= 	Capture Screen
	Copy File 	${screenshotname} 	${SS_DIR}/${PrefixOS}_${Catagory}_${RFS_Release}_${Name}.png



Make rfswarm Active
	Click 	rfwasrm_mac_title_bg.png
	Run Keyword And Ignore Error	Click Plan

Click Plan
	Click	rfwasrm_mac_Plan.png
	Wait until screen contain 	rfwasrm_mac_Play.png	10

Click Run
	Click	rfwasrm_mac_Run.png
	Wait until screen contain 	rfwasrm_mac_RunScreen.png	10

Click Agents
	Click	rfwasrm_mac_Agents.png
	Sleep 	1

Click About
	Click	rfwasrm_mac_About.png
	Sleep 	1

Click New
	Click 	rfwasrm_mac_New.png
	Run Keyword And Ignore Error	Click No
	Click Index 1

Click Play
	Click	rfwasrm_mac_Play.png
	Wait until screen contain 	rfwasrm_mac_RunScreen.png	10

Click Stop
	Click	rfwasrm_mac_Stop.png
	Sleep 	1

Click Abort
	Click	rfwasrm_mac_Abort.png
	Wait until screen contain 	rfwasrm_mac_Abort_Dialogue.png	10

Click Aborted
	Click	rfwasrm_mac_Aborted.png
	Sleep 	1


Click Settings
	Click	rfwasrm_mac_Settings.png
	Wait until screen contain 	rfwasrm_mac_Save.png 	10

Click No
	Wait until screen contain 	rfwasrm_mac_No.png 	10
	Click	rfwasrm_mac_No.png
	Wait Until Screen Not Contain 	rfwasrm_mac_No.png 	10

Click Yes
	Click	rfwasrm_mac_Yes.png
	Wait Until Screen Not Contain 	rfwasrm_mac_Yes.png 	10

Click Cancel
	Click	rfwasrm_mac_Cancel.png
	Wait Until Screen Not Contain 	rfwasrm_mac_Cancel.png 	10

Click Index 1
	Click 	rfwasrm_mac_Index_1.png
	Sleep 	1

Open Scenario
	[Arguments]		${scenario_file}
	Click 	rfwasrm_mac_Open.png
	Run Keyword And Ignore Error	Click No
	Wait until screen contain 	rfwasrm_mac_OpenFile.png 	10
	# "g", Key.META + Key.SHIFT
	# Press Special Key 	"g" 	META + SHIFT
	# Type With Modifiers 	g 	META + SHIFT
	Type With Modifiers 	G 	META
	Wait until screen contain 	rfwasrm_mac_GoToTheFolder.png 	10
	Press Special Key 	DELETE
	# Paste Text 	${scenario_file}
	Input Text 	${EMPTY} 	${scenario_file}
	Press Special Key 	ENTER
	Wait Until Screen Not Contain 	rfwasrm_mac_GoToTheFolder.png 	10
	Sleep 	.5
	Press Special Key 	ENTER
	Wait Until Screen Not Contain 	rfwasrm_mac_OpenFile.png 	10
	Click Index 1

2 Agents Ready
	Wait until screen contain 	rfwasrm_mac_Agents_Ready.png	300

Open Graphs Menu
	Click 	rfwasrm_mac_Graphs_Menu.png
	Wait until screen contain 	rfwasrm_mac_Graphs_Menu_Open.png	10

Open Graphs Menu Examples
	Open Graphs Menu
	Mouse Move 	rfwasrm_mac_Graphs_Menu_Examples.png
	# Sleep 	1
	Wait until screen contain 	rfwasrm_mac_Graphs_Menu_Examples_Open_expect.png	10

Close Window
	${wndctrl}= 	Get Image Coordinates 	rfwasrm_mac_Window_Controls.png
	Highlight Region 	${wndctrl} 	1
	# ${score}= 	Get Match Score		rfwasrm_mac_Window_Controls.png
	Set Min Similarity 	0.88
	Click 	rfwasrm_mac_Window_Controls.png 	xOffset=-23 	yOffset=0
	Set Min Similarity 	0.7

Close Graph Window
	Set Min Similarity 	0.88
	Click 	rfwasrm_mac_GraphWindow_Controls 	xOffset=-36 	yOffset=-21
	Set Min Similarity 	0.7

Open SS Close Graph
	[Arguments]		${GraphName}
	Open Graphs Menu Examples
	Click 	rfwasrm_mac_Graphs_Menu_Examples_${GraphName}.png
	# Click Text 	${GraphName}
	Sleep 	15
	Take SS 	Graphs 	${GraphName}
	Close Graph Window

Open SS Close New Graph
	Open Graphs Menu
	Click 	rfwasrm_mac_Graphs_Menu_New.png
	Sleep 	1
	Take SS 	Graphs 	New_Graph_Metric
	Click 	rfwasrm_mac_Graphs_Menu_New_DataType.png
	Wait until screen contain 	rfwasrm_mac_Graphs_Menu_New_DataType_Result.png 	5
	Click 	rfwasrm_mac_Graphs_Menu_New_DataType_Result.png
	Sleep 	1
	Take SS 	Graphs 	New_Graph_Result
	Close Graph Window
