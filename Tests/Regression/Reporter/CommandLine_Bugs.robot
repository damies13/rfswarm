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

*** Test Cases ***
Command Line Generate HTML
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	HTML
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
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --html
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --html
	Log 	result: ${\n}${result} 	console=True
	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.html

Command Line Generate Docx
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	DOCX
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
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --docx
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --docx
	Log 	${\n}${result} 	console=True
	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.docx

Command Line Generate Xlsx
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	XLSX
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
	# ${result}=	Run 	python3 ${pyfile} -n -g 1 -d ${resultfolder} -t ${template} --xlsx
	${result}= 	Run 	${cmd_reporter} -n -g 1 -d ${resultfolder} -t ${template} --xlsx
	Log 	${\n}${result} 	console=True
	Should Not Contain 	${result} 	Traceback
	Should Exist	${resultfolder}${/}${resultdata}.xlsx