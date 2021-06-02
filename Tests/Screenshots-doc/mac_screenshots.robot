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
	# open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/150 users stepped in groups of 25.rfs")
	# takess("Plan", "150u_25per10min")
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/150 users stepped in groups of 25.rfs
	Take SS 	Plan 	150u_25per10mins

saved opened
	# open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/test2.rfs")
	# takess("Plan", "saved_opened")
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/test2.rfs
	Take SS 	Plan 	saved_opened

20 robots delay example
	# open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/Simple_delay.rfs")
	# takess("Plan", "20u_delay_example")
	Open Scenario	/Users/dave/Documents/GitHub/rfswarm/Scenarios/Simple_delay.rfs
	Take SS 	Plan 	20u_delay_example

Agents Ready
	# click_new()
	# click_Agents()
	# takess("Agents", "Ready")
	Click New
	Click Agents
	Take SS 	Agents 	Ready

About Screen
	# click_About()
	# takess("About", "About")
	Click About
	Take SS 	About 	About


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
	Sleep 	1

Click Run
	Click	rfwasrm_mac_Run.png
	Sleep 	1

Click Agents
	Click	rfwasrm_mac_Agents.png
	Sleep 	1

Click About
	Click	rfwasrm_mac_About.png
	Sleep 	1

Click New
	Click 	rfwasrm_mac_New.png
	Run Keyword And Ignore Error	Click	rfwasrm_mac_No.png
	Click Index 1

Click Settings
	Click	rfwasrm_mac_Settings.png
	Wait until screen contain 	rfwasrm_mac_Save.png 	10

Click Cancel
	Click	rfwasrm_mac_Cancel.png

Click Index 1
	Click 	rfwasrm_mac_Index_1.png
	Sleep 	1

Open Scenario
	[Arguments]		${scenario_file}
	Click 	rfwasrm_mac_Open.png
	Run Keyword And Ignore Error	Click	rfwasrm_mac_No.png
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
	Press Special Key 	ENTER
	Wait Until Screen Not Contain 	rfwasrm_mac_OpenFile.png 	10
	Click Index 1
