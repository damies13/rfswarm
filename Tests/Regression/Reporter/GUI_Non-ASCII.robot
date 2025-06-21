*** Settings ***
Test Tags 	windows-latest 	ubuntu-latest 	macos-latest 	Issue #97 	Languages

Resource 	../Common/GUI_Common.resource
Resource 	resources/GUI_Reporter.resource

Variables 	${CURDIR}${/}testdata${/}Issue-#97${/}lang_samples.yaml

Suite Setup 	Non-ASCII Suite Setup
Test Setup 		Non-ASCII Test Setup
Test Template 	Test Non-ASCII Characters
Test Teardown 	Non-ASCII Test Teardown
Suite Teardown 	Non-ASCII Suite Teardown

*** Variables ***
${test_data} 		${CURDIR}${/}testdata${/}Issue-#97
${scenario_name} 	${None}


*** Test Cases ***
Latin 		pl
Icelandic 	ic
Greek 		gr
Cyrillic 	cy
Armenian 	am
Thai 		th
Chinese (Simplified) 	zh
Japanese 	ja
Korean 		ko
Arabic 		ar
Tibetan  	ti


*** Keywords ***
Test Non-ASCII Characters
	[Documentation] 	Verify all fields handle UTF-8 correctly, especially non Latin characters.
	[Arguments] 	${langcode}
	Log 	\n\n\n> Testing: ${langcode} 	console=True
	VAR 	${sample} 	${Samples.${langcode}}
	${template_file}= 	Create Language Files 	${langcode} 	${sample}
	${manager_results} 	Choose Language Manager Result DB 	${langcode}

	Open GUI 	-g 	1 	-d 	${manager_results} 	-t 	${template_file}
	Wait For Status 	PreviewLoaded


	Log 	Test fields: 	console=${True}

	Set Text Value To Right Of 	Title 	${sample} 	offsetx=100
	Take A Screenshot

	Click Section 	Note
	VAR 	${note_sample_heading} 	${sample} Note
	Set Text Value To Right Of 	Heading 	${note_sample_heading}
	Click Label With Vertical Offset 	Heading 	90
	Evaluate 	clipboard.copy("${sample}") 	modules=clipboard
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.v
	ELSE
		Press Combination	KEY.ctrl		KEY.v
	END
	Take A Screenshot
	Click Tab 	Preview
	Click Tab 	Settings

	Click Section	TestResultSummary
	VAR 	${data_table_sample_heading} 	${sample} TestResultSummary
	Set Text Value To Right Of 	Heading 	${data_table_sample_heading}
	Sleep 	3
	Set Text Value To Right Of 	ResultName 	${sample} 	offsetx=70
	Take A Screenshot
	Click Tab 	Preview
	Click Tab 	Settings

	Click Section 	DataGraph
	VAR 	${graph_sample_heading} 	${sample} DataGraph
	Set Text Value To Right Of 	Heading 	${graph_sample_heading}
	Take A Screenshot
	Click Tab 	Preview
	Click Tab 	Settings

	Click Section 	Errors
	VAR 	${errors_sample_heading} 	${sample} Errors
	Set Text Value To Right Of 	Heading 	${errors_sample_heading}
	Take A Screenshot
	Click Tab 	Preview
	Click Tab 	Settings

	Click Button 	SaveTemplate
	Sleep 	10

	Log 	Test Template: 	console=${True}
	${template_content} 	Get File 	${template_file}
	Should Contain 	${template_content} 	title = ${sample}
	Should Contain 	${template_content} 	name = ${note_sample_heading}
	Should Contain 	${template_content} 	name = ${data_table_sample_heading}
	Should Contain 	${template_content} 	col_result_name = ${sample}
	Should Contain 	${template_content} 	filterpattern = ${sample} Keyword
	Should Contain 	${template_content} 	name = ${graph_sample_heading}
	Should Contain 	${template_content} 	name = ${errors_sample_heading}

	Log 	Test HTML DOCX? XLSX? Reports: 	console=${True}
	Click Button	generatehtml
	Sleep 	1
	@{files} 	List Files In Directory 	${manager_results} 	pattern=*.html 	absolute=${True}
	VAR 	${html_file} 	${files}[0]
	Wait Until Created 	${html_file}	timeout=9 minutes

	VAR 	${Cover} 	${${langcode} Cover} 	scope=TEST
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}

	Verify HTML Cover Page 	${html}

	VAR 	${section} 	${note_sample_heading}
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	${langcode} Note
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj}

	VAR 	${section} 	Table of Contents
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	${langcode} Contents
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}

	VAR 	${section} 	${data_table_sample_heading}
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	${langcode} Table
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Filter TestResultSummary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	${langcode} Filter Table
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${html_img_path} 	${manager_results}${/}html_images
	VAR 	${html_expected_img_path} 	${test_data}${/}html_images
	VAR 	${img_comp_threshold} 	0.7
	VAR 	${move_tolerance} 	30
	VAR 	${section} 	${graph_sample_heading}
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	VAR 	${section} 	${langcode} graph
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	${errors_sample_heading}
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	VAR 	${section} 	${langcode} Errors
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

Non-ASCII Suite Setup
	Remove Directory 	${OUTPUT DIR}${/}results${/}Issue-#97 	recursive=${True}
	GUI_Common.GUI Suite Initialization Reporter
	Extract Zip File 	${test_data}${/}manager_results.zip 	${test_data}

Non-ASCII Suite Teardown
	Copy Directory 		${test_data} 	${OUTPUT DIR}${/}results${/}Issue-#97
	Remove File 	${OUTPUT DIR}${/}results${/}Issue-#97${/}manager_results.zip
	Remove Directory 	${test_data}${/}files 	recursive=${True}
	Remove Directory 	${test_data}${/}manager_results 	recursive=${True}

Non-ASCII Test Setup
	Change Reporter INI File Settings 	win_width 	1200
	Change Reporter INI File Settings 	win_height 	700

Non-ASCII Test Teardown
	Close GUI
	Check Logs

Choose Language Manager Result DB
	[Arguments] 	${langcode}
	VAR 	${manager_results} 	${test_data}${/}manager_results
	@{manager_results}= 	List Directories In Directory 	${manager_results} 	absolute=${True}
	FOR  ${result}  IN  @{manager_results}
		@{splitted_path}= 	Split String From Right 	${result} 	separator=_ 	max_split=2
		VAR 	${result_langcode} 	${splitted_path}[-2]
		IF  '${result_langcode}' == '${langcode}'
			RETURN 	${result}
		END
	END

	Fail 	Can't find manager results directory with the specified language code.
	
Create Language Files
	[Arguments] 	${langcode} 	${sample}
	Create Directory 	${test_data}${/}files
	VAR 	${template_file} 	${test_data}${/}files${/}${sample}.template

	Copy File 	${test_data}${/}LANG_template.template 	${template_file}

	Change __Lang__ With ${langcode} In ${template_file}
	Change __Lang_Sample__ With ${sample} In ${template_file}

	RETURN 	${template_file}
