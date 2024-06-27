*** Settings ***
Resource 	GUI_Common.robot

Test Teardown 	Close GUI

*** Test Cases ***
Verify That Files Get Saved With Correct Extension And Names
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #39
	${testdata}=		Set Variable	Issue-#39
	${resultdata}=		Set Variable	20240622_182505_Issue-#39
	${basefolder}=		Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}=	Set Variable	${basefolder}${/}${resultdata}
	#${manager_dir}=		Get Manager Default Save Path

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder: ${resultfolder} 	console=True
	Log To Console	Files to check: report file, report template, output files from reporter (html docx xlsx)

	Open GUI	-d 	${resultfolder}
	Click Button	savetemplate
	Save Template File OS DIALOG	Issue-#39
	Click Button	generatehtml
	Click Button	generateword
	Click Button	generateexcel
	Sleep	5

	# Verify files:
	@{manager_files}=		List Files In Directory		${manager_dir}
	Log To Console	${\n}All manager files: ${manager_files}${\n}
	@{template_file}=		List Files In Directory		${manager_dir}	pattern=Issue-#39*
	Length Should Be	${template_file}	1	msg=Template file name didnt saved correctly!
	@{template_file_fragmented}=	Split String	${template_file}[0]		separator=.
	Length Should Be	${template_file_fragmented}		2	msg=template file: ${template_file}[0] didnt saved correctly!
	Should Be Equal		${template_file_fragmented}[0]		Issue-#39	msg=File name is not correct!
	Should Be Equal		${template_file_fragmented}[1]		template	msg=File extension is not correct!

	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	Length Should Be	${result_files}		5	msg=Raport files name didnt saved correctly!
	
	@{file_extensions}	Create List		db	docx	html	report	xlsx
	FOR  ${i}  IN RANGE  0  5
		${file}		Set Variable	${result_files}[${i}]
		@{file_fragmented}=		Split String	${file}		separator=.
		Length Should Be	${file_fragmented}		2	msg=${file_extensions}[${i}] file didnt saved correctly!
		Should Be Equal		${file_fragmented}[0]		${resultdata}	msg=File name is not correct!
		Should Be Equal		${file_fragmented}[1]		${file_extensions}[${i}]	msg=File extenstion is not correct!
	END

	[Teardown]	Run Keywords
	...    Remove File	${manager_dir}${/}Issue-#39*	AND
	...    Close GUI

Whole report time range
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #138
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
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

	Click Section			Robots
	Click Tab 	 Preview

	# check the graph as expected
	Set Confidence		0.8
	Locate 	reporter_${platform}_graph_robots1.png
	Set Confidence		0.9

	Click Tab 	 Settings
	Click Section			Report

	# Set start time 14:20
	# Select Field With Label 	StartTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace
	# Type 	20
	${StartTime}= 	Get Text Value To Right Of 	StartTime
	${StartTime}= 	Replace String 	${StartTime} 	14:11 	14:20
	Set Text Value To Right Of 	StartTime 	${StartTime}

	# Set start time 14:58
	# Select Field With Label 	EndTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace
	# Type 	14:58
	${EndTime}= 	Get Text Value To Right Of 	EndTime
	${EndTime}= 	Replace String 	${EndTime} 	15:00 	14:58
	Set Text Value To Right Of 	EndTime 	${EndTime}

	# ${bounds}= 	Find Text 	Title:

	Select Field With Label 	Title

	Click Tab 	 Preview
	Wait For Status 	PreviewLoaded

	Sleep    10

	Wait For Status 	PreviewLoaded
	Click Section			Robots
	Wait For Status 	PreviewLoaded

	# check the graph as expected
	Set Confidence		0.8
	Locate 	reporter_${platform}_graph_robots2.png
	Set Confidence		0.9

Verify if reporter handle missing test result file
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #157
	${testdata}		Set Variable	Issue-#157
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}
	Copy File	${resultfolder}${/}${resultdata}.db		${basefolder}${/}result_backup${/}

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder: ${resultfolder} 	console=True

	Open GUI	-d 	${resultfolder}
	Wait For Status 	PreviewLoaded
	Close GUI

	Should Exist	${basefolder}${/}result_backup${/}${resultdata}.db
	Remove File		${resultfolder}${/}${resultdata}.db

	Open GUI	-d 	${resultfolder}
	Sleep	10
	Click Section	test_result_summary
	Click	#double click needed. Maybe delete after eel module implemetation

	${status}=	Run Keyword And Return Status
	...    Wait For	reporter_${platform}_option_datatable.png 	timeout=${30}
	Run Keyword If	not ${status}	Fail	msg=Reporter is not responding!

	[Teardown]	Run Keywords
	...    Copy File	${basefolder}${/}result_backup${/}${resultdata}.db	${resultfolder}		AND
	...    Remove File	${basefolder}${/}result_backup${/}${resultdata}.db						AND
	...    Close GUI
