*** Settings ***
Library 	OperatingSystem
Library 	Process

Suite Setup			Clean Up Old Files

*** Variables ***
${cmd_reporter} 		rfswarm-reporter
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

*** Test Cases ***
Robot Version
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Robot_Version} =	Evaluate	robot.__version__ 	modules=robot
	Log to console 	${\n}Robot Version: ${Robot_Version}

Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Reporter Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -v
	${result}= 	Run 	${cmd_reporter} -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Reporter

Reporter Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -h
	${result}= 	Run 	${cmd_reporter} -h
	Log to console 	${\n}${result}
	Should Contain	${result}	Excel

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

*** Keywords ***
Clean Up Old Files
		[Tags]	ubuntu-latest 	macos-latest 	windows-latest
		# cleanup previous output
		Log To Console    ${OUTPUT DIR}
		Remove File    ${OUTPUT DIR}${/}*.txt
		Remove File    ${OUTPUT DIR}${/}*.png
		# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*
