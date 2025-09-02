*** Settings ***
Resource 	resources/GUI_Reporter.resource
Resource 	resources/Reporter_DOCX.resource
Resource 	resources/Reporter_HTML.resource
Resource 	resources/Reporter_XLSX.resource

Resource 	../../Common/Directories_and_Files.resource
Resource 	../../Common/Logs.resource
Resource 	../../Common/INI_PIP_Data.resource
Resource 	../../Common/GUI_RFS_Components.resource

Suite Setup 	GUI_Common.GUI Suite Initialization Reporter
Test Teardown 	Close Reporter GUI

*** Test Cases ***
Verify That Files Get Saved With Correct Extension And Names
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #39 	Issue #257
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	${testdata}=		Set Variable	Issue-#39
	${resultdata}=		Set Variable	20240622_182505_Issue-#39
	${basefolder}=		Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}=	Set Variable	${basefolder}${/}${resultdata}
	${templatefolder}=	Set Variable	${resultfolder}${/}template_dir
	${templatename}=	Set Variable	Issue-#39
	Create Reporter INI File If It Does Not Exist
	Change Reporter INI Option 	Reporter 	templatedir 	${templatefolder}

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder: ${resultfolder} 	console=True
	Log To Console	Files to check: report file, report template, output files from reporter (html docx xlsx)

	Open Reporter GUI	-d 	${resultfolder}
	Click Button	savetemplate
	Save Template File OS DIALOG	${templatename}
	Click Button	generateword
	Sleep	2
	Click Button	generateexcel
	Sleep	2
	Click Button	generatehtml
	Sleep	2

	Wait For Status 	SavedXHTMLReport

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
	...    Close Reporter GUI

Whole report time range
	[Tags]	ubuntu-latest 	windows-latest 	Issue #138
	# [Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #138
	# This test stopped working on macos a week before go live, for some reason imagehorizon is no longer
	# 	able to send keystoked to the main UI screen, this needs further investigation
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
	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Robots
	# Take A Screenshot
	Click Tab 	 Preview
	# Take A Screenshot

	${pvinfo}= 	Get Python Version Info

	# check the graph as expected
	# Take A Screenshot
	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_robots1_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_robots1.png
	END
	Set Confidence		0.9

	Click Tab 	 Settings
	# Take A Screenshot
	Click Section			Report

	# Take A Screenshot

	# ${title}= 	Get Text Value To Right Of 	Title

	# Take A Screenshot
	# Set start time 14:20
	# Select Field With Label 	StartTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace
	# Type 	20
	# ${StartTime}= 	Set Variable    2023-09-28 14:20
	${StartTime}= 	Get Text Value To Right Of 	StartTime
	${StartTime}= 	Replace String 	${StartTime} 	14:11 	14:20
	Set Text Value To Right Of 	StartTime 	${StartTime}
	# Take A Screenshot

	# Take A Screenshot
	Select Field With Label 	Title 		150
	Wait For Status 	PreviewLoaded
	# Take A Screenshot
	# Set start time 14:58
	# Select Field With Label 	EndTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace
	# Type 	14:58
	# ${EndTime}= 	Set Variable    2023-09-28 14:58
	${EndTime}= 	Get Text Value To Right Of 	EndTime
	${EndTime}= 	Replace String 	${EndTime} 	15:00 	14:58
	Set Text Value To Right Of 	EndTime 	${EndTime}
	Take A Screenshot

	# Take A Screenshot
	# ${bounds}= 	Find Text 	Title:

	Select Field With Label 	Title 		150

	Click Tab 	 Preview
	Wait For Status 	PreviewLoaded

	# Sleep    10
	#
	# Wait For Status 	PreviewLoaded
	Click Section			Robots
	Wait For Status 	PreviewLoaded

	# check the graph as expected
	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_robots2_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_robots2.png
	END
	Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI

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

	Open Reporter GUI	-d 	${resultfolder}
	Wait For Status 	PreviewLoaded
	Close Reporter GUI

	Should Exist	${basefolder}${/}result_backup${/}${resultdata}.db
	Remove File		${resultfolder}${/}${resultdata}.db

	Open Reporter GUI	-d 	${resultfolder}
	Sleep	10
	Click Section	test_result_summary
	Click	#double click needed. Maybe delete after eel module implemetation

	${status}=	Run Keyword And Return Status
	...    Wait For	reporter_${PLATFORM}_option_datatable.png 	timeout=${30}
	Run Keyword If	not ${status}	Fail	msg=Reporter is not responding!

	[Teardown]	Run Keywords
	...    Copy File	${basefolder}${/}result_backup${/}${resultdata}.db	${resultfolder}		AND
	...    Remove File	${basefolder}${/}result_backup${/}${resultdata}.db						AND
	...    Close Reporter GUI

