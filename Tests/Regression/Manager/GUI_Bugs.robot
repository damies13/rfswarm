*** Settings ***
Test Tags       Bugs 	GUI

Resource 	GUI_Common.robot
Suite Setup 	Set Platform

Test Teardown 	Run Keyword		Close Manager GUI ${platform}

*** Variables ***
@{robot_data}=	example.robot	Example Test Case
${scenario_name}=	test_scenario

*** Test Cases ***
Verify If Manager Runs With Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Run Keywords
	...    Set Global Filename And Default Save Path	${robot_data}[0]	AND
	...    Open Manager GUI													AND
	...    Run Keyword		Close Manager GUI ${platform}

	File Should Exist	${global_path}${/}RFSwarmManager.ini
	File Should Not Be Empty	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with existing ini file.
	Open Manager GUI
	TRY
		Click Tab	Run
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
		Click Tab	Plan
	EXCEPT
		Fail	msg=RFSwarm Manager is not responding!
	END

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}

Verify If Manager Runs With No Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	Remove File		${global_path}${/}RFSwarmManager.ini
	File Should Not Exist	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with no existing ini file.
	Open Manager GUI
	TRY
		Click Tab	Run
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
		Click Tab	Plan
	EXCEPT
		Fail	msg=RFSwarm Manager is not responding!
	END

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}

Verify If Manager Runs With Existing INI File From Previous Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	Remove File		${global_path}${/}RFSwarmManager.ini
	File Should Not Exist	${global_path}${/}RFSwarmManager.ini
	${v1_0_0_inifile}=		Normalize Path		${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmManager.ini
	Copy File	${v1_0_0_inifile}		${global_path}
	File Should Exist	${global_path}${/}RFSwarmManager.ini
	File Should Not Be Empty	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with existing ini file.
	Open Manager GUI
	TRY
		Click Tab	Run
		Wait For	manager_${platform}_button_stoprun.png	timeout=30
		Click Tab	Plan
	EXCEPT
		Fail	msg=RFSwarm Manager is not responding!
	END

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}

Verify That INI Graphs Are Loaded When the Provided Scenario Is Invalid
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #362
	[Setup]	Run Keywords
	...    Change Manager INI Option 	Plan 	scenariofile 	${EMPTY} 	AND
	...    Set INI Window Size 	1200 	600

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#362${/}invalid.rfs
	${inifile}= 		Normalize Path 	${CURDIR}${/}testdata${/}Issue-#362${/}RFSwarmManager.ini
	VAR 	@{mngr_options} 	-s 	${scenariofile} 	-i 	${inifile}
	Open Manager GUI 	${mngr_options}

	Sleep 	5s

	Take A Screenshot
	VAR 	${graph_settings} 	manager_${platform}_button_graphsettings.png
	Wait For 	${graph_settings} 	 timeout=30

	IF 	"${platform}" == "macos"
		Click Button 	CloseWindow
	ELSE
		Click Button With Vertical Offset 	GraphSettings 	offset=-15
	END

	Click Menu 	graphs
	Sleep 	1
	Take A Screenshot
	Click Menu 	Recent
	Sleep 	1
	Take A Screenshot
	# Select Option 	InvalidScenarioTestGraph
	# Sleep 	1
	# Take A Screenshot

	# IF 	"${platform}" == "macos"
	# 	Click Button 	CloseWindow
	# ELSE
	# 	Click Button With Vertical Offset 	GraphSettings 	offset=-15
	# END

	Run Keyword 	Close Manager GUI ${platform}

	Check Logs

	${running}= 	Is Process Running 	${process_manager}
	[Teardown] 	Run Keyword If 	${running} 	Close Manager GUI ${platform}

# # Test for Issue #171	moved to agent test suite, can easily be tested for via the command line
# Issue #171
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	Open Agent
# 	Open Manager GUI
# 	Resize Window 	100 	10
# 	Take A Screenshot
#
# 	Wait Agent Ready
# 	Click Tab 	 Plan
#
# 	# manager_macos_button_runsettings
# 	Click Button 	runsettings
# 	Take A Screenshot
# 	# Click Button 	Cancel
# 	Click Image		manager_${platform}_button_closewindow.png
#
# 	Run Keyword 	Close Manager GUI ${platform}
# 	Stop Agent
