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

	# Take A Screenshot
	# Set start time 14:20
	# Select Field With Label 	StartTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace
	# Type 	20
	${StartTime}= 	Get Text Value To Right Of 	StartTime
	${StartTime}= 	Replace String 	${StartTime} 	14:11 	14:20
	Set Text Value To Right Of 	StartTime 	${StartTime}

	# Take A Screenshot
	Select Field With Label 	Title 		150
	Wait For Status 	PreviewLoaded
	# Take A Screenshot
	# Set start time 14:58
	# Select Field With Label 	EndTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace
	# Type 	14:58
	${EndTime}= 	Get Text Value To Right Of 	EndTime
	${EndTime}= 	Replace String 	${EndTime} 	15:00 	14:58
	Set Text Value To Right Of 	EndTime 	${EndTime}

	# Take A Screenshot
	# ${bounds}= 	Find Text 	Title:

	Select Field With Label 	Title 		150

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
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #38 	DOCX	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${docx_file}		${resultfolder}${/}${resultdata}.docx

	Log 	template: ${template_dir} 	console=True
	Open GUI	-d 	${resultfolder} 	-t 	${template_dir}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=300
	Take A Screenshot
	Click Button	generateword
	Wait Until Created 	${resultfolder}${/}${resultdata}.docx	timeout=9 minutes
	Close GUI

	Log To Console	Verification of saved data in the RFSwarm DOCX raport started.
	File Should Exist 	${docx_file}
	&{docx_paragraphs}= 	Read Paragraphs Docx File 	${docx_file}
	@{docx_images_names}= 	Extract Images From Docx 	${docx_file} 	${OUTPUT_DIR}${/}${testdata}${/}docx_images
	@{expected_docx_images_names}= 	List Files In Directory 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images
	Run Keyword And Continue On Failure 	Lists Should Be Equal
	...    ${expected_docx_images_names} 	${docx_images_names} 	msg=Not all images were extracted form the docx. [ Expected != Extracted ] 	ignore_order=${True}
	@{docx_tables}= 	Extract Tables From Docx 	${docx_file}
	Log		${docx_paragraphs}
	Log		${docx_images_names}
	Log		${docx_tables}

	@{docx_images}= 	List Files In Directory 	${OUTPUT_DIR}${/}${testdata}${/}docx_images 	absolute=${true}
	${docx_images}= 	Sort Docx Images 	${docx_images}
	Log 	${docx_images}
	@{expected_docx_images}= 	List Files In Directory 	${CURDIR}${/}testdata${/}Issue-#38${/}docx_images 	absolute=${True}
	${expected_docx_images} 	Sort Docx Images 	${expected_docx_images}
	Log 	${expected_docx_images}

	Dictionary Should Contain Key 	${docx_paragraphs} 	No Heading
	@{no_heading_contet} 	Convert To List 	${docx_paragraphs}[No Heading]
	VAR 	@{no_heading_expected}	quickdemo  2023-07-28 15:42 - 15:50
	Lists Should Be Equal 	${no_heading_expected} 		${no_heading_contet}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	1 This is Heading


	# Contents:
	Dictionary Should Contain Key 	${docx_paragraphs} 	2 Contents contents
	Dictionary Should Contain Key 	${docx_paragraphs} 	3 Contents graphs
	Dictionary Should Contain Key 	${docx_paragraphs} 	4 Contents tables


	# Notes:
	Dictionary Should Contain Key 	${docx_paragraphs} 	5 Note
	@{5_Note_contet} 	Convert To List 	${docx_paragraphs}[5 Note]
	VAR 	@{5_Note_expected}	Hello i am a simple and obvious note :-)  This is just second line.  - first line  - second line  - third line
	Lists Should Be Equal 	${5_Note_expected} 		${5_Note_contet}	msg=[ Expected != Converted ]
	Dictionary Should Contain Key 	${docx_paragraphs} 	5.1 Second Note
	Should Contain 	${docx_paragraphs}[5.1 Second Note] 	This is my second note.
	Dictionary Should Contain Key 	${docx_paragraphs} 	5.1.1 Third Note
	Should Contain 	${docx_paragraphs}[5.1.1 Third Note] 	This is my third note.


	# Graphs - when new graphs are required, save them using the function in read_docx.py!
	Dictionary Should Contain Key 	${docx_paragraphs} 	6 Data Graph Left Metric
	Convert Image To Black And White 	${docx_images}[0]
	Compare Images 	${expected_docx_images}[0] 	${docx_images}[0]

	Dictionary Should Contain Key 	${docx_paragraphs} 	7 Data Graph Left Result
	Convert Image To Black And White 	${docx_images}[1]
	Compare Images 	${expected_docx_images}[1] 	${docx_images}[1]

	Dictionary Should Contain Key 	${docx_paragraphs} 	8 Data Graph Left Result FAIL
	Convert Image To Black And White 	${docx_images}[2]
	Compare Images 	${expected_docx_images}[2] 	${docx_images}[2]

	Dictionary Should Contain Key 	${docx_paragraphs} 	9 Data Graph Left Result TPS
	Convert Image To Black And White 	${docx_images}[3]
	Compare Images 	${expected_docx_images}[3] 	${docx_images}[3]

	Dictionary Should Contain Key 	${docx_paragraphs} 	10 Data Graph Left Result Total TPS
	Convert Image To Black And White 	${docx_images}[4]
	Compare Images 	${expected_docx_images}[4] 	${docx_images}[4]

	Dictionary Should Contain Key 	${docx_paragraphs} 	11 Data Graph Right Metric
	Convert Image To Black And White 	${docx_images}[5]
	Compare Images 	${expected_docx_images}[5] 	${docx_images}[5]

	Dictionary Should Contain Key 	${docx_paragraphs} 	12 Data Graph Right Result
	Convert Image To Black And White 	${docx_images}[6]
	Compare Images 	${expected_docx_images}[6] 	${docx_images}[6]

	Dictionary Should Contain Key 	${docx_paragraphs} 	13 Data Graph LR Combined
	Convert Image To Black And White 	${docx_images}[7]
	Compare Images 	${expected_docx_images}[7] 	${docx_images}[7]


	# Tables:
	Length Should Be 	${docx_tables} 	11

	Dictionary Should Contain Key 	${docx_paragraphs} 	14 Data Table Metric
	Log 	Data Table Metric: ${docx_tables}[0]
	VAR 	${table_metric_expected_length} 	437
	VAR 	@{table_metric_header_expected} 	PrimaryMetric  MetricType  SecondaryMetric  Minimum  Average  90%ile  Maximum  Std. Dev.
	@{table_metric_header_row} 	Convert To List 	${docx_tables}[0][0]	# table first row (header)
	Length Should Be 	${docx_tables}[0] 	${table_metric_expected_length}
	Lists Should Be Equal 	${table_metric_header_expected} 	${table_metric_header_row}	msg=[ Expected != Converted ]
	# [1] equals first data row
	@{14_table_1} 	Convert To List 	${docx_tables}[0][1]
	VAR 	@{14_table_1_expected} 		1  Scenario_Delay 	Odoo Sales 	0 	0.0 	None 	0 	None
	Lists Should Be Equal 	${14_table_1_expected} 	${14_table_1}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{14_table_-1} 	Convert To List 	${docx_tables}[0][-1]
	VAR 	@{14_table_-1_expected} 	Waits until the element ``locator`` is visible. 	Summary 	stDev 	0.006 	0.047 	0.089 	0.089 	0.038
	Lists Should Be Equal 	${14_table_-1_expected} 	${14_table_-1}	msg=[ Expected != Converted ]
	# [107] equals quater row
	@{14_table_107} 	Convert To List 	${docx_tables}[0][107]
	VAR 	@{14_table_107_expected} 		Delay_4 	Scenario 	Odoo Receipts 	0 	0.0 	None 	0 	None
	Lists Should Be Equal 	${14_table_107_expected} 	${14_table_107}	msg=[ Expected != Converted ]
	# [218] equals middle row
	@{14_table_218} 	Convert To List 	${docx_tables}[0][218]
	VAR 	@{14_table_218_expected} 		Odoo Open Receipt 	Summary 	max 	None 	None 	None 	None 	None
	Lists Should Be Equal 	${14_table_218_expected} 	${14_table_218}	msg=[ Expected != Converted ]
	# [327] equals upper middle row
	@{14_table_327} 	Convert To List 	${docx_tables}[0][327]
	VAR 	@{14_table_327_expected} 		Returns the number of elements matching ``locator``. 	Summary 	_fail 	0 	0.0 	0.0 	0 	0.0
	Lists Should Be Equal 	${14_table_327_expected} 	${14_table_327}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_metric_expected_length}
		VAR 	${row} 		${docx_tables}[0][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Metric!
	END

	Dictionary Should Contain Key 	${docx_paragraphs} 	15 Data Table Result
	Log 	Data Table Result: ${docx_tables}[1]
	VAR 	${table_result_expected_length} 	42
	VAR 	@{table_result_header_expected} 	Result Name  Minimum  Average  90%ile  Maximum  Std. Dev.  Count
	@{table_result_header_row} 	Convert To List 	${docx_tables}[1][0]
	Length Should Be 	${docx_tables}[1] 	${table_result_expected_length}
	Lists Should Be Equal 	${table_result_header_expected} 	${table_result_header_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_expected_length}
		VAR 	${row} 		${docx_tables}[1][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result!
	END
	# [1] equals first data row
	@{15_table_1} 	Convert To List 	${docx_tables}[1][1]
	VAR 	@{15_table_1_expected} 		:example: 'John Doe' 	0.001 	0.001 	None 	0.001 	0.0 	4
	Lists Should Be Equal 	${15_table_1_expected} 	${15_table_1}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{15_table_-1} 	Convert To List 	${docx_tables}[1][-1]
	VAR 	@{15_table_-1_expected} 	Waits until the element ``locator`` is visible. 	0.045 	0.115 	None 	0.204 	0.078 	5
	Lists Should Be Equal 	${15_table_-1_expected} 	${15_table_-1}	msg=[ Expected != Converted ]
	# [11] equals quater row
	@{15_table_11} 	Convert To List 	${docx_tables}[1][11]
	VAR 	@{15_table_11_expected} 	Odoo Confirm RFQ 	0.001 	1.131 	None 	2.262 	1.599 	2
	Lists Should Be Equal 	${15_table_11_expected} 	${15_table_11}	msg=[ Expected != Converted ]
	# [21] equals middle row
	@{15_table_21} 	Convert To List 	${docx_tables}[1][21]
	VAR 	@{15_table_21_expected} 	Odoo Open Receipt 	0.0 	0.0 	None 	0.0 	None 	1
	Lists Should Be Equal 	${15_table_21_expected} 	${15_table_21}	msg=[ Expected != Converted ]
	# [30] equals upper middle row
	@{15_table_30} 	Convert To List 	${docx_tables}[1][30]
	VAR 	@{15_table_30_expected} 	Opening browser 'Chrome' to base url 'https://192.168.13.58'. 	1.781 	2.781 	None 	3.308 	0.621 	5
	Lists Should Be Equal 	${15_table_30_expected} 	${15_table_30}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	16 Data Table Result TPS
	Log 	Data Table Result TPS: ${docx_tables}[2]
	VAR 	${table_result_tps_expected_length} 	60
	VAR 	@{table_result_tps_expected} 	Result Name  Result  Count
	@{table_result_tps_header_row} 	Convert To List 	${docx_tables}[2][0]
	Length Should Be 	${docx_tables}[2] 	${table_result_tps_expected_length}
	Lists Should Be Equal 	${table_result_tps_expected} 	${table_result_tps_header_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_tps_expected_length}
		VAR 	${row} 		${docx_tables}[2][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result TPS!
	END
	# [1] equals first data row
	@{16_table_1} 	Convert To List 	${docx_tables}[2][1]
	VAR 	@{16_table_1_expected} 		Open Odoo Login Screen 	PASS 	30
	Lists Should Be Equal 	${16_table_1_expected} 	${16_table_1}	msg=[ Expected != Converted ]
	# [-2] equals almost last row
	@{16_table_-2} 	Convert To List 	${docx_tables}[2][-2]
	VAR 	@{16_table_-2_expected} 	Odoo Confirm RFQ 	FAIL 	1
	Lists Should Be Equal 	${16_table_-2_expected} 	${16_table_-2}	msg=[ Expected != Converted ]
	# [15] equals quater row
	@{16_table_15} 	Convert To List 	${docx_tables}[2][15]
	VAR 	@{16_table_15_expected} 	:example: 'John Doe' 	PASS 	4
	Lists Should Be Equal 	${16_table_15_expected} 	${16_table_15}	msg=[ Expected != Converted ]
	# [30] equals middle row
	@{16_table_30} 	Convert To List 	${docx_tables}[2][30]
	VAR 	@{16_table_30_expected} 	Clicking element '(//tr/td/span[text()='RFQ'])[1]'. 	PASS 	1
	Lists Should Be Equal 	${16_table_30_expected} 	${16_table_30}	msg=[ Expected != Converted ]
	# [45] equals upper middle row
	@{16_table_45} 	Convert To List 	${docx_tables}[2][45]
	VAR 	@{16_table_45_expected} 	Odoo Validate Receipt 	NOT RUN 	1
	Lists Should Be Equal 	${16_table_45_expected} 	${16_table_45}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	17 Data Table Result TotalTPS
	Log 	Data Table Result TotalTPS: ${docx_tables}[3]
	VAR 	${table_result_ttps_expected_length} 	4
	VAR 	@{table_result_ttps_header_expected} 	Result  Count
	@{table_result_ttps_header_row} 	Convert To List 	${docx_tables}[3][0]
	Length Should Be 	${docx_tables}[3] 	${table_result_ttps_expected_length}
	Lists Should Be Equal 	${table_result_ttps_header_expected} 	${table_result_ttps_header_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_result_ttps_expected_length}
		VAR 	${row} 		${docx_tables}[3][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table Result TotalTPS!
	END
	# [1] equals first data row
	@{17_table_1} 	Convert To List 	${docx_tables}[3][1]
	VAR 	@{17_table_1_expected} 		PASS 	166
	Lists Should Be Equal 	${17_table_1_expected} 	${17_table_1}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{17_table_-1} 	Convert To List 	${docx_tables}[3][-1]
	VAR 	@{17_table_-1_expected} 	FAIL 	19
	Lists Should Be Equal 	${17_table_-1_expected} 	${17_table_-1}	msg=[ Expected != Converted ]
	# [2] equals last row
	@{17_table_2} 	Convert To List 	${docx_tables}[3][2]
	VAR 	@{17_table_2_expected} 		NOT RUN 	55
	Lists Should Be Equal 	${17_table_2_expected} 	${17_table_2}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	18 Data Table ResultSummary
	Log 	Data Table ResultSummary: ${docx_tables}[4]
	VAR 	${table_resultSum_expected_length} 	42
	VAR 	@{table_resultSum_header_expected}
	...    ${EMPTY}  Result Name  Minimum  Average  90%ile  Maximum  Std. Dev.  Pass  Fail  Other	# first colum is ${None} because of the enabled colors
	@{table_resultSum_header_row} 	Convert To List 	${docx_tables}[4][0]
	Length Should Be 	${docx_tables}[4] 	${table_resultSum_expected_length}
	Lists Should Be Equal 	${table_resultSum_header_expected} 	${table_resultSum_header_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_resultSum_expected_length}
		VAR 	${row} 		${docx_tables}[4][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table ResultSummary!
	END
	# [1] equals first data row
	@{err_1_table} 	Convert To List 	${docx_tables}[4][1]
	VAR 	@{err_1_table_expected} 		${EMPTY} 	:example: 'John Doe' 	0.001 	0.001 	None 	0.001 	0.0 	4 	0 	0
	Lists Should Be Equal 	${err_1_table_expected} 	${err_1_table}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_1_table_-1} 	Convert To List 	${docx_tables}[4][-1]
	VAR 	@{err_1_table_-1_expected} 	${EMPTY} 	Waits until the element ``locator`` is visible. 	0.045 	0.115 	None 	0.204 	0.078 	5 	0 	0
	Lists Should Be Equal 	${err_1_table_-1_expected} 	${err_1_table_-1}	msg=[ Expected != Converted ]
	# [11] equals quater row
	@{err_1_table_1} 	Convert To List 	${docx_tables}[4][11]
	VAR 	@{err_1_table1_expected} 	${EMPTY} 	Odoo Confirm RFQ 	None 	None 	None 	None 	None 	0 	1 	1
	Lists Should Be Equal 	${err_1_table1_expected} 	${err_1_table1}	msg=[ Expected != Converted ]
	# [21] equals middle row
	@{err_1_table_21} 	Convert To List 	${docx_tables}[4][21]
	VAR 	@{err_1_table_21_expected} 	${EMPTY} 	Odoo Open Receipt 	None 	None 	None 	None 	None 	0 	0 	1
	Lists Should Be Equal 	${err_1_table_21_expected} 	${err_1_table_21}	msg=[ Expected != Converted ]
	# [31] equals upper middle row
	@{err_1_table_31} 	Convert To List 	${docx_tables}[4][31]
	VAR 	@{err_1_table_31_expected} 	${EMPTY} 	Returns the number of elements matching ``locator``. 	0.012 	0.012 	None 	0.012 	None 	1 	0 	2
	Lists Should Be Equal 	${err_1_table_31_expected} 	${err_1_table_31}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	19 Data Table Polish Lang
	Log 	Data Table Polish Lang: ${docx_tables}[5]
	VAR 	${table_polish_expected_length} 	42
	VAR 	@{table_polish_header_expected}
	...    Nazwa Wyniku 	Minimum 	Średnia 	90%yl 	Maksimum 	Odchylenie Standardowe 	Pomyślnie 	Niepowodzenie 	Inne
	@{table_polish_header_row} 	Convert To List 	${docx_tables}[5][0]	#first row (header)
	Length Should Be 	${docx_tables}[5] 	${table_polish_expected_length}
	Lists Should Be Equal 	${table_polish_header_expected} 	${table_polish_header_row}	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${table_polish_expected_length}
		VAR 	${row} 		${docx_tables}[5][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Data Table ResultSummary!
	END


	# Error Details:
	# Error Details Screenshots:
	VAR 	${first_error_image} 	49
	${len}= 	Get Length 	${expected_docx_images}
	FOR  ${image_num}  IN RANGE  ${first_error_image}  ${len}
		Compare Images 	${expected_docx_images}[${image_num}] 	${docx_images}[${image_num}]	# images should be the same tolerance is not needed
	END

	Dictionary Should Contain Key 	${docx_paragraphs} 	20 Error Details
	Log 	Error Details Table content: ${docx_tables}[6]
	VAR 	${table_error_expected_length} 	33
	VAR 	@{expected_header_col} 		Result: 	Error: 	Screenshot:
	Length Should Be 	${docx_tables}[6] 	${table_error_expected_length}
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[6][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_header_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_header_col}.
		END
	END
	# [0] equals first data row
	@{err_1_table_0} 	Convert To List 	${docx_tables}[6][0]
	VAR 	@{err_1_table_0_expected} 		Result: 	Odoo Create Sale 	Test: 	Odoo Sales 	Script: 	Odoo.robot 	Count: 	4
	Lists Should Be Equal 	${err_1_table_0_expected} 	${err_1_table_0}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_1_table_-1} 	Convert To List 	${docx_tables}[6][-1]
	VAR 	@{err_1_table_-1_expected} 		Screenshot: 	${EMPTY}
	Lists Should Be Equal 	${err_1_table_-1_expected} 	${err_1_table_-1}	msg=[ Expected != Converted ]
	# [10] equals quater row
	@{err_1_table_10} 	Convert To List 	${docx_tables}[6][10]
	VAR 	@{err_1_table_10_expected} 		Error: 	Text 'Scheduled Date' did not appear in 2 minutes. 	Count: 	2
	Lists Should Be Equal 	${err_1_table_10_expected} 	${err_1_table_10}	msg=[ Expected != Converted ]
	# [15] equals middle row
	@{err_1_table_15} 	Convert To List 	${docx_tables}[6][15]
	VAR 	@{err_1_table_15_expected} 		
	...    Result: 	Text 'Requests for Quotation' did not appear in 2 minutes. 	Test: 	Odoo Process RFQs 	Script: 	Odoo.robot 	Count: 	1
	Lists Should Be Equal 	${err_1_table_15_expected} 	${err_1_table_15}	msg=[ Expected != Converted ]
	# [20] equals upper middle row
	@{err_1_table_20} 	Convert To List 	${docx_tables}[6][20]
	VAR 	@{err_1_table_20_expected} 		Screenshot: 	${EMPTY}
	Lists Should Be Equal 	${err_1_table_20_expected} 	${err_1_table_20}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	21 Error Details No Screenshots
	Log 	Error Details Table content: ${docx_tables}[7]
	VAR 	${table_error_expected_length} 	22
	VAR 	@{expected_header_col} 		Result: 	Error:
	Length Should Be 	${docx_tables}[7] 	${table_error_expected_length}
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[7][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_header_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_header_col}.
		END
	END
	# [0] equals first data row
	@{err_2_table_0} 	Convert To List 	${docx_tables}[7][0]
	VAR 	@{err_2_table_0_expected} 		Result: 	Odoo Create Sale 	Test: 	Odoo Sales 	Script: 	Odoo.robot  Count: 	4
	Lists Should Be Equal 	${err_2_table_0_expected} 	${err_2_table_0}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_2_table_-1} 	Convert To List 	${docx_tables}[7][-1]
	VAR 	@{err_2_table_-1_expected} 		Error: 	Text 'Scheduled Date' did not appear in 2 minutes. 	Count: 	1
	Lists Should Be Equal 	${err_2_table_-1_expected} 	${err_2_table_-1}	msg=[ Expected != Converted ]
	# [5] equals quater row
	@{err_2_table_5} 	Convert To List 	${docx_tables}[7][5]
	VAR 	@{err_2_table_5_expected} 		Error: 	Text 'Inventory Overview' did not appear in 2 minutes. 	Count: 	3
	Lists Should Be Equal 	${err_2_table_5_expected} 	${err_2_table_5}	msg=[ Expected != Converted ]
	# [11] equals middle row
	@{err_2_table_11} 	Convert To List 	${docx_tables}[7][11]
	VAR 	@{err_2_table_11_expected} 		Error: 	Text 'Requests for Quotation' did not appear in 2 minutes. 	Count: 	1
	Lists Should Be Equal 	${err_2_table_11_expected} 	${err_2_table_11}	msg=[ Expected != Converted ]
	# [16] equals upper middle row
	@{err_2_table_16} 	Convert To List 	${docx_tables}[7][16]
	VAR 	@{err_2_table_16_expected} 		Result: 	Odoo Confirm RFQ 	Test: 	Odoo Process RFQs 	Script: 	Odoo.robot 	Count: 	1
	Lists Should Be Equal 	${err_2_table_16_expected} 	${err_2_table_16}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	22 Error Details No GBRN
	Log 	Error Details Table content: ${docx_tables}[8]
	VAR 	${table_error_expected_length} 	8
	VAR 	@{expected_header_col} 		Error: 	Screenshot:
	Length Should Be 	${docx_tables}[8] 	${table_error_expected_length}
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[8][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_header_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_header_col}.
		END
	END
	# [0] equals first data row
	@{err_3_table_0} 	Convert To List 	${docx_tables}[8][0]
	VAR 	@{err_3_table_0_expected} 		Error: 	Text 'New' did not appear in 2 minutes. 	Count: 	14
	Lists Should Be Equal 	${err_3_table_0_expected} 	${err_3_table_0}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_3_table_-1} 	Convert To List 	${docx_tables}[8][-1]
	VAR 	@{err_3_table_-1_expected} 		Screenshot: 	${EMPTY}
	Lists Should Be Equal 	${err_3_table_-1_expected} 	${err_3_table_-1}	msg=[ Expected != Converted ]
	# [4] equals middle row
	@{err_3_table_4} 	Convert To List 	${docx_tables}[8][4]
	VAR 	@{err_3_table_4_expected} 		Error: 	Text 'Requests for Quotation' did not appear in 2 minutes. 	Count: 	2
	Lists Should Be Equal 	${err_3_table_4_expected} 	${err_3_table_4}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	23 Error Details No GBET
	Log 	Error Details Table content: ${docx_tables}[9]
	VAR 	${table_error_expected_length} 	49
	VAR 	@{expected_header_col} 		Result: 	Error: 	Screenshot:
	Length Should Be 	${docx_tables}[9] 	${table_error_expected_length}
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[9][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_header_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_header_col}.
		END
	END
	# [0] equals first data row
	@{err_4_table_0} 	Convert To List 	${docx_tables}[9][0]
	VAR 	@{err_4_table_0_expected} 		Result: 	Odoo Create Sale 	Test: 	Odoo Sales 	Script: 	Odoo.robot 	Count: 	4
	Lists Should Be Equal 	${err_4_table_0_expected} 	${err_4_table_0}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_4_table_-1} 	Convert To List 	${docx_tables}[9][-1]
	VAR 	@{err_4_table_-1_expected} 		Screenshot: 	${EMPTY}
	Lists Should Be Equal 	${err_4_table_-1_expected} 	${err_4_table_-1}	msg=[ Expected != Converted ]
	# [12] equals quater row
	@{err_4_table_12} 	Convert To List 	${docx_tables}[9][12]
	VAR 	@{err_4_table_12_expected} 		Error: 	Text 'Salesperson' did not appear in 2 minutes.
	Lists Should Be Equal 	${err_4_table_12_expected} 	${err_4_table_12}	msg=[ Expected != Converted ]
	# [24] equals middle row
	@{err_4_table_24} 	Convert To List 	${docx_tables}[9][24]
	VAR 	@{err_4_table_24_expected} 		Error: 	Text 'Scheduled Date' did not appear in 2 minutes.
	Lists Should Be Equal 	${err_4_table_24_expected} 	${err_4_table_24}	msg=[ Expected != Converted ]
	# [36] equals upper middle row
	@{err_4_table_36} 	Convert To List 	${docx_tables}[9][36]
	VAR 	@{err_4_table_36_expected} 		Screenshot: 	${EMPTY}
	Lists Should Be Equal 	${err_4_table_36_expected} 	${err_4_table_36}	msg=[ Expected != Converted ]

	Dictionary Should Contain Key 	${docx_paragraphs} 	24 Error Details Polish Lang
	Log 	Error Details Table content: ${docx_tables}[10]
	VAR 	${table_error_expected_length} 	38
	VAR 	@{expected_header_col} 		Nazwa Wyniku: 	Błąd:
	Length Should Be 	${docx_tables}[10] 	${table_error_expected_length}
	FOR  ${i}  IN RANGE  0  ${table_error_expected_length}
		VAR 	${row} 		${docx_tables}[10][${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the Error Details Table!
		IF  '${row}[0]' not in @{expected_header_col}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${expected_header_col}.
		END
	END
	# [0] equals first data row
	@{err_5_table_0} 	Convert To List 	${docx_tables}[10][0]
	VAR 	@{err_5_table_0_expected} 		Nazwa Wyniku: 	Odoo Create Sale 	Test: 	Odoo Sales 	Skrypt:	Odoo.robot
	Lists Should Be Equal 	${err_5_table_0_expected} 	${err_5_table_0}	msg=[ Expected != Converted ]
	# [-1] equals last row
	@{err_5_table_-1} 	Convert To List 	${docx_tables}[10][-1]
	VAR 	@{err_5_table_-1_expected} 		Błąd: 	Text 'Scheduled Date' did not appear in 2 minutes.
	Lists Should Be Equal 	${err_5_table_-1_expected} 	${err_5_table_-1}	msg=[ Expected != Converted ]
	# [10] equals quater row
	@{err_5_table_10} 	Convert To List 	${docx_tables}[10][10]
	VAR 	@{err_5_table_10_expected} 		Nazwa Wyniku: 	Odoo Create Sale 	Test: 	Odoo Sales 	Skrypt: 	Odoo.robot
	Lists Should Be Equal 	${err_5_table_10_expected} 	${err_5_table_10}	msg=[ Expected != Converted ]
	# [19] equals middle row
	@{err_5_table_19} 	Convert To List 	${docx_tables}[10][19]
	VAR 	@{err_5_table_19_expected} 		Błąd: 	Button with locator 'Validate' not found.
	Lists Should Be Equal 	${err_5_table_19_expected} 	${err_5_table_19}	msg=[ Expected != Converted ]
	# [29] equals upper middle row
	@{err_5_table_29} 	Convert To List 	${docx_tables}[10][29]
	VAR 	@{err_5_table_29_expected} 		Błąd: 	Text 'Requests for Quotation' did not appear in 2 minutes.
	Lists Should Be Equal 	${err_5_table_29_expected} 	${err_5_table_29}	msg=[ Expected != Converted ]

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
