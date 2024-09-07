*** Settings ***
Resource 	CommandLine_Common.robot

Suite Setup 	Set Platform

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	${result}= 	Run 	${cmd_reporter} -c ICON
	Log 		${result}
	Check Icon Install
