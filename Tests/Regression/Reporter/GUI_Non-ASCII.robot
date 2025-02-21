*** Settings ***
Test Tags 	windows-latest 	ubuntu-latest 	macos-latest 	Issue #97 	Languages

Resource 	GUI_Common.robot
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

	#Set Text Value To Right Of 	Title 	${sample}
	Take A Screenshot

	Click Section 	Note
	VAR 	${note_sample_heading} 	${sample} Note
	Set Text Value To Right Of 	Heading 	${note_sample_heading}
	Click Label With Vertical Offset 	Heading 	90
	Type 	${sample}
	Take A Screenshot

	Click Section	TestResultSummary
	VAR 	${data_table_sample_heading} 	${sample} TestResultSummary
	Set Text Value To Right Of 	Heading 	${data_table_sample_heading}
	Take A Screenshot  # get image*** vvv
	Set Text Value To Right Of 	ResultName 	${sample} 	offsetx=100
	Take A Screenshot

	Click Section 	DataGraph
	VAR 	${graph_sample_heading} 	${sample} DataGraph
	Set Text Value To Right Of 	Heading 	${graph_sample_heading}
	Take A Screenshot

	Click Section 	Errors
	VAR 	${errors_sample_heading} 	${sample} Errors
	Set Text Value To Right Of 	Heading 	${errors_sample_heading}
	Take A Screenshot
	# K all section headings
	# K preview Table of Contents for section headings (html)
	# filter for graphs and data table (Metric and Agent name)
	# Error details

	Log 	Test Template: 	console=${True}


	Log 	Test HTML DOCX? XLSX? Reports: 	console=${True}
	# preview Table of Contents

	Check Logs

Non-ASCII Suite Setup
	Remove Directory 	${OUTPUT DIR}${/}results${/}Issue-#97 	recursive=${True}
	Set Platform
	Extract Zip File 	${test_data}${/}manager_results.zip 	${test_data}

Non-ASCII Suite Teardown
	Copy Directory 		${test_data} 	${OUTPUT DIR}${/}results${/}Issue-#97
	Remove Directory 	${test_data}${/}files 	recursive=${True}
	Remove Directory 	${test_data}${/}manager_results 	recursive=${True}

Non-ASCII Test Setup
	Change Reporter INI File Settings 	win_width 	1200
	Change Reporter INI File Settings 	win_height 	700

Non-ASCII Test Teardown
	Close GUI

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

Check Logs
	${stdout_reporter}= 		Read Log 	${OUTPUT DIR}${/}stdout.txt
	${stderr_reporter}= 		Read Log 	${OUTPUT DIR}${/}stderr.txt

	Should Not Contain 	${stdout_reporter} 	RuntimeError
	Should Not Contain 	${stderr_reporter} 	RuntimeError
	Should Not Contain 	${stdout_reporter} 	Exception
	Should Not Contain 	${stderr_reporter} 	Exception
	Should Not Contain 	${stdout_reporter}	OSError
	Should Not Contain 	${stderr_reporter} 	OSError
