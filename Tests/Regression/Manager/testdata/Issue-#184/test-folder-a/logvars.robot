*** Settings ***
Resource 	..${/}test-folder-common${/}resource.robot

*** Variables ***


*** Test Cases ***
Log Variables Folder A
  Sleep   1
  Log Vars
	Log Vars Deep
	Log Vars


#
