*** Settings ***
Resource 	GUI_Common.robot
Library 	XML 	use_lxml=True

Suite Setup 	Set Platform
Test Teardown 	Close GUI

*** Test Cases ***
Verify If Reporter Runs With Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Run Keywords
	...    Open GUI		AND
	...    Sleep	5	AND
	...    Close GUI

	${location}=	Get Reporter Default Save Path
	File Should Exist	${location}${/}RFSwarmReporter.ini
	File Should Not Be Empty	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with existing ini file.
	Open GUI
	Wait For Status 	PreviewLoaded
	TRY
		Click Section	test_result_summary
		Click	#double click needed. Maybe delete after eel module implemetation
		Wait For	reporter_${platform}_option_datatable.png 	timeout=${60}
	EXCEPT
		Fail	msg=Reporter is not responding!
	END

Verify If Reporter Runs With No Existing INI File From Current Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Reporter Default Save Path
	Remove File		${location}${/}RFSwarmReporter.ini
	File Should Not Exist	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with no existing ini file.
	Open GUI
	Wait For Status 	SelectResultFile
	TRY
		Click Section	test_result_summary
		Click	#double click needed. Maybe delete after eel module implemetation
		Wait For	reporter_${platform}_option_datatable.png 	timeout=${30}
	EXCEPT
		Fail	msg=Reporter is not responding!
	END

