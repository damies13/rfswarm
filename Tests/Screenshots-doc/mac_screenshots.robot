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



#	def gui_run():
#	    click_new()
#	    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/30u5r20m.rfs")
#	    click_Agents()
#	    wait("1622432336397.png", 300)
#	    click_Plan()
#	    click_play()
#	    wait(5)
#	    takess("Run", "Start_5s")
#	    wait(55)
#	    takess("Run", "Start_60s")
#	    click_Agents()
#	    takess("Agents", "Runing")
#	    click_Run()
#	    click_stop()
#	    takess("Run", "Bomb_Run")
#	    wait(10)
#	    click_Agents()
#	    takess("Agents", "Stopping")
#	    click_Run()
#	    click_abort()
#	    takess("Run", "Abort_Dialogue")
#	    click_Yes()
#	    click_aborted()
#	    takess("Run", "Aborted")

Aborted Run
	Click Plan
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


#	def gui_2h():
#	    click_new()
#	    open_scenario("/Users/dave/Documents/GitHub/rfswarm/Scenarios/100u_test.rfs")
#	    click_Agents()
#	    wait("1622432336397.png", 300)
#	    click_Plan()
#	    click_play()




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
	Run Keyword And Ignore Error	Click	rfwasrm_mac_No.png
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
	Sleep 	.5
	Press Special Key 	ENTER
	Wait Until Screen Not Contain 	rfwasrm_mac_OpenFile.png 	10
	Click Index 1

2 Agents Ready
	Wait until screen contain 	rfwasrm_mac_Agents_Ready.png	300