Verify the Content Of the HTML Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #36 	HTML 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${html_file}		${resultfolder}${/}${resultdata}.html
	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#36${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Log 	template: ${template_dir} 	console=True
	Open Reporter GUI	-d 	${resultfolder} 	-t 	${template_dir}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=300
	Take A Screenshot
	Click Button	generatehtml
	Wait Until Created 	${html_file}	timeout=9 minutes
	Close Reporter GUI

	Log To Console	Verification of saved data in the RFSwarm HTML report started.
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}

	Verify HTML Cover Page 	${html}

	VAR 	${section} 	This is Heading
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}

	VAR 	${section} 	Contents graphs
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}

	VAR 	${section} 	Contents tables
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section} 		Note
	VAR 	${break_at} 	h2
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj} 	${break_at}

	VAR 	${section} 	Second Note
	VAR 	${break_at} 	h3
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section} 	heading=h2
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj} 	${break_at}

	VAR 	${section} 	Third Note
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section} 	heading=h3
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj}


	# Graphs - when new graphs are required, save them using the function in save_html_image.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph Left Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result FAIL
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result Total TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph LR Combined
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result TotalTPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table ResultSummary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Polish Lang
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No Screenshots
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No GBRN
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No GBET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details Polish Lang
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	[Teardown] 	Run Keywords
	...    Close Reporter GUI	AND
	...    Move File 	${html_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.html

Verify the Content Of the DOCX Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #38 	DOCX 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${docx_file}		${resultfolder}${/}${resultdata}.docx
	VAR 	${docx_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}docx_images
	VAR 	${docx_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#38${/}docx_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Log 	template: ${template_dir} 	console=True
	Open Reporter GUI	-d 	${resultfolder} 	-t 	${template_dir}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=300
	Take A Screenshot
	Click Button	generateword
	Wait Until Created 	${resultfolder}${/}${resultdata}.docx	timeout=9 minutes
	Close Reporter GUI

	Log To Console	Verification of saved data in the RFSwarm DOCX report started.
	File Should Exist 	${docx_file}
	&{docx_data} 	Read DOCX File 	${docx_file}
	Log 	${docx_data}

	Verify DOCX Cover Page 	${docx_data}

	VAR 	${section} 	This is Heading
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}

	VAR 	${section} 	Contents graphs
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}

	VAR 	${section} 	Contents tables
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section} 		Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section} 	custom=${True}

	VAR 	${section} 		Second Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section}

	VAR 	${section} 		Third Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section}


	# Graphs - when new graphs are required, save them using the function in read_docx.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 		Data Graph Left Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result FAIL
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result Total TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Right Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Right Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph LR Combined
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result TotalTPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table ResultSummary
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section} 	custom=${True}

	VAR 	${section} 	Data Table Polish Lang
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No Screenshots
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No GBRN
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No GBET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details Polish Lang
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	[Teardown] 	Run Keywords
	...    Close Reporter GUI	AND
	...    Move File 	${docx_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx

Verify the Content Of the XLSX Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #37 	XLSX 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${xlsx_file}		${resultfolder}${/}${resultdata}.xlsx
	VAR 	${xlsx_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}xlsx_images
	VAR 	${xlsx_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#37${/}xlsx_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Log 	template: ${template_dir} 	console=True
	Open Reporter GUI	-d 	${resultfolder} 	-t 	${template_dir}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=300
	Take A Screenshot
	Click Button	generateexcel
	Wait Until Created 	${xlsx_file}	timeout=9 minutes
	Close Reporter GUI

	Log To Console	Verification of saved data in the RFSwarm XLSX report started.
	File Should Exist 	${xlsx_file}
	@{xlsx_sheets}= 	Read All Xlsx Sheets 	${xlsx_file}
	Log		${xlsx_sheets}

	Verify XLSX Cover Page 	${xlsx_file}

	VAR 	${section} 	This is Heading
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Contents graphs
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Contents tables
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section1} 	Note
	VAR 	${section2} 	Second Note
	VAR 	${section3} 	Third Note
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section1}
	${sheet_number} 	Get Substring 	${xlsx_sheet} 	0 	1

	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section1}" section.
	Verify XLSX Report Notes 	${xlsx_file} 	${section1} 	${xlsx_sheet} 	stop_at=${sheet_number}.1 ${section2} 	custom=${True}

	Verify XLSX Report Notes 	${xlsx_file} 	${section2} 	${xlsx_sheet} 	start_at=${sheet_number}.1 ${section2} 	stop_at=${sheet_number}.1.1 ${section3}

	Verify XLSX Report Notes 	${xlsx_file} 	${section3} 	${xlsx_sheet} 	start_at=${sheet_number}.1.1 ${section3}


	# Graphs - when new graphs are required, save them using the function in read_xlsx.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph Left Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result FAIL
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result Total TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph LR Combined
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result TotalTPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table ResultSummary
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	custom=${True}

	VAR 	${section} 	Data Table Polish Lang
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No Screenshots
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No GBRN
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No GBET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details Polish Lang
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	[Teardown] 	Run Keywords
	...    Close Reporter GUI	AND
	...    Move File 	${xlsx_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.xlsx

Verify Plan Graph - No Total
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #140
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	${templatefile}= 	Set Variable    ${basefolder}${/}original_base.template
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Create New Section 		Issue #140

	Click Section			Issue#140

	Select Field With Label 	Type

	# Take A Screenshot
	Select Option 	DataGraph
	# Take A Screenshot

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	DataType

	# Take A Screenshot
	Select Option 	Plan

	# Take A Screenshot
	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Click Tab 	 Preview

	# Take A Screenshot

	${pvinfo}= 	Get Python Version Info

	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_plannototal_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_plannototal.png
	END
	Set Confidence		0.9


	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}


