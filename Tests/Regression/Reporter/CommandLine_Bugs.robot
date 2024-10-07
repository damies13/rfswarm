*** Settings ***
Resource 	CommandLine_Common.robot


*** Test Cases ***
Check If The Not Buildin Modules Are Included In The Reporter Setup File
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	${imports}	Get Modules From Program .py File That Are Not BuildIn
	...    ${CURDIR}..${/}..${/}..${/}..${/}rfswarm_reporter${/}rfswarm_reporter.py

	Log	${imports}

	${requires}	Get Install Requires From Setup File
	...    ${CURDIR}..${/}..${/}..${/}..${/}setup-reporter.py

	Log	${requires}

	FOR  ${i}  IN  @{imports}
		Run Keyword And Continue On Failure
		...    Should Contain	${requires}	${i}
		...    msg="Some modules are not in Reporter setup file"
	END

Auto Generate HTML Report Without GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	Issue #132 	HTML
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	Log 	template: ${template} 	console=True
	Log To Console	Run Reporter with cutom template and generate html report.
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --html
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --html
	Log 	result: ${\n}${result} 	console=True

	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.html
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.html
	${html_content}= 	Get File 	${resultfolder}${/}${resultdata}.html
	Should Contain 	${html_content} 	<title>quickdemo</title>
	Should Contain 	${html_content} 	<h1>8 Issue-#132</h1>
	Should Contain 	${html_content} 	<div class="body"><p>This is a test for Issue-#132</p></div>

	[Teardown] 	Move File 	${resultfolder}${/}${resultdata}.html 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.html

Auto Generate DOCX Report Without GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	Issue #132 	DOCX
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	Log 	template: ${template} 	console=True
	Log To Console	Run Reporter with cutom template and generate docx report.
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --docx
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --docx
	Log 	result: ${\n}${result} 	console=True

	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.docx
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.docx

	[Teardown] 	Move File 	${resultfolder}${/}${resultdata}.docx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx

Auto Generate XLSX Report Without GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	Issue #132 	XLSX
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	Log 	template: ${template} 	console=True
	Log To Console	Run Reporter with cutom template and generate xlsx report.
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --xlsx
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --xlsx
	Log 	result: ${\n}${result} 	console=True

	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.xlsx
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.xlsx

	[Teardown] 	Move File 	${resultfolder}${/}${resultdata}.xlsx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.xlsx

Generate Reports With Unsupported Characters
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #305 	HTML 	DOCX 	XLSX
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata}= 		Issue-#305
	VAR 	${resultdata}= 		20241006_111707_AUT_Linux_ssh_scenario
	VAR 	${basefolder}= 		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder}= 	${basefolder}${/}${resultdata}
	VAR 	${template}= 	${basefolder}${/}sample.template

	Should Exist	${basefolder}
	Log 	basefolder: ${basefolder} 	console=True
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	Should Exist	${template}
	Log 	template: ${template} 	console=True

	Log To Console	Run Reporter with cutom template and generate html, docx, xlsx reports.
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --html --docx --xlsx
	Log 	result: ${\n}${result} 	console=True

	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.html
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.html
	Should Exist	${resultfolder}${/}${resultdata}.docx
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.docx
	Should Exist	${resultfolder}${/}${resultdata}.xlsx
	File Should Not Be Empty 	${resultfolder}${/}${resultdata}.xlsx

	[Teardown] 	Run Keywords
	...    Move File 	${resultfolder}${/}${resultdata}.html 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.html	AND
	...    Move File 	${resultfolder}${/}${resultdata}.docx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx	AND
	...    Move File 	${resultfolder}${/}${resultdata}.xlsx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.xlsx
