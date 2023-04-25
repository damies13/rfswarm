*** Settings ***
Library 	OperatingSystem

Suite Setup			Clean Up Old Files

*** Test Cases ***
Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Reporter Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Reporter

Reporter Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -h
	Log to console 	${\n}${result}
	Should Contain	${result}	Excel

Command Line Generate HTML
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	HTML
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -n -d ${resultfolder} -t ${template} --html
	Log to console 	${\n}${result}
	Should Not Contain 	${result} 	Traceback
	Should Contain	${result}	html
	Should Exist	${resultfolder}${/}${resultdata}.html

Command Line Generate Docx
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	DOCX
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -n -d ${resultfolder} -t ${template} --docx
	Log to console 	${\n}${result}
	Should Not Contain 	${result} 	Traceback
	Should Contain	${result}	docx
	Should Exist	${resultfolder}${/}${resultdata}.docx

Command Line Generate Xlsx
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #144 	XLSX
	${testdata}= 	Set Variable    Issue-#144
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	${template}= 	Set Variable    ${basefolder}${/}90%ileTemplate.template
	Should Exist	${template}
	${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py -n -d ${resultfolder} -t ${template} --xlsx
	Log to console 	${\n}${result}
	Should Not Contain 	${result} 	Traceback
	Should Contain	${result}	xlsx
	Should Exist	${resultfolder}${/}${resultdata}.xlsx

*** Keywords ***
Clean Up Old Files
		[Tags]	ubuntu-latest 	macos-latest 	windows-latest
		# cleanup previous output
		Log To Console    ${OUTPUT DIR}
		Remove File    ${OUTPUT DIR}${/}*.txt
		Remove File    ${OUTPUT DIR}${/}*.png
		# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*