Verify Plan Graph - With Total
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #140
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	${templatefile}= 	Set Variable    ${basefolder}${/}original_base.template
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Create New Section 		Issue #140

	Click Section			Issue#140

	Select Field With Label 	Type

	# Take A Screenshot
	Select Option 	DataGraph
	# Take A Screenshot

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	DataType

	# Take A Screenshot
	Select Option 	Plan

	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	ShowTotal

	# Take A Screenshot
	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Click Tab 	 Preview

	# Take A Screenshot

	${pvinfo}= 	Get Python Version Info

	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_plantotal_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_plantotal.png
	END
	Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Verify Plan Table
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #141
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	${templatefile}= 	Set Variable    ${basefolder}${/}original_base.template
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Create New Section 		Issue #141

	Click Section			Issue#141

	Select Field With Label 	Type

	# Take A Screenshot
	Select Option 	DataTable
	# Take A Screenshot

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	DataTypeWide

	# Take A Screenshot
	Select Option 	Plan

	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	ShowGraphColours

	# Take A Screenshot
	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Click Tab 	 Preview

	Take A Screenshot

	Set Confidence		0.7
	Locate 	reporter_${PLATFORM}_table_plan.png
	Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Change Line Colour
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #307
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#307
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	${templatefile}= 	Set Variable    ${basefolder}${/}Issue-#307.template
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Wait For Status 	PreviewLoaded

	# Take A Screenshot

	# Scenario Plan
	Click Section			ScenarioPlan

	Wait For Status 	PreviewLoaded

	Click Tab 	 Preview

	${pvinfo}= 	Get Python Version Info
	# Locate 	reporter_${PLATFORM}_graph_plancolourb4.png
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_plancolourb4_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_plancolourb4.png
	END

	Click Button 		ColourSales

	# Sleep 	1
	Take A Screenshot

	# Original colour : aa4c4f
	Choose Colour With OS Colour Picker 		0088ff		# Mid blue
	# Choose Colour With OS Colour Picker 		DA8801 	# Mid orange


	Wait For Status 	PreviewLoaded

	Take A Screenshot

	# Locate 	reporter_${PLATFORM}_graph_plancolourafter.png
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		Locate 	reporter_${PLATFORM}_graph_plancolourafter_py3.9.png
	ELSE
		Locate 	reporter_${PLATFORM}_graph_plancolourafter.png
	END
	# bring window to foreground so teardown works	reporter_ubuntu_status_previewloaded
	Click Image 	reporter_${PLATFORM}_status_previewloaded.png

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Change Font
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #148
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}Issue-#148
	VAR 	${result_name} 	20250327_221800_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_dir} 	${test_data}${/}font_test.template

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}
	IF 	"${PLATFORM}" == "ubuntu" # impact font is not available in ubuntu
		VAR 	${font_name} 	Standard Symbols PS
		Change Impact With ${font_name} In ${template_dir}
		${test} 	Get File 	${template_dir}
		Log 	${test}
	ELSE
		VAR 	${font_name} 	Impact
	END

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1 	--html 	--docx 	--xlsx
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	1
	Take A Screenshot
	VAR 	${img} 	reporter_${PLATFORM}_customfont_title.png
	Wait For 	${img} 	 timeout=30
	Take A Screenshot

	Click Section 	Note
	Sleep 	1
	Take A Screenshot
	VAR 	${img} 	reporter_${PLATFORM}_customfont_heading.png
	Wait For 	${img} 	 timeout=30
	VAR 	${img} 	reporter_${PLATFORM}_customfont_note.png
	Wait For 	${img} 	 timeout=30

	Click Section 	Table_of_Contents
	Sleep 	1
	Take A Screenshot
	VAR 	${img} 	reporter_${PLATFORM}_customfont_contents.png
	Wait For 	${img} 	 timeout=30

	Click Section	TestResultSummary
	Sleep 	1
	Take A Screenshot
	VAR 	${img} 	reporter_${PLATFORM}_customfont_tabledata.png
	Wait For 	${img} 	 timeout=30

	Click Section 	DataGraph
	Sleep 	1
	Take A Screenshot
	${pvinfo}= 	Get Python Version Info
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		VAR 	${img} 	reporter_${PLATFORM}_customfont_graph_py3.9.png
	ELSE
		VAR 	${img} 	reporter_${PLATFORM}_customfont_graph.png
	END
	Wait For 	${img} 	 timeout=30

	Click Section 	Errors
	Sleep 	1
	Take A Screenshot
	VAR 	${img} 	reporter_${PLATFORM}_customfont_errors.png
	Wait For 	${img} 	 timeout=30


	${docx_font} 	Get Default Font Name From Document 	${result_dir}${/}${result_name}.docx
	Should Be Equal 	${docx_font} 	${font_name}

	${xlsx_font} 	Get Font Name From Xlsx Sheet 	${result_dir}${/}${result_name}.xlsx 	Cover
	Should Be Equal 	${xlsx_font} 	${font_name}

	${html_content} 	Get File 	${result_dir}${/}${result_name}.html
	Should Contain 	${html_content} 	font-family: "${font_name}"

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

