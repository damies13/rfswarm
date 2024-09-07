*** Settings ***
Resource 	CommandLine_Common.robot

Suite Setup 	Set Platform

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	@{agent_options}= 	Create List 	-g 	6 	-c 	ICON
	Run Agent 	${agent_options}
	Sleep    2
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Check Icon Install
