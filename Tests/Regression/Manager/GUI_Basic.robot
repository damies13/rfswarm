*** Settings ***
# Library 	OperatingSystem
Library 	Process
Library 	SikuliLibrary

Suite Setup       Sikili Setup


*** Variables ***
${IMAGE_DIR} 	${CURDIR}/../../Screenshots-doc/img

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py    alias=Manager
	Wait Until Screen Contain 	rfwasrm_mac_Window_Controls.png 	120s
	Make rfswarm Active
	Type With Modifiers 	q 	CMD
	${result}= 	Wait For Process 	First
	Should Be Equal As Integers 	${result.rc} 	0


*** Keywords ***
Sikili Setup
	Add Image Path    ${IMAGE_DIR}

Make rfswarm Active
	Click 	rfwasrm_mac_title_bg.png
	Run Keyword And Ignore Error	Click Plan

Click Plan
	Click	rfwasrm_mac_Plan.png
	Wait until screen contain 	rfwasrm_mac_Play.png	10