# Verify Agent Filter Metric For Data Table and Graph
# 	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #217 	robot:continue-on-failure
# 	[Setup] 	Change Reporter INI File Settings 	win_height 	600
# 	VAR 	${test_data} 	${CURDIR}${/}testdata${/}Issue-#105
# 	VAR 	${result_name} 	20250501_103943_example
# 	VAR 	${result_dir} 	${test_data}${/}${result_name}
# 	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
# 	VAR 	${template_name} 	filter_metric
# 	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

# 	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}html_images
# 	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#105${/}html_images
# 	VAR 	${img_comp_threshold} 	0.7
# 	VAR 	${move_tolerance} 		30

# 	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

# 	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
# 	Wait For Status 	PreviewLoaded
# 	Sleep 	1
# 	Take A Screenshot

# 	# Enable filters:
# 	Click Section 	Robots
# 	Sleep 	1
# 	Take A Screenshot
# 	Click Label With Horizontal Offset 	FilterAgent 	140
# 	Take A Screenshot
# 	Select Option 	TEST_1
# 	Sleep 	3
# 	Click Tab 	Preview
# 	Take A Screenshot
# 	Click Tab 	Settings


# 	# HTML:
# 	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
# 	Click Button 	generatehtml
# 	Wait Until Created 	${html_file} 	timeout=9 minutes

