*** Settings ***

Suite Setup 		My Suite Setup
Suite Teardown 		My Suite Teardown
Test Setup 			My Test Setup
Test Teardown 		My Test Teardown

*** Variables ***

*** Tasks ***
My Example Test Case
    [Documentation]    run a test case
	Do Something
	Do Something
	Do Something


*** Keywords ***

My Suite Setup
	Do Something

My Suite Teardown
	Do Something

My Test Setup
	Do Something

My Test Teardown
	Do Something

Do Something
	Log 	Do Something
	Sleep 	1

 #
 
