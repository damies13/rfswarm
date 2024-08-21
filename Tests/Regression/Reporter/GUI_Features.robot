*** Settings ***
Resource 	GUI_Common.robot

Test Teardown 	Close GUI

*** Test Cases ***
Reporter Command Line INI -i
	#[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${test_dir}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${ini_content}=		Get File	${test_dir}${/}RFSwarmReporter.ini
	${ini_content}=		Replace String	${ini_content}	template_here	${test_dir}${/}Issue-#14.template
	${ini_content}=		Replace String	${ini_content}	template_dir_here	${test_dir}
	Remove File		${test_dir}${/}RFSwarmReporter.ini
	Log		${ini_content}
	Append To File	${test_dir}${/}RFSwarmReporter.ini	${ini_content}

	Log To Console	Run Reporter with alternate ini file with variable: template = ${test_dir}${/}RFSwarmReporter.ini.
	Open GUI	-i	${test_dir}${/}RFSwarmReporter.ini
	Log To Console	Check that Robots section exist.
	${status}=	Run Keyword And Return Status
	...    Wait For	reporter_${platform}_section_robots.png 	timeout=${10}
	Take A Screenshot
	Run Keyword If	not ${status}	Fail
	...    msg=The Reporter did not load alternate ini file because it cannot find Robots section!

Manager Command Line DIR -d
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Open GUI	-n	-d 	${resultfolder}
	${inifile}=		Get Reporter INI Location
	${inifile_content}=		Get File		${inifile}
	${inifile_content}=		Split String	${inifile_content}

	${resultdir_offset}		Get Index From List 	${inifile_content}	resultdir
	Should Be Equal		resultdir	${inifile_content}[${resultdir_offset}]		msg=resultdir value is missing!
	Should Be Equal		${basefolder}		${inifile_content}[${resultdir_offset + 2}]
	...    msg=resultdir path value did not save correctly [settings != scenario]!

	${results_offset}		Get Index From List 	${inifile_content}	results
	Should Be Equal		results		${inifile_content}[${results_offset}]		msg=results value is missing!
	Should Be Equal		${resultfolder}${/}${resultdata}.db		${inifile_content}[${results_offset + 2}]
	...    msg=results path value did not save correctly [settings != scenario]!

Reporter Command Line TEMPLATE -t
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${basefolder}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${templatefile}=	Normalize Path	${basefolder}${/}Issue-#14.template

	Open GUI	-n	-t	${templatefile}
	${inifile}=		Get Reporter INI Location
	${inifile_content}=		Get File		${inifile}
	${inifile_content}=		Split String	${inifile_content}

	${template_offset}		Get Index From List 	${inifile_content}	template
	Should Be Equal		template	${inifile_content}[${template_offset}]		msg=template value is missing!
	${inifile_content}[${template_offset + 2}]=	Evaluate		r"${inifile_content}[${template_offset + 2}]".replace('x35', '#')
	Should Be Equal		${templatefile}		${inifile_content}[${template_offset + 2}]
	...    msg=template path value did not save correctly [settings != scenario]!

	${templatedir_offset}		Get Index From List 	${inifile_content}	templatedir
	Should Be Equal		templatedir		${inifile_content}[${templatedir_offset}]		msg=templatedir value is missing!
	${inifile_content}[${templatedir_offset + 2}]=	Evaluate		r"${inifile_content}[${templatedir_offset + 2}]".replace('x35', '#')
	Should Be Equal		${basefolder}		${inifile_content}[${templatedir_offset + 2}]
	...    msg=templatedir path value did not save correctly [settings != scenario]!

Manager Command Line HTML report --html
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Open GUI	-n	-d	${resultfolder}		--html
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.html

Manager Command Line HTML report --docx
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Open GUI	-n	-d	${resultfolder}		--docx
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.docx

Manager Command Line HTML report --xlsx
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Open GUI	-n	-d	${resultfolder}		--xlsx
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.xlsx

Verify That Files Get Saved With Correct Extension And Names
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #39 	Issue #257
	${testdata}=		Set Variable	Issue-#39
	${resultdata}=		Set Variable	20240622_182505_Issue-#39
	${basefolder}=		Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}=	Set Variable	${basefolder}${/}${resultdata}
	${templatefolder}=	Set Variable	${resultfolder}${/}template_dir
	${templatename}=	Set Variable	Issue-#39
	Change Reporter INI File Settings	templatedir		${templatefolder}

	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	basefolder: ${basefolder} 	console=True
	Log 	resultfolder: ${resultfolder} 	console=True
	Log To Console	Files to check: report file, report template, output files from reporter (html docx xlsx)

	Open GUI	-d 	${resultfolder}
	Click Button	savetemplate
	Save Template File OS DIALOG	${templatename}
	Click Button	generatehtml
	Sleep	2
	Click Button	generateword
	Sleep	2
	Click Button	generateexcel
	Sleep	2

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
	...    Close GUI

Whole report time range
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #138
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
	Open GUI	-d 	${resultfolder}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Wait For Status 	PreviewLoaded

	Click Section			Robots
	Click Tab 	 Preview

	# check the graph as expected
	Set Confidence		0.8
	Locate 	reporter_${platform}_graph_robots1.png
	Set Confidence		0.9

	Click Tab 	 Settings
	Click Section			Report

	# Set start time 14:20
	# Select Field With Label 	StartTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace
	# Type 	20
	${StartTime}= 	Get Text Value To Right Of 	StartTime
	${StartTime}= 	Replace String 	${StartTime} 	14:11 	14:20
	Set Text Value To Right Of 	StartTime 	${StartTime}

	# Set start time 14:58
	# Select Field With Label 	EndTime
	# Press Combination 	KEY.END
	# Press Combination 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace 	KEY.backspace
	# Type 	14:58
	${EndTime}= 	Get Text Value To Right Of 	EndTime
	${EndTime}= 	Replace String 	${EndTime} 	15:00 	14:58
	Set Text Value To Right Of 	EndTime 	${EndTime}

	# ${bounds}= 	Find Text 	Title:

	Select Field With Label 	Title

	Click Tab 	 Preview
	Wait For Status 	PreviewLoaded

	Sleep    10

	Wait For Status 	PreviewLoaded
	Click Section			Robots
	Wait For Status 	PreviewLoaded

	# check the graph as expected
	Set Confidence		0.8
	Locate 	reporter_${platform}_graph_robots2.png
	Set Confidence		0.9

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

	Open GUI	-d 	${resultfolder}
	Wait For Status 	PreviewLoaded
	Close GUI

	Should Exist	${basefolder}${/}result_backup${/}${resultdata}.db
	Remove File		${resultfolder}${/}${resultdata}.db

	Open GUI	-d 	${resultfolder}
	Sleep	10
	Click Section	test_result_summary
	Click	#double click needed. Maybe delete after eel module implemetation

	${status}=	Run Keyword And Return Status
	...    Wait For	reporter_${platform}_option_datatable.png 	timeout=${30}
	Run Keyword If	not ${status}	Fail	msg=Reporter is not responding!

	[Teardown]	Run Keywords
	...    Copy File	${basefolder}${/}result_backup${/}${resultdata}.db	${resultfolder}		AND
	...    Remove File	${basefolder}${/}result_backup${/}${resultdata}.db						AND
	...    Close GUI