# 	Log 	\nVerifying Graphs: 	console=${True}
# 	VAR 	${section} 	Robots
# 	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
# 	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
# 	VAR 	${section} 	Filter Robots METRIC 1
# 	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

Verify Filter Metric For Data Table and Graph - Wildcard
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #105 	robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${issue} 	Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_metric
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}${issue}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot

 	# Enable filters:
	Click Section	TestResultSummary
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	Wildcard
	VAR 	${filter} 	*21*
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings
	Click Section 	DataGraph
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	Wildcard
	VAR 	${filter} 	*21*
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings


	# HTML:
	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
	Click Button 	generatehtml
	Wait Until Created 	${html_file} 	timeout=9 minutes

	Log To Console	Verification of saved data in the RFSwarm HTML report started [ METRIC 1. ].
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Test Result Summary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	Filter Test Result Summary METRIC 1
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	Filter Data Graph METRIC 1
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	Copy File 	${result_dir}${/}${result_name}.html 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_METRIC_1.html
	Remove File 	${result_dir}${/}${result_name}.html

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

Verify Filter Metric For Data Table and Graph - Not Wildcard
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #105 	robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${issue} 	Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_metric
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}${issue}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot


	# Enable filters:
	Click Section	TestResultSummary
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	NotWildcard
	VAR 	${filter} 	*Keyword *2
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings
	Click Section 	DataGraph
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	NotWildcard
	VAR 	${filter} 	*Keyword *2
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings

	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
	Click Button 	generatehtml
	Wait Until Created 	${html_file} 	timeout=9 minutes

	# HTML:
	Log To Console	Verification of saved data in the RFSwarm HTML report started [ METRIC 2. ].
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Test Result Summary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	Filter Test Result Summary METRIC 2
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	Filter Data Graph METRIC 2
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	Copy File 	${result_dir}${/}${result_name}.html 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_METRIC_2.html
	Remove File 	${result_dir}${/}${result_name}.html

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

Verify Filter Result For Data Table and Graph - Wildcard
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #105 	robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${issue} 	Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}${issue}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot

 	# Enable filters:
	Click Section	TestResultSummary
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	Wildcard
	VAR 	${filter} 	*21*
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings
	Click Section 	DataGraph
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	Wildcard
	VAR 	${filter} 	*21*
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings


	# HTML:
	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
	Click Button 	generatehtml
	Wait Until Created 	${html_file} 	timeout=9 minutes

	Log To Console	Verification of saved data in the RFSwarm HTML report started [ RESULT 1. ].
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Test Result Summary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	Filter Test Result Summary RESULT 1
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	Filter Data Graph RESULT 1
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	Copy File 	${result_dir}${/}${result_name}.html 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_RESULT_1.html
	Remove File 	${result_dir}${/}${result_name}.html

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

Verify Filter Result For Data Table and Graph - Not Wildcard
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #105 	robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${issue} 	Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}${issue}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot


	# Enable filters:
	Click Section	TestResultSummary
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	NotWildcard
	VAR 	${filter} 	*Keyword *2
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings
	Click Section 	DataGraph
	Sleep 	1
	Click Label With Horizontal Offset 	FilterType 	120
	Take A Screenshot
	Select Option 	NotWildcard
	VAR 	${filter} 	*Keyword *2
	Set Text Value To Right Of 	FilterPattern 	${filter} 	offsetx=120
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings

	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
	Click Button 	generatehtml
	Wait Until Created 	${html_file} 	timeout=9 minutes

	# HTML:
	Log To Console	Verification of saved data in the RFSwarm HTML report started [ RESULT 2. ].
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Test Result Summary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	Filter Test Result Summary RESULT 2
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	Filter Data Graph RESULT 2
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	Copy File 	${result_dir}${/}${result_name}.html 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_RESULT_2.html
	Remove File 	${result_dir}${/}${result_name}.html

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

