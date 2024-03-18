*** Settings ***
Resource 	${CURDIR}${/}..${/}test-folder-common${/}resource.robot

*** Variables ***


*** Test Cases ***
Log Variables Folder A
  Sleep   3
  Log Vars
	Sleep   3
	Log Vars Local
	Sleep   3
	Log Vars Deep
	Sleep   3
	Log Vars
	Sleep   3

*** Keywords ***
Log Vars Local
  [Documentation]   Folder A Log Variables AAA
	No Operation


#
