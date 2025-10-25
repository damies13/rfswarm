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
	Take A Screenshot
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
	Take A Screenshot
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

	${status}=	Run Keyword And Return Status
	...    Wait For	reporter_${PLATFORM}_label_title.png 	timeout=${30}
	Run Keyword If	not ${status}	Fail	msg=Reporter is not responding!

	[Teardown]	Run Keywords
	...    Copy File	${basefolder}${/}result_backup${/}${resultdata}.db	${resultfolder}		AND
	...    Remove File	${basefolder}${/}result_backup${/}${resultdata}.db						AND
	...    Close Reporter GUI

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
	Remove File 	${resultfile}
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile} 	-g 	2
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

	Take A Screenshot
	Select Field With Label 	DataType

	# Take A Screenshot
	Select Option 	Plan
	Sleep 	5s

	# Take A Screenshot
	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Click Tab 	 Preview

	# Take A Screenshot

	${pvinfo}= 	Get Python Version Info

	Take A Screenshot
	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		VAR 	${plannototal_img} 	reporter_${PLATFORM}_graph_plannototal_py3.9.png
	ELSE
		VAR 	${plannototal_img} 	reporter_${PLATFORM}_graph_plannototal.png
	END
	Wait For 	${plannototal_img} 	timeout=30
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
	Remove File 	${resultfile}
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile} 	-g  2
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
	Sleep 	5s

	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Select Field With Label 	ShowTotal
	Sleep 	5s

	# Take A Screenshot
	Wait For Status 	PreviewLoaded

	# Take A Screenshot
	Click Tab 	 Preview

	# Take A Screenshot

	${pvinfo}= 	Get Python Version Info

	Set Confidence		0.7
	IF 	${pvinfo.minor} < 10 and "${PLATFORM}" == "ubuntu"
		VAR 	${plantotal_img} 	reporter_${PLATFORM}_graph_plantotal_py3.9.png
	ELSE
		VAR 	${plantotal_img} 	reporter_${PLATFORM}_graph_plantotal.png
	END
	Wait For 	${plantotal_img} 	timeout=30
	Set Confidence		0.9

	[Teardown]	Run Keywords
	...    Take A Screenshot 		AND
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
	Remove File 	${resultfile}
	Should Not Exist 	${resultfile}

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
	...    Take A Screenshot 		AND
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
	Remove File 	${resultfile}
	Should Not Exist	${resultfile}

	# pass a default ini file with extended height to ensure that default values are used
	Open Reporter GUI 	-d 	${resultfolder} 	-i 	${basefolder}${/}RFSwarmReporter.ini 	-t 	${templatefile}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Sleep 	5s
	Take A Screenshot
	Wait For Status 	PreviewLoaded

	Click Section			Report

	Wait For Status 	PreviewLoaded

	# Take A Screenshot

	# Scenario Plan
	Click Section			ScenarioPlan

	Wait For Status 	PreviewLoaded

	Click Tab 	 Preview

	Take A Screenshot

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

