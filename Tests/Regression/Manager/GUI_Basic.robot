*** Settings ***
Test Tags       Basic 	GUI

Resource 	../../Resources/Tk_GUI/Manager/GUI_Manager.resource
Resource 	../../Resources/Common/GUI_RFS_Components.resource

Suite Setup 	GUI_Common.GUI Suite Initialization Manager

*** Variables ***
${pyfile}		${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process}		${None}

*** Test Cases ***
Open GUI
	[Tags]	macos-latest		windows-latest		ubuntu-latest

	Open Manager GUI
	Sleep 	5

	${img}=	Set Variable		manager_${platform}_tab_agents.png
	Log 	Waiting for ${img} 	console=True
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot
	Log 	Done 	console=True
Select Monitoring Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest	Issue #173
	Click Tab 	 Monitoring
	Sleep 	5

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
	[Tags]		windows-latest		ubuntu-latest	 	macos-latest
	Close Manager GUI


# Intentional Fail
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
# 	...								Ensure this is commented out before release or pull request
# 	Fail


*** Keywords ***
Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		manager_${PLATFORM}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot
