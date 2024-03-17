*** Settings ***
Resource 	..${/}test-folder-common${/}resource.robot

*** Variables ***


*** Test Cases ***
Log Variables Folder A
  Sleep   5
  Log Vars
	Sleep   5
	Log Vars Deep
	Sleep   5
	Log Vars
	Sleep   5


#
