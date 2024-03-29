*** Settings ***
Resource 	GUI_Common.robot

Suite Setup 	Set Platform

*** Test Cases ***
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

Verify scenario file content for example robot
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #1
	@{correct_data}		Set Variable	Example Test Case	example.robot
	${scenario_name}	Set Variable	test_scenario

	Set INI Data Window Size	900		400
	Open Manager GUI
	Set Global Save Path And Filename	${correct_data}[1]
	Create Example Robot File
	Click Button	runscriptrow
	Select Robot File	@{correct_data}
	Click Button	select_test_case
	Click Button	select_example
	Click Button	runsave
	Save Scenario File	${scenario_name}
	Verify scenario File	${scenario_name}	@{correct_data}
	Delete Scenario File	${scenario_name}
	Delete Example Robot File
	Run Keyword		Close Manager GUI ${platform}
