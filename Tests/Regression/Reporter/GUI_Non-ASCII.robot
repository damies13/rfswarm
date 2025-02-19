*** Settings ***
Test Tags 	windows-latest 	ubuntu-latest 	macos-latest 	Issue #97 	Languages 	GUI

Resource 	GUI_Common.robot
Variables 	${CURDIR}${/}testdata${/}Issue-#97${/}lang_samples.yaml

Suite Setup 	Set Platform
Test Setup 		Non-ASCII Test Setup
Test Template 	Test Non-ASCII Characters
Test Teardown 	Non-ASCII Test Teardown
Suite Teardown 	Copy Directory 	${test_data} 	${OUTPUT DIR}${/}results


*** Variables ***
${test_data} 		${CURDIR}${/}testdata${/}Issue-#97
${scenario_name} 	${None}
${results_dir} 		${None}


*** Test Cases ***
Latin 		pl
# Greek 		gr
# Cyrillic 	cy
# Armenian 	am
# Thai 		th
# Chinese (Simplified) 	zh
# Japanese 	ja
# Korean 		ko
# Arabic 		ar
# Tibetan  	ti


*** Keywords ***
Test Non-ASCII Characters
	[Documentation] 	Verify all fields handle UTF-8 correctly, especially non Latin characters.
	[Arguments] 	${langcode}
	Log 	\n\n\n> Testing: ${langcode} 	console=True

	VAR 	${sample} 	${Samples.${langcode}}
	#Set Test Variable 	${scenario_name} 	${langcode}_scenario
	Set Test Variable 	${results_dir} 		${test_data}${/}results
	Create Directory 	${results_dir}
	${template_file}= 	Create Language Files 	${langcode} 	${sample}

	Open GUI 	-g 	1 	-d 	${results_dir} 	-t 	${template_file}
	Wait For Status 	PreviewLoaded

	Log 	Test fields: 	console=${True}
	Take A Screenshot
	Set Text Value To Right Of 	Title 	${sample}
	Take A Screenshot
	Click Section 	Note
	Set Text Value To Right Of 	Heading 	${sample}
	Click Label With Vertical Offset 	Heading 	90
	Type 	${sample}
	Take A Screenshot
	Click Section	TestResultSummary
	Take A Screenshot  # get image*** vvv
	Set Text Value To Right Of 	ResultName 	${sample}
	#Click Section 	ScenarioPlan
	Take A Screenshot

	Log 	Test Template: 	console=${True}


	Log 	Test HTML DOCX XLSX Reports: 	console=${True}


	Check Logs

Non-ASCII Test Setup
	Change Reporter INI File Settings 	win_width 	1200
	Change Reporter INI File Settings 	win_height 	700

Non-ASCII Test Teardown
	Close GUI

Create Language Files
	[Arguments] 	${langcode} 	${sample}
	Create Directory 	${test_data}${/}files
	VAR 	${template_file} 	${test_data}${/}files${/}${sample}.template

	Copy File 	${test_data}${/}LANG_template.template 	${template_file}

	# Change __Lang__ With ${langcode} In ${robot_file}
	# Change __Lang_Sample__ With ${sample} In ${robot_file}
	# Change __LangRobot__ With ${robot_file} In ${scenario_file}
	# Change __LangTest__ With ${sample} Test Case In ${scenario_file}

	RETURN 	${template_file}

Check Logs
	${stdout_manager}= 		Read Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Read Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Read Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Read Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${stdout_manager} 	RuntimeError
	Should Not Contain 	${stderr_manager} 	RuntimeError
	Should Not Contain 	${stdout_manager} 	Exception
	Should Not Contain 	${stderr_manager} 	Exception
	Should Not Contain 	${stdout_manager}	OSError
	Should Not Contain 	${stderr_manager} 	OSError
	Should Not Contain 	${stdout_agent} 	RuntimeError
	Should Not Contain 	${stderr_agent} 	RuntimeError
	Should Not Contain 	${stdout_agent} 	Exception
	Should Not Contain 	${stderr_agent} 	Exception
	Should Not Contain 	${stdout_agent}		OSError
	Should Not Contain 	${stderr_agent} 	OSError
