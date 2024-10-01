*** Settings ***
Resource 	GUI_Common.robot

Suite Setup 	Set Platform
Test Teardown 	Close GUI

*** Test Cases ***
Verify That Files Get Saved With Correct Extension And Names
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #39 	Issue #257
	${testdata}=		Set Variable	Issue-#39
	${resultdata}=		Set Variable	20240622_182505_Issue-#39
	${basefolder}=		Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}=	Set Variable	${basefolder}${/}${resultdata}
	${templatefolder}=	Set Variable	${resultfolder}${/}template_dir
	${templatename}=	Set Variable	Issue-#39
	Change Reporter INI File Settings	templatedir		${templatefolder}

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder: ${resultfolder} 	console=True
	Log To Console	Files to check: report file, report template, output files from reporter (html docx xlsx)

	Open GUI	-d 	${resultfolder}
	Click Button	savetemplate
	Save Template File OS DIALOG	${templatename}
	Click Button	generatehtml
	Sleep	2
	Click Button	generateword
	Sleep	2
	Click Button	generateexcel
	Sleep	2

	# Verify files:
	Remove File		${templatefolder}${/}here_will_be_template.txt
	@{template_files}=		List Files In Directory		${templatefolder}
	Log To Console	${\n}All Template files: ${template_files}${\n}
	@{template_file}=		List Files In Directory		${templatefolder}
	Length Should Be	${template_file}	1	msg=The Template file was not saved at all!
	Should Be Equal As Strings		${template_file}[0]		${template_name}.template
	...    msg=Template file name incorrect: expected "${template_name}.template", actual: "${template_file}[0]"

	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	Length Should Be	${result_files}		5	msg=Result files didnt saved correctly!

	@{file_extensions}	Create List		db	docx	html	report	xlsx
	FOR  ${i}  IN RANGE  0  5
		${file}		Set Variable	${result_files}[${i}]
		Should Be Equal As Strings		${file}		${resultdata}.${file_extensions}[${i}]
		...    msg=Result file name incorrect: expected "${resultdata}.${file_extensions}[${i}]", actual: "${file}"
	END

	[Teardown]	Run Keywords
	...    Remove File	${templatefolder}${/}Issue-#39*						AND
	...    Create File		${templatefolder}${/}here_will_be_template.txt	AND
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
	# pass a non-existant ini file to ensure that default values are used
	Open GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}${testdata}.ini
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

