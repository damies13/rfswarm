*** Settings ***
Resource 	GUI_Common.robot

Test Teardown 	Close GUI

*** Test Cases ***
Whole report time range
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #138
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#138
	${resultdata}= 	Set Variable    20230928_141103_OCDemo_Requests
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Open GUI	-d 	${resultfolder}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Robot
	Click Tab 	 Preview

	# check the graph as expected

	Click Tab 	 Settings
	Click Section			Report

	# Set start time 14:20

	# Set start time 14:58

	Wait For Status 	PreviewLoaded

	Click Section			Robot
	Wait For Status 	PreviewLoaded
	Click Tab 	 Preview

	# check the graph as expected
