*** Settings ***
Resource 	GUI_Common.robot

*** Test Cases ***
Issue #171
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Open Agent
	Open Manager GUI
	Click Tab 	 Agents
	Sleep 	5
	Take A Screenshot

	Close Manager GUI
	Stop Agent