Verify Agent Filter Metric For Data Table
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #121
	[Setup] 	Set Reporter INI Window Size 	height=600
	VAR 	${issue} 			Issue-#121
	VAR 	${result_name} 		20250917_164531_filter_agent
	VAR 	${test_data} 		${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_dir} 		${test_data}${/}${result_name}
	VAR 	${result_db} 		${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_metric
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d  ${result_db}  -t  ${template_dir}  -g  2
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot
	Click Section 	ScenarioPlan
	Sleep 	1
	Take A Screenshot

	GROUP  Validating data for "TEST_1" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_1
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Tables: 	console=${True}
		VAR 	${section} 	Scenario Plan
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Agent Filter Data Table METRIC 1
		Run Keyword And Continue On Failure
		...    Verify HTML Report Table Content
		...    ${section} 	${section_obj}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_DataTable_METRIC_1.html
		Remove File 	${html_file}
	END

	GROUP  Validating data for "TEST_2" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_2
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Tables: 	console=${True}
		VAR 	${section} 	Scenario Plan
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Agent Filter Data Table METRIC 2
		Run Keyword And Continue On Failure
		...    Verify HTML Report Table Content
		...    ${section} 	${section_obj}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_DataTable_METRIC_2.html
		Remove File 	${html_file}
	END

	[Teardown] 	Run Keywords
	...    Set Confidence 	${CONFIDENCE} 	AND
	...    Close Reporter GUI 	AND
	...    Remove Directory 	${CURDIR}${/}testdata${/}Issue-#121${/}${result_name} 	recursive=${true}

Verify Agent Filter Results For Data Table
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #121
	[Setup] 	Set Reporter INI Window Size 	height=600
	VAR 	${issue} 			Issue-#121
	VAR 	${result_name} 		20250917_164531_filter_agent
	VAR 	${test_data} 		${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_dir} 		${test_data}${/}${result_name}
	VAR 	${result_db} 		${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d  ${result_db}  -t  ${template_dir}  -g  2
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot
	Click Section 	TestResultSummary
	Sleep 	1
	Take A Screenshot

	GROUP  Validating data for "TEST_1" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_1
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Tables: 	console=${True}
		VAR 	${section} 	Test Result Summary
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Agent Filter Data Table RESULTS 1
		Run Keyword And Continue On Failure
		...    Verify HTML Report Table Content
		...    ${section} 	${section_obj}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_DataTable_RESULTS_1.html
		Remove File 	${html_file}
	END

	GROUP  Validating data for "TEST_2" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_2
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Tables: 	console=${True}
		VAR 	${section} 	Test Result Summary
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Agent Filter Data Table RESULTS 2
		Run Keyword And Continue On Failure
		...    Verify HTML Report Table Content
		...    ${section} 	${section_obj}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_DataTable_RESULTS_2.html
		Remove File 	${html_file}
	END

	[Teardown] 	Run Keywords
	...    Set Confidence 	${CONFIDENCE} 	AND
	...    Close Reporter GUI 	AND
	...    Remove Directory 	${CURDIR}${/}testdata${/}Issue-#121${/}${result_name} 	recursive=${true}

Verify Agent Filter Metric For Graph
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #121
	[Setup] 	Set Reporter INI Window Size 	height=600
	VAR 	${issue} 			Issue-#121
	VAR 	${result_name} 		20250917_164531_filter_agent
	VAR 	${test_data} 		${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_dir} 		${test_data}${/}${result_name}
	VAR 	${result_db} 		${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_metric
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d  ${result_db}  -t  ${template_dir}  -g  2
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot
	Click Section 	Robots
	Sleep 	1
	Take A Screenshot

	GROUP  Validating data for "TEST_1" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_1
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Graphs: 	console=${True}
		VAR 	${section} 	Robots
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Filter Robots METRIC 1
		Run Keyword And Continue On Failure
		...    Verify HTML Report Graph
		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_METRIC_1.html
		Remove File 	${html_file}
	END

	GROUP  Validating data for "TEST_2" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_2
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Graphs: 	console=${True}
		VAR 	${section} 	Robots
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Filter Robots METRIC 2
		Run Keyword And Continue On Failure
		...    Verify HTML Report Graph
		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_METRIC_2.html
		Remove File 	${html_file}
	END

	[Teardown] 	Run Keywords
	...    Set Confidence 	${CONFIDENCE} 	AND
	...    Close Reporter GUI 	AND
	...    Remove Directory 	${CURDIR}${/}testdata${/}Issue-#121${/}${result_name} 	recursive=${true}

Verify Agent Filter Results For Graph
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #121
	[Setup] 	Set Reporter INI Window Size 	height=600
	VAR 	${issue} 			Issue-#121
	VAR 	${result_name} 		20250917_164531_filter_agent
	VAR 	${test_data} 		${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_dir} 		${test_data}${/}${result_name}
	VAR 	${result_db} 		${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.9
	VAR 	${move_tolerance} 			0

	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

	Open Reporter GUI 	-d  ${result_db}  -t  ${template_dir}  -g  2
	Wait For Status 	PreviewLoaded
	Sleep 	1
	Take A Screenshot
	Click Section 	DataGraph
	Sleep 	1
	Take A Screenshot

	GROUP  Validating data for "TEST_1" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_1
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Graphs: 	console=${True}
		VAR 	${section} 	Data Graph
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Filter Data Graph RESULTS 1
		Run Keyword And Continue On Failure
		...    Verify HTML Report Graph
		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_RESULTS_1.html
		Remove File 	${html_file}
	END

	GROUP  Validating data for "TEST_2" Agent
		Click Label With Horizontal Offset 	FilterAgent 	140
		Take A Screenshot
		Set Confidence 	${0.96}
		Select Option 	TEST_2
		Set Confidence 	${CONFIDENCE}
		Sleep 	3
		Click Tab 	Preview
		Take A Screenshot
		Click Tab 	Settings

		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
		Click Button 	generatehtml
		Wait Until Created 	${html_file} 	timeout=9 minutes
		${html} 	Parse HTML File 	${html_file}

		Log 	\nVerifying Graphs: 	console=${True}
		VAR 	${section} 	Data Graph
		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
		VAR 	${section} 	Filter Data Graph RESULTS 2
		Run Keyword And Continue On Failure
		...    Verify HTML Report Graph
		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_RESULTS_2.html
		Remove File 	${html_file}
	END

	[Teardown] 	Run Keywords
	...    Set Confidence 	${CONFIDENCE} 	AND
	...    Close Reporter GUI 	AND
	...    Remove Directory 	${CURDIR}${/}testdata${/}Issue-#121${/}${result_name} 	recursive=${true}

# AGENT FILTER FOR ERROR DETAILS ARE NOT AVAILABLE
#
# Verify Agent Filter Results For Error Details
# 	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #121
# 	[Setup] 	Set Reporter INI Window Size 	height=600
# 	VAR 	${issue} 			Issue-#121
# 	VAR 	${result_name} 		20250917_164531_filter_agent
# 	VAR 	${test_data} 		${CURDIR}${/}testdata${/}${issue}
# 	VAR 	${result_dir} 		${test_data}${/}${result_name}
# 	VAR 	${result_db} 		${result_dir}${/}${result_name}.db
# 	VAR 	${template_name} 	filter_error
# 	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

# 	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
# 	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
# 	VAR 	${img_comp_threshold} 		0.9
# 	VAR 	${move_tolerance} 			0

# 	Extract Zip File 	${test_data}${/}results.zip 	${test_data}

# 	Open Reporter GUI 	-d  ${result_db}  -t  ${template_dir}  -g  1
# 	Wait For Status 	PreviewLoaded
# 	Sleep 	1
# 	Take A Screenshot
# 	Click Section 	Errors
# 	Sleep 	1
# 	Take A Screenshot

# 	GROUP  Validating data for "TEST_1" Agent
# 		Click Label With Horizontal Offset 	FilterAgent 	140
# 		Take A Screenshot
# 		Set Confidence 	${0.96}
# 		Select Option 	TEST_1
# 		Set Confidence 	${CONFIDENCE}
# 		Sleep 	3
# 		Click Tab 	Preview
# 		Take A Screenshot
# 		Click Tab 	Settings

# 		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
# 		Click Button 	generatehtml
# 		Wait Until Created 	${html_file} 	timeout=9 minutes
# 		${html} 	Parse HTML File 	${html_file}

# 		Log 	\nVerifying Graphs: 	console=${True}
# 		VAR 	${section} 	Data Graph
# 		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
# 		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
# 		VAR 	${section} 	Filter Data Graph RESULTS 1
# 		Run Keyword And Continue On Failure
# 		...    Verify HTML Report Graph
# 		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

# 		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_RESULTS_1.html
# 		Remove File 	${html_file}
# 	END

# 	GROUP  Validating data for "TEST_2" Agent
# 		Click Label With Horizontal Offset 	FilterAgent 	140
# 		Take A Screenshot
# 		Set Confidence 	${0.96}
# 		Select Option 	TEST_2
# 		Set Confidence 	${CONFIDENCE}
# 		Sleep 	3
# 		Click Tab 	Preview
# 		Take A Screenshot
# 		Click Tab 	Settings

# 		VAR 	${html_file} 	${result_dir}${/}${result_name}.html
# 		Click Button 	generatehtml
# 		Wait Until Created 	${html_file} 	timeout=9 minutes
# 		${html} 	Parse HTML File 	${html_file}

# 		Log 	\nVerifying Graphs: 	console=${True}
# 		VAR 	${section} 	Data Graph
# 		${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
# 		Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
# 		VAR 	${section} 	Filter Data Graph RESULTS 2
# 		Run Keyword And Continue On Failure
# 		...    Verify HTML Report Graph
# 		...    ${section}  ${section_obj}  ${html_expected_img_path}  ${html_img_path}  ${img_comp_threshold}  ${move_tolerance}

# 		Copy File 		${html_file} 	${OUTPUT_DIR}${/}${issue}${/}${result_name}_Graph_RESULTS_2.html
# 		Remove File 	${html_file}
# 	END

# 	[Teardown] 	Run Keywords
#	...    Set Confidence 	${CONFIDENCE} 	AND
# 	...    Close Reporter GUI 	AND
# 	...    Remove Directory 	${CURDIR}${/}testdata${/}Issue-#121${/}${result_name} 	recursive=${true}

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

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

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

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

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

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

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

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

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
	VAR 	${issue} 		Issue-#105
	VAR 	${test_data} 	${CURDIR}${/}testdata${/}${issue}
	VAR 	${result_name} 	20250501_103943_example
	VAR 	${result_dir} 	${test_data}${/}${result_name}
	VAR 	${result_db} 	${result_dir}${/}${result_name}.db
	VAR 	${template_name} 	filter_result
	VAR 	${template_dir} 	${test_data}${/}${template_name}.template

	VAR 	${html_img_path} 			${OUTPUT_DIR}${/}${issue}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 		0.7
	VAR 	${move_tolerance} 			30

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
	Remove File 	${resultfile}
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
	Remove File 	${resultfile}
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
	Remove File 	${resultfile}
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