Verify the Content Of the DOCX Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #38 	DOCX	robot:continue-on-failure 	hi
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${docx_file}		${resultfolder}${/}${resultdata}.docx
	VAR 	${image_move_tolerance} 	10 	# used for comparing images (this is needed because of different colours)

	Log 	template: ${template_dir} 	console=True
	Open GUI	-d 	${resultfolder} 	-t 	${template_dir}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=300
	Click Button	generateword
	Wait Until Created 	${resultfolder}${/}${resultdata}.docx	timeout=9 minutes
	Close GUI

	Log To Console	Verification of saved data in the RFSwarm DOCX raport started.
	File Should Exist 	${docx_file}
	&{docx_content}= 	Read Docx File 	${docx_file}
	@{docx_images_names}= 	Extract Images From Docx 	${docx_file} 	${OUTPUT_DIR}${/}${testdata}${/}docx_images
	@{expected_docx_images_names}= 	List Files In Directory 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images
	Run Keyword And Continue On Failure 	Lists Should Be Equal
	...    ${expected_docx_images_names} 	${docx_images_names} 	msg=Not all images were extracted form the docx. [ Expected != Extracted ] 	ignore_order=${True}
	@{docx_tables}= 	Extract Tables From Docx 	${docx_file}
	Log		${docx_content}
	Log		${docx_images_names}
	Log		${docx_tables}

	@{docx_images}= 	List Files In Directory 	${OUTPUT_DIR}${/}${testdata}${/}docx_images 	absolute=${true}
	${docx_images}= 	Sort Docx Images 	${docx_images}
	Log 	${docx_images}
	@{expected_docx_images}= 	List Files In Directory 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images 	absolute=${True}
	${expected_docx_images} 	Sort Docx Images 	${expected_docx_images}
	Log 	${expected_docx_images}
	# VAR 	${docx_images_dir} 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images
	# VAR 	${expected_docx_images_dir} 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images

	Dictionary Should Contain Key 	${docx_content} 	No Heading 	msg=DOCX raport file didn't
	@{no_heading_contet} 	Convert To List 	${docx_content}[No Heading]
	VAR 	@{no_heading_expected}	quickdemo  2023-07-28 15:42 - 15:50
	Lists Should Be Equal 	${no_heading_expected} 		${no_heading_contet}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_content} 	1 This is Heading

	# Contents:
	Dictionary Should Contain Key 	${docx_content} 	2 Contents contents
	Dictionary Should Contain Key 	${docx_content} 	3 Contents graphs
	Dictionary Should Contain Key 	${docx_content} 	4 Contents tables

	# Notes:
	Dictionary Should Contain Key 	${docx_content} 	5 Note
	@{5_Note_contet} 	Convert To List 	${docx_content}[5 Note]
	VAR 	@{5_Note_expected}	Hello i am a simple and obvious note :-)  This is just second line.  - first line  - second line  - third line
	Lists Should Be Equal 	${5_Note_expected} 		${5_Note_contet}	msg=[ Expected != Converted ]
	Dictionary Should Contain Key 	${docx_content} 	5.1 Second Note
	Should Contain 	${docx_content}[5.1 Second Note] 	This is my second note.
	Dictionary Should Contain Key 	${docx_content} 	5.1.1 Third Note
	Should Contain 	${docx_content}[5.1.1 Third Note] 	This is my third note.

	# Graphs - when new graphs are required, save them using the function in read_docx.py!
	Dictionary Should Contain Key 	${docx_content} 	6 Data Graph Left Metric
	Compare Images 	${expected_docx_images}[0] 	${docx_images}[0] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	7 Data Graph Left Result
	Compare Images 	${expected_docx_images}[1] 	${docx_images}[1] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	8 Data Graph Left Result FAIL
	Compare Images 	${expected_docx_images}[2] 	${docx_images}[2] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	9 Data Graph Left Result TPS
	Compare Images 	${expected_docx_images}[3] 	${docx_images}[3] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	10 Data Graph Left Result Total TPS
	Compare Images 	${expected_docx_images}[4] 	${docx_images}[4] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	11 Data Graph Right Metric
	Compare Images 	${expected_docx_images}[5] 	${docx_images}[5] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	Dictionary Should Contain Key 	${docx_content} 	12 Data Graph Right Result
	Compare Images 	${expected_docx_images}[6] 	${docx_images}[6] 	move_tolerance=${image_move_tolerance} 	threshold=0.5

	# Tables:
	Length Should Be 	${docx_tables} 	6

	Dictionary Should Contain Key 	${docx_content} 	13 Data Table Metric
	Log 	Data Table Metric: ${docx_tables}[0]
	VAR 	${table_metric_expected_length} 	437
	VAR 	@{table_metric_expected} 	PrimaryMetric  MetricType  SecondaryMetric  Minimum  Average  90%ile  Maximum  Std. Dev.
	@{table_metric_first_row} 	Convert To List 	${docx_tables}[0][0]	#first row (header)
	Length Should Be 	${docx_tables}[0] 	${table_metric_expected_length}
	Lists Should Be Equal 	${table_metric_expected} 	${table_metric_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_metric_expected_length}
		VAR 	${row} 		${docx_tables}[0][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Metric!
	END

	Dictionary Should Contain Key 	${docx_content} 	14 Data Table Result
	Log 	Data Table Result: ${docx_tables}[1]
	VAR 	${table_result_expected_length} 	42
	VAR 	@{table_result_expected} 	Result Name  Minimum  Average  90%ile  Maximum  Std. Dev.  Count
	@{table_result_first_row} 	Convert To List 	${docx_tables}[1][0]	#first row (header)
	Length Should Be 	${docx_tables}[1] 	${table_result_expected_length}
	Lists Should Be Equal 	${table_result_expected} 	${table_result_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_expected_length}
		VAR 	${row} 		${docx_tables}[1][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result!
	END

	Dictionary Should Contain Key 	${docx_content} 	15 Data Table Result TPS
	Log 	Data Table Result TPS: ${docx_tables}[2]
	VAR 	${table_result_tps_expected_length} 	60
	VAR 	@{table_result_tps_expected} 	Result Name  Result  Count
	@{table_result_tps_first_row} 	Convert To List 	${docx_tables}[2][0]	#first row (header)
	Length Should Be 	${docx_tables}[2] 	${table_result_tps_expected_length}
	Lists Should Be Equal 	${table_result_tps_expected} 	${table_result_tps_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_tps_expected_length}
		VAR 	${row} 		${docx_tables}[2][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result TPS!
	END

	Dictionary Should Contain Key 	${docx_content} 	16 Data Table Result TotalTPS
	Log 	Data Table Result TotalTPS: ${docx_tables}[3]
	VAR 	${table_result_ttps_expected_length} 	4
	VAR 	@{table_result_ttps_expected} 	Result  Count
	@{table_result_ttps_first_row} 	Convert To List 	${docx_tables}[3][0]	#first row (header)
	Length Should Be 	${docx_tables}[3] 	${table_result_ttps_expected_length}
	Lists Should Be Equal 	${table_result_ttps_expected} 	${table_result_ttps_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_ttps_expected_length}
		VAR 	${row} 		${docx_tables}[3][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result TotalTPS!
	END

	Dictionary Should Contain Key 	${docx_content} 	17 Data Table ResultSummary
	Log 	Data Table ResultSummary: ${docx_tables}[4]
	VAR 	${table_resultSum_expected_length} 	42
	VAR 	@{table_resultSum_expected}
	...    ${EMPTY}  Result Name  Minimum  Average  90%ile  Maximum  Std. Dev.  Pass  Fail  Other	# first colum is ${None} because of the enabled colors
	@{table_resultSum_first_row} 	Convert To List 	${docx_tables}[4][0]	#first row (header)
	Length Should Be 	${docx_tables}[4] 	${table_resultSum_expected_length}
	Lists Should Be Equal 	${table_resultSum_expected} 	${table_resultSum_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_resultSum_expected_length}
		VAR 	${row} 		${docx_tables}[4][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table ResultSummary!
	END

	# Error Details:
	Dictionary Should Contain Key 	${docx_content} 	18 Error Details
	Log 	Error Details Table content: ${docx_tables}[5]
	VAR 	${table_error_expected_length} 	33
	VAR 	@{table_error_expected}
	...    Result:  Odoo Create Sale  Odoo Create Sale  Test:  Odoo Sales  Script:  Odoo.robot  Count:  4
	# Doubled "Odoo Create Sale" value because it is in two cols?
	VAR 	@{expected_first_col} 		Result:  Error:  Screenshot:
	@{table_error_first_row} 	Convert To List 	${docx_tables}[5][0]	#first row (header)
	Length Should Be 	${docx_tables}[5] 	${table_error_expected_length}
	Lists Should Be Equal 	${table_error_expected} 	${table_error_first_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[5][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_first_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_first_col}.
		END
	END

	VAR 	${first_error_image} 	48
	${len}= 	Get Length 	${expected_docx_images}
	FOR  ${image_num}  IN RANGE  ${first_error_image}  ${len}
		Compare Images 	${expected_docx_images}[${image_num}] 	${docx_images}[${image_num}]	# images should be the same tolerance is not needed
	END

	[Teardown] 	Run Keywords
	...    Close GUI	AND
	...    Move File 	${docx_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx

Check Application Icon or Desktop Shortcut in GUI
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	${result}= 	Run 	${cmd_reporter} -g 6 -c ICON
	Log 		${result}
	Sleep    1

	Navigate to and check Desktop Icon

	[Teardown]	Type 	KEY.ESC 	KEY.ESC 	KEY.ESC


#