Verify If Reporter Runs With Existing INI File From Previous Version
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Reporter Default Save Path
	Remove File		${location}${/}RFSwarmReporter.ini
	File Should Not Exist	${location}${/}RFSwarmReporter.ini
	${v1_0_0_inifile}=		Normalize Path		${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmReporter.ini
	Copy File	${v1_0_0_inifile}		${location}
	File Should Exist	${location}${/}RFSwarmReporter.ini
	File Should Not Be Empty	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with existing ini file.
	Open GUI
	Wait For Status 	SelectResultFile
	TRY
		Click Section	test_result_summary
		Click	#double click needed. Maybe delete after eel module implemetation
		Wait For	reporter_${platform}_option_datatable.png 	timeout=${30}
	EXCEPT
		Fail	msg=Reporter is not responding!
	END
	Close GUI

	[Teardown] 	Run Keywords
	...    Remove File 	${location}${/}RFSwarmReporter.ini 	AND
	...    Open GUI 	AND
	...    Sleep 	5 	AND
	...    Close GUI

Verify If Reporter Runs With Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Reporter Default Save Path
	Open GUI	-n
	${result}= 	Wait For Process 	${process} 	timeout=60
	Check Result 	${result}

	File Should Exist	${location}${/}RFSwarmReporter.ini
	File Should Not Be Empty	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with existing ini file.
	Open GUI	-n
	${result}= 	Wait For Process 	${process} 	timeout=60
	Check Result 	${result}

Verify If Reporter Runs With No Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Reporter Default Save Path
	Remove File		${location}${/}RFSwarmReporter.ini
	File Should Not Exist	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with no existing ini file.

	Open GUI	-n
	${result}= 	Wait For Process 	${process} 	timeout=60
	Check Result 	${result}

Verify If Reporter Runs With Existing INI File From Previous Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49

	${location}=	Get Reporter Default Save Path
	Remove File		${location}${/}RFSwarmReporter.ini
	File Should Not Exist	${location}${/}RFSwarmReporter.ini
	${v1_0_0_inifile}=		Normalize Path		${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmReporter.ini
	Copy File	${v1_0_0_inifile}		${location}
	File Should Exist	${location}${/}RFSwarmReporter.ini
	File Should Not Be Empty	${location}${/}RFSwarmReporter.ini
	Log To Console	Running Reporter with existing ini file.

	Open GUI	-n
	${result}= 	Wait For Process 	${process} 	timeout=60
	Check Result 	${result}

	[Teardown] 	Run Keywords
	...    Remove File 	${location}${/}RFSwarmReporter.ini 	AND
	...    Open GUI 	-n

First Run
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #147
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#147
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	${epoch}=	Get Time	epoch
	Open GUI	-i 	blank_${epoch}.ini 	-d 	${resultfolder}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded
	# Close GUI

New Data Table Section
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #149 	Issue #150
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	${testdata}= 	Set Variable    Issue-#147
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Open GUI 	-d 	${resultfolder}
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded
	# Click Section			toc
	# This should click Report
	Click Section			Report
	# Click Text			toc 	0 	-20
	# Click To The Below Of Image 	reporter_${platform}_button_removesection.png 	20

	Take A Screenshot

	Click Button 			AddSection

	Click To The Below Of Image 	reporter_${platform}_label_sectionname.png 	20
	Type 	Issue #149
	Click Button 			OK
	Take A Screenshot
	Click Section			Issue#149

	Select Field With Label 	Type

	Select Option 	DataTable

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	Select Field With Label 	ShowGraphColours

	Select Field With Label 	DataTypeWide

	Select Option 	Result

	Select Field With Label 	ResultType

	Select Option 	ResponseTime

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	# click Generate HTML as partial regression test for Issue #150
	Click Button 	GenerateHTML

	# Wait For Status 	GeneratingXHTMLReport

	Wait For Status 	SavedXHTMLReport

	# Close GUI


Template with Start and End Dates
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #250
	Log To Console 	${\n}TAGS: ${TEST TAGS}

	${testdata}=		Set Variable	Issue-#250
	${basefolder}=		Set Variable	${CURDIR}${/}testdata${/}${testdata}

	${resultdata0}=		Set Variable	20240626_130059_jpetstore-nomon-quick
	${resultfolder0}=	Set Variable	${basefolder}${/}${resultdata0}

	${resultdata1}=		Set Variable	20240626_130756_jpetstore-nomon-quick
	${resultfolder1}=	Set Variable	${basefolder}${/}${resultdata1}

	${templatename}=	Set Variable	Issue-#250
	${templatefolder}=	Set Variable	${OUTPUT DIR}${/}${templatename}${/}template_dir

	${testresultfolder0}=	Set Variable	${OUTPUT DIR}${/}${templatename}${/}${resultdata0}
	${testresultfolder1}=	Set Variable	${OUTPUT DIR}${/}${templatename}${/}${resultdata1}

	Change Reporter INI File Settings	templatedir		${templatefolder}
	Create Directory		${templatefolder}

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder0: ${resultfolder0} 	console=True
	Log 	resultfolder1: ${resultfolder1} 	console=True
	Log To Console	Open Reporter with resultfolder0 and create template

	Open GUI	-d 	${resultfolder0}
	Wait For Status 	PreviewLoaded

	# change the start and end times
	Click Section			Report
	# Take A Screenshot

	Take A Screenshot
	Make Clipboard Not None
	${StartTime}= 	Get Text Value To Right Of 	StartTime
	${StartTime}= 	Replace String 	${StartTime} 	03:00 	03:01
	Set Text Value To Right Of 	StartTime 	${StartTime}

	# Take A Screenshot
	Select Field With Label 	Title 		150
	Wait For Status 	PreviewLoaded
	# Take A Screenshot

	${EndTime}= 	Get Text Value To Right Of 	EndTime
	${EndTime}= 	Replace String 	${EndTime} 	03:03 	03:02
	Wait For Status 	PreviewLoaded
	Set Text Value To Right Of 	EndTime 	${EndTime}
	# Take A Screenshot


	Select Field With Label 	Title 		150
	Wait For Status 	PreviewLoaded
	# Take A Screenshot


	# switch to preview tab

	Click Tab 	 Preview

	Click Section			TestResultSummary
	# Wait For Status 	PreviewLoaded
	# Take A Screenshot

	Click Button	savetemplate
	Save Template File OS DIALOG	${templatename}

	Click Button 	GenerateHTML
	# Wait For Status 	GeneratingXHTMLReport
	Wait For Status 	SavedXHTMLReport
	Sleep    1
	Close GUI

	Copy Files 	${resultfolder0}/*.report 	${testresultfolder0}
	Copy Files 	${resultfolder0}/*.html 	${testresultfolder0}

	# ${html}= 	Parse XML 		${resultfolder0}${/}${resultdata0}.html
	# import lxml.etree
	# tree = lxml.etree.parse("/home/dave/Downloads/Reporter-windows-latest-3.11/Issue-#250/20240626_130059_jpetstore-nomon-quick/20240626_130059_jpetstore-nomon-quick.html", lxml.etree.HTMLParser())
	${html}= 	Evaluate 			lxml.etree.parse(r'${resultfolder0}${/}${resultdata0}.html', lxml.etree.HTMLParser()) 	modules=lxml.etree
	# ${rawhtml}= 	Get File 	${resultfolder0}${/}${resultdata0}.html
	# ${html}= 	Evaluate 			lxml.etree.fromstring('${rawhtml}', lxml.etree.HTMLParser()) 	modules=lxml.etree
	# ${sectionid}= 		Get Element Attribute 	${html} 	id 	.//h1[text()='2 Test Result Summary']/..
	# ${sectionid}= 		Get Element Attribute 	${html} 	id 	.//h1[text()='4 Test Result Summary']/..
	${sectionid}= 		Get Element Attribute 	${html} 	id 	//h1[contains(text(), 'Test Result Summary')]/..
	# FB9D1A0486F		//div[@id='FB9D1A0486F']//table
	${table}= 		Get Element 	${html} 	//div[@id='${sectionid}']//table
	${expected}= 	Get Elements Texts 	${table} 	tr/td[1]

	Log To Console	Open Reporter with resultfolder1 and check template works

	Open GUI	-d 	${resultfolder1}	-t 	${templatefolder}${/}${templatename}.template
	Wait For Status 	PreviewLoaded

	Click Button 	GenerateHTML
	Wait For Status 	SavedXHTMLReport

	Copy Files 	${resultfolder1}/*.report 	${testresultfolder1}
	Copy Files 	${resultfolder1}/*.html 	${testresultfolder1}

	# ${html}= 	Parse XML 		${resultfolder1}${/}${resultdata1}.html
	# ${html}= 	Evaluate 			lxml.etree.parse("${resultfolder1}${/}${resultdata1}.html", lxml.etree.HTMLParser()) 	modules=lxml.etree
	${html}= 	Evaluate 			lxml.etree.parse(r'${resultfolder1}${/}${resultdata1}.html', lxml.etree.HTMLParser()) 	modules=lxml.etree
	# ${rawhtml}= 	Get File 	${resultfolder1}${/}${resultdata1}.html
	# ${html}= 	Evaluate 			lxml.etree.fromstring('${rawhtml}', lxml.etree.HTMLParser()) 	modules=lxml.etree
	# ${sectionid}= 		Get Element Attribute 	${html} 	id 	.//h1[text()='2 Test Result Summary']/..
	${sectionid}= 		Get Element Attribute 	${html} 	id 	//h1[contains(text(), 'Test Result Summary')]/..
	${table}= 		Get Element 	${html} 	.//div[@id='${sectionid}']//table
	FOR 	${index}    ${item}    IN ENUMERATE    @{expected}
		${row}= 	Evaluate    ${index} + 2
		${txt}= 	Get Element Text 	${table} 	tr[${row}]/td[1]
		Should Be Equal As Strings    ${item}    ${txt}
	END

	Click Tab 	 Preview

	Click Section			TestResultSummary
	# Take A Screenshot
	Wait For 	reporter_${platform}_expected_testresultsummary.png 	 timeout=30

Auto Generate HTML Report With GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #132 	HTML

	VAR 	${testdata}			Issue-#132
	VAR 	${resultdata}		sample_results
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}

	Log To Console	Run Reporter with cutom template and generate html report.
	${template_dir}=		Normalize Path	${basefolder}${/}Issue-#132.template
	Open GUI	-d 	${resultfolder} 	-t 	${template_dir} 	--html
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=10
	Close GUI
	@{html_files}=		List Files In Directory		${resultfolder} 	absolute=True 	pattern=*.html
	Log To Console	${\n}All result files: ${html_files}${\n}
	Length Should Be 	${html_files} 	1

	File Should Not Be Empty 	${html_files}[0]
	${html_content}= 	Get File 	${html_files}[0]
	Should Contain 	${html_content} 	<title>Report for Issue-#132</title>
	Should Contain 	${html_content} 	<h1>4 Issue-#132</h1>
	Should Contain 	${html_content} 	<div class="body"><p>This is a test for Issue-#132</p></div>

	[Teardown] 	Run Keywords
	...    Close GUI	AND
	...    Move File 	${resultfolder}${/}${resultdata}.html 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.html

Auto Generate DOCX Report With GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #132 	DOCX

	VAR 	${testdata}			Issue-#132
	VAR 	${resultdata}		sample_results
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}

	Log To Console	Run Reporter with cutom template and generate docx report.
	${template_dir}=		Normalize Path	${basefolder}${/}Issue-#132.template
	Open GUI	-d 	${resultfolder} 	-t 	${template_dir} 	--docx
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=10
	Close GUI
	@{docx_files}=		List Files In Directory		${resultfolder} 	absolute=True 	pattern=*.docx
	Log To Console	${\n}All result files: ${docx_files}${\n}
	Length Should Be 	${docx_files} 	1

	File Should Not Be Empty 	${docx_files}[0]

	[Teardown] 	Run Keywords
	...    Close GUI	AND
	...    Move File 	${resultfolder}${/}${resultdata}.docx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx

Auto Generate XLSX Report With GUI Using Template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #132 	XLSX

	VAR 	${testdata}			Issue-#132
	VAR 	${resultdata}		sample_results
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}

	Log To Console	Run Reporter with cutom template and generate xlsx report.
	${template_dir}=		Normalize Path	${basefolder}${/}Issue-#132.template
	Open GUI	-d 	${resultfolder} 	-t 	${template_dir} 	--xlsx
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded	timeout=10
	Close GUI
	@{xlsx_files}=		List Files In Directory		${resultfolder} 	absolute=True 	pattern=*.xlsx
	Log To Console	${\n}All result files: ${xlsx_files}${\n}
	Length Should Be 	${xlsx_files} 	1

	File Should Not Be Empty 	${xlsx_files}[0]

	[Teardown] 	Run Keywords
	...    Close GUI	AND
	...    Move File 	${resultfolder}${/}${resultdata}.xlsx 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.xlsx
