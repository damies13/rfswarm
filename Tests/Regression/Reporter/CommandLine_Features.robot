*** Settings ***
Resource 	resources/CommandLine_Reporter.resource

Suite Setup 	Common.Basic Suite Initialization Reporter

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	${result}= 	Run 	${cmd_reporter} -g 6 -c ICON
	Log 		${result}
	Sleep    1
	Check Icon Install

Reporter Command Line INI -i
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${testdata}			Issue-#14${/}result_dir
	VAR 	${resultdata}		ini_testcase
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}

	${test_dir}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${ini_content}=		Get File	${test_dir}${/}RFSwarmReporter.ini
	${ini_content}=		Replace String	${ini_content}	template_here	${test_dir}${/}Issue-#14.template
	${ini_content}=		Replace String	${ini_content}	template_dir_here	${test_dir}
	Remove File		${test_dir}${/}RFSwarmReporter.ini
	Log		${ini_content}
	Append To File	${test_dir}${/}RFSwarmReporter.ini	${ini_content}

	Log To Console	Run Reporter with alternate ini file with variable: template = ${test_dir}${/}RFSwarmReporter.ini.
	Run Reporter CLI	-n 	-i	${test_dir}${/}RFSwarmReporter.ini 	-d	${resultfolder} 	--html
	Wait For Reporter Process 	10s
	Log To Console	Check that template elements exist in html.
	@{html_files}=		List Files In Directory		${resultfolder} 	absolute=True 	pattern=*.html
	Log To Console	${\n}All result files: ${html_files}${\n}
	Length Should Be 	${html_files} 	1
	${html_content}= 	Get File 	${html_files}[0]

	Should Contain 	${html_content} 	<title>Report for Issue-#14</title>
	Should Contain 	${html_content} 	<h1>4 Issue-#14</h1>
	Should Contain 	${html_content} 	<div class="body"><p>This is a test for Issue-#14</p></div>

	[Teardown] 	Remove File 	${html_files}[0]

Reporter Command Line INI --ini
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${testdata}			Issue-#14${/}result_dir
	VAR 	${resultdata}		ini_testcase
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}

	${test_dir}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${ini_content}=		Get File	${test_dir}${/}RFSwarmReporter.ini
	${ini_content}=		Replace String	${ini_content}	template_here	${test_dir}${/}Issue-#14.template
	${ini_content}=		Replace String	${ini_content}	template_dir_here	${test_dir}
	Remove File		${test_dir}${/}RFSwarmReporter.ini
	Log		${ini_content}
	Append To File	${test_dir}${/}RFSwarmReporter.ini	${ini_content}

	Log To Console	Run Reporter with alternate ini file with variable: template = ${test_dir}${/}RFSwarmReporter.ini.
	Run Reporter CLI	-n	--ini	${test_dir}${/}RFSwarmReporter.ini 	-d	${resultfolder} 	--html
	Wait For Reporter Process 	10s
	Log To Console	Check that template elements exist in html.
	@{html_files}=		List Files In Directory		${resultfolder} 	absolute=True 	pattern=*.html
	Log To Console	${\n}All result files: ${html_files}${\n}
	Length Should Be 	${html_files} 	1
	${html_content}= 	Get File 	${html_files}[0]

	Should Contain 	${html_content} 	<title>Report for Issue-#14</title>
	Should Contain 	${html_content} 	<h1>4 Issue-#14</h1>
	Should Contain 	${html_content} 	<div class="body"><p>This is a test for Issue-#14</p></div>

	[Teardown] 	Remove File 	${html_files}[0]

Reporter Command Line DIR -d
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-n	-d 	${resultfolder}
	Wait For Reporter Process 	60s
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

	[Teardown] 	Remove File 	${inifile}

Reporter Command Line DIR --dir
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-n	--dir	${resultfolder}
	Wait For Reporter Process 	60s
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

	[Teardown] 	Remove File 	${inifile}

Reporter Command Line TEMPLATE -t
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${basefolder}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${templatefile}=	Normalize Path	${basefolder}${/}Issue-#14.template

	Run Reporter CLI	-n	-t	${templatefile}
	Wait For Reporter Process 	60s
	${inifile}=		Get Reporter INI Location
	${inifile_content}=		Get File		${inifile}
	${inifile_content}=		Split String	${inifile_content}

	${template_offset}		Get Index From List 	${inifile_content}	template
	Should Be Equal		template	${inifile_content}[${template_offset}]		msg=template value is missing!
	${inifile_content}[${template_offset + 2}]= 	Evaluate		r"${inifile_content}[${template_offset + 2}]".replace('x35', '#')
	Should Be Equal		${templatefile}		${inifile_content}[${template_offset + 2}]
	...    msg=template path value did not save correctly [settings != scenario]!

	${templatedir_offset}		Get Index From List 	${inifile_content}	templatedir
	Should Be Equal		templatedir		${inifile_content}[${templatedir_offset}]		msg=templatedir value is missing!
	${inifile_content}[${templatedir_offset + 2}]= 	Evaluate		r"${inifile_content}[${templatedir_offset + 2}]".replace('x35', '#')
	Should Be Equal		${basefolder}		${inifile_content}[${templatedir_offset + 2}]
	...    msg=templatedir path value did not save correctly [settings != scenario]!

	[Teardown] 	Remove File 	${inifile}

Reporter Command Line TEMPLATE --template
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${basefolder}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14
	${templatefile}=	Normalize Path	${basefolder}${/}Issue-#14.template

	Run Reporter CLI	-n	--template	${templatefile}
	Wait For Reporter Process 	60s
	${inifile}=		Get Reporter INI Location
	${inifile_content}=		Get File		${inifile}
	${inifile_content}=		Split String	${inifile_content}

	${template_offset}		Get Index From List 	${inifile_content}	template
	Should Be Equal		template	${inifile_content}[${template_offset}]		msg=template value is missing!
	${inifile_content}[${template_offset + 2}]= 	Evaluate		r"${inifile_content}[${template_offset + 2}]".replace('x35', '#')
	Should Be Equal		${templatefile}		${inifile_content}[${template_offset + 2}]
	...    msg=template path value did not save correctly [settings != scenario]!

	${templatedir_offset}		Get Index From List 	${inifile_content}	templatedir
	Should Be Equal		templatedir		${inifile_content}[${templatedir_offset}]		msg=templatedir value is missing!
	${inifile_content}[${templatedir_offset + 2}]= 	Evaluate		r"${inifile_content}[${templatedir_offset + 2}]".replace('x35', '#')
	Should Be Equal		${basefolder}		${inifile_content}[${templatedir_offset + 2}]
	...    msg=templatedir path value did not save correctly [settings != scenario]!

	[Teardown] 	Remove File 	${inifile}

Reporter Command Line HTML report --html
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14 	HTML

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240709_151531_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-d	${resultfolder}		-n	--html
	Wait For Reporter Process 	60s
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.html

	[Teardown] 	Remove File 	${resultdata}.html

Reporter Command Line DOCX report --docx
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14 	DOCX

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-n	-d	${resultfolder}		--docx
	Wait For Reporter Process 	60s
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.docx

	[Teardown] 	Remove File 	${resultdata}.docx

Reporter Command Line XLSX report --xlsx
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #14 	XLSX

	${testdata}		Set Variable	Issue-#14${/}result_dir
	${resultdata}	Set Variable	20240622_182505_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-n	-d	${resultfolder}		--xlsx
	Wait For Reporter Process 	60s
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.xlsx

	[Teardown] 	Remove File 	${resultdata}.xlsx