Verify Filter Result For Data Table and Graph - Filter Result
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #105 	robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Create Reporter INI File If It Does Not Exist 	AND
	...    Set Reporter INI Window Size 	height=600
	VAR 	${issue} 	Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}${issue}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 		30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d 	${result_db} 	-t 	${template_dir} 	-g 	1
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot


	# Enable filters:
	Click Section	TestResultSummary
	Sleep 	1
	Take A Screenshot
	Click Label With Horizontal Offset 	FilterResult 	120
	Sleep 	1
	Take A Screenshot
	Select Option 	Fail
	Sleep 	1
	Click Label With Vertical Offset 	Enabled 	42 	# enable filter
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings
	Click Section 	DataGraph
	Sleep 	1
	Take A Screenshot
	Click Label With Horizontal Offset 	FilterResult 	120
	Sleep 	1
	Take A Screenshot
	Select Option 	Fail
	Sleep 	1
	Click Label With Vertical Offset 	Enabled 	42 	# enable filter
	Sleep 	2
	Take A Screenshot
	Click Tab 	Preview
	Sleep 	2
	Take A Screenshot
	Click Tab 	Settings

	VAR 	${html_file} 	${result_dir}${/}${result_name}.html
	Click Button 	generatehtml
	Wait Until Created 	${html_file} 	timeout=9 minutes

	# HTML:
	Log To Console	Verification of saved data in the RFSwarm HTML report started [ RESULT 3. ].
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Test Result Summary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	Filter Test Result Summary RESULT 3
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	Filter Data Graph RESULT 3
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	Copy File 	${result_dir}${/}${result_name}.html 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_RESULT_3.html
	Remove File 	${result_dir}${/}${result_name}.html

	[Teardown] 	Run Keywords
	...    Close Reporter GUI 	AND 	Remove Directory 	${result_dir} 	recursive=${True}

Check Reporter with JSON Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${configfile}= 	Set Variable    ${basefolder}${/}RFSwarmReporter-JSON.json

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-i 	${configfile}

	Sleep    10s
	Take A Screenshot
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	SelectResultFile	 	60

	Take A Screenshot

	# Set Confidence		0.7
	Locate 	reporter_${PLATFORM}_windowsize_json.png
	# Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI

Check Reporter with Yaml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${configfile}= 	Set Variable    ${basefolder}${/}RFSwarmReporter-Yaml.yaml

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-i 	${configfile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	SelectResultFile

	Take A Screenshot

	# Set Confidence		0.7
	Locate 	reporter_${PLATFORM}_windowsize_yaml.png
	# Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI

Check Reporter with yml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None
	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${configfile}= 	Set Variable    ${basefolder}${/}RFSwarmReporter-yml.yml

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-i 	${configfile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	SelectResultFile

	Take A Screenshot

	# Set Confidence		0.7
	Locate 	reporter_${PLATFORM}_windowsize_yml.png
	# Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI

Check Reporter with JSON Template File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None

	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${templatefile}= 	Set Variable    ${basefolder}${/}template-JSON.json


	${testdata2}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder2}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata2}
	Should Exist	${basefolder2}
	Log to console 	basefolder2: ${basefolder2} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder2}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Take A Screenshot

	Click Section			Issue#172-json

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Check Reporter with Yaml Template File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None

	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${templatefile}= 	Set Variable    ${basefolder}${/}template-Yaml.yaml


	${testdata2}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder2}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata2}
	Should Exist	${basefolder2}
	Log to console 	basefolder2: ${basefolder2} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder2}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Take A Screenshot

	Click Section			Issue#172-Yaml

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Check Reporter with yml Template File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Make Clipboard Not None

	${testdata}= 	Set Variable    Issue-#172
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${templatefile}= 	Set Variable    ${basefolder}${/}template-yml.yml


	${testdata2}= 	Set Variable    Issue-#140
	${resultdata}= 	Set Variable    20230728_130340_Odoo-demo
	${basefolder2}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata2}
	Should Exist	${basefolder2}
	Log to console 	basefolder2: ${basefolder2} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder2}${/}${resultdata}
	${resultfile}= 	Set Variable    ${basefolder}${/}${resultdata}${/}${resultdata}.report
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Take A Screenshot

	Click Section			Issue#172-yml

	[Teardown]	Run Keywords
	...    Set Confidence 	0.9 	AND
	...    Close Reporter GUI 		AND
	...    Remove File 		${resultfile}

Check Application Icon or Desktop Shortcut in GUI
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	${result}= 	Run 	${cmd_reporter} -g 6 -c ICON
	Log 		${result}
	Sleep    1

	Navigate to and check Desktop Icon

	[Teardown]	Type 	KEY.ESC 	KEY.ESC 	KEY.ESC

#
