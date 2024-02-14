*** Settings ***
Resource 	GUI_Common.robot

Suite Setup 	Set Platform

*** Test Cases ***
Issue #171
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Open Agent
	Open Manager GUI
	Click Tab 	 Agents
	# give time for agent to start and connect to manager
	Sleep 	20
	Take A Screenshot

	Run Keyword 	Close Manager GUI ${platform}
	Stop Agent
