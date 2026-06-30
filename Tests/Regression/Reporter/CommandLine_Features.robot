*** Settings ***
Resource 	../../Resources/CommandLine/Reporter/CommandLine_Reporter.resource
Resource 	../../Resources/CommandLine/Reporter/Reporter_DOCX.resource
Resource 	../../Resources/CommandLine/Reporter/Reporter_HTML.resource
Resource 	../../Resources/CommandLine/Reporter/Reporter_XLSX.resource

Resource 	../../Resources/Common/Directories_and_Files.resource
Resource 	../../Resources/Common/INI_PIP_Data.resource
Resource 	../../Resources/Common/Logs.resource
Resource 	../../Resources/Common/RFS_Components.resource


Suite Setup 	Common.Basic Suite Initialization Reporter

Test Timeout 	10 minutes

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
	${resultdata}	Set Variable	20240709_151531_test_scenario
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
	${resultdata}	Set Variable	20240709_151531_test_scenario
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
	${resultdata}	Set Variable	20240709_151531_test_scenario
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
	${resultdata}	Set Variable	20240709_151531_test_scenario
	${basefolder}	Set Variable	${CURDIR}${/}testdata${/}${testdata}
	${resultfolder}	Set Variable	${basefolder}${/}${resultdata}

	Run Reporter CLI	-n	-d	${resultfolder}		--xlsx
	Wait For Reporter Process 	60s
	@{result_files}=		List Files In Directory		${resultfolder}
	Log To Console	${\n}All result files: ${result_files}${\n}
	List Should Contain Value	${result_files}		${resultdata}.xlsx

	[Teardown] 	Remove File 	${resultdata}.xlsx

Verify the Content Of the HTML Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #36 	HTML 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${html_file}		${resultfolder}${/}${resultdata}.html
	VAR 	${html_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}html_images
	VAR 	${html_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#36${/}html_images
	VAR 	${img_comp_threshold} 	0
	VAR 	${move_tolerance} 		300

	Log 	template: ${template_dir} 	console=True
	Run Reporter CLI	-d  ${resultfolder}  -t  ${template_dir}  -n  --html
	Wait For Reporter Process 	timeout=30 minutes
	Wait Until Created 	${html_file} 	timeout=5 minutes

	Log To Console	Verification of saved data in the RFSwarm HTML report started.
	${html} 	Parse HTML File 	${html_file}
	@{headings}= 	Extract All HTML Report Headings 	${html}
	Log		${headings}

	Verify HTML Cover Page 	${html}

	VAR 	${section} 	This is Heading
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}

	VAR 	${section} 	Contents graphs
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}

	VAR 	${section} 	Contents tables
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Contents 	${section} 	${section_obj}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section} 		Note
	VAR 	${break_at} 	h2
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj} 	${break_at}

	VAR 	${section} 	Second Note
	VAR 	${break_at} 	h3
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section} 	heading=h2
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj} 	${break_at}

	VAR 	${section} 	Third Note
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section} 	heading=h3
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Notes 	${section} 	${section_obj}


	# Graphs - when new graphs are required, save them using the function in save_html_image.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph Left Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result FAIL
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result Total TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph LR Combined
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Graph 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result TPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Result TotalTPS
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table ResultSummary
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table Polish Lang
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}

	VAR 	${section} 	Data Table ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Table Content 	${section} 	${section_obj}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No Screenshots
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No GBRN
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details No GBET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details Polish Lang
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	VAR 	${section} 	Error Details ST ET
	${section_obj} 	Get HTML Report Heading Section Object 	${html} 	${section}
	Should Not Be Equal 	${section_obj} 	${0} 	msg=Didn't find "${section}" section.
	Verify HTML Report Error Details Content 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}

	[Teardown] 	Run Keywords
	...    Stop Reporter CLI 	AND
	...    Move File 	${html_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.html

Verify the Content Of the DOCX Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #38 	DOCX 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${docx_file}		${resultfolder}${/}${resultdata}.docx
	VAR 	${docx_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}docx_images
	VAR 	${docx_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#38${/}docx_images
	VAR 	${img_comp_threshold} 	0
	VAR 	${move_tolerance} 		300

	Log 	template: ${template_dir} 	console=True
	Run Reporter CLI	-d  ${resultfolder}  -t  ${template_dir}  -n  --docx
	Wait For Reporter Process 	timeout=30 minutes
	Wait Until Created 	${docx_file} 	timeout=5 minutes

	Log To Console	Verification of saved data in the RFSwarm DOCX report started.
	File Should Exist 	${docx_file}
	&{docx_data} 	Read DOCX File 	${docx_file}
	Log 	${docx_data}

	Verify DOCX Cover Page 	${docx_data}

	VAR 	${section} 	This is Heading
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}

	VAR 	${section} 	Contents graphs
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}

	VAR 	${section} 	Contents tables
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Contents 	${docx_data} 	${section}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section} 		Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section} 	custom=${True}

	VAR 	${section} 		Second Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section}

	VAR 	${section} 		Third Note
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Notes 	${docx_data} 	${section}


	# Graphs - when new graphs are required, save them using the function in read_docx.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 		Data Graph Left Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result FAIL
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Left Result Total TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Right Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph Right Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph LR Combined
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 		Data Graph ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Graph 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result TPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table Result TotalTPS
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table ResultSummary
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section} 	custom=${True}

	VAR 	${section} 	Data Table Polish Lang
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}

	VAR 	${section} 	Data Table ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Table Content 	${docx_data} 	${section}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No Screenshots
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No GBRN
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details No GBET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details Polish Lang
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	VAR 	${section} 	Error Details ST ET
	Dictionary Should Contain Key 	${docx_data} 	${section} 	msg=Didn't find "${section}" section.
	Verify DOCX Report Error Details Content 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path}

	[Teardown] 	Run Keywords
	...    Stop Reporter CLI 	AND
	...    Move File 	${docx_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.docx

Verify the Content Of the XLSX Report
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #37 	XLSX 	robot:continue-on-failure
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${testdata} 		Issue-#36_37_38
	VAR 	${resultdata}		20230728_154253_Odoo-demo
	VAR 	${basefolder}		${CURDIR}${/}testdata${/}${testdata}
	VAR 	${resultfolder} 	${basefolder}${/}${resultdata}
	VAR 	${template_dir} 	${basefolder}${/}sample.template
	VAR 	${xlsx_file}		${resultfolder}${/}${resultdata}.xlsx
	VAR 	${xlsx_img_path} 		${OUTPUT_DIR}${/}${testdata}${/}xlsx_images
	VAR 	${xlsx_expected_img_path} 		${CURDIR}${/}testdata${/}Issue-#37${/}xlsx_images
	VAR 	${img_comp_threshold} 	0
	VAR 	${move_tolerance} 		300

	Log 	template: ${template_dir} 	console=True
	Run Reporter CLI	-d  ${resultfolder}  -t  ${template_dir}  -n  --xlsx
	Wait For Reporter Process 	timeout=30 minutes
	Wait Until Created 	${xlsx_file} 	timeout=5 minutes

	Log To Console	Verification of saved data in the RFSwarm XLSX report started.
	File Should Exist 	${xlsx_file}
	@{xlsx_sheets}= 	Read All Xlsx Sheets 	${xlsx_file}
	Log		${xlsx_sheets}

	Verify XLSX Cover Page 	${xlsx_file}

	VAR 	${section} 	This is Heading
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.


	# Contents:
	Log 	\nVerifying Contents: 	console=${True}
	VAR 	${section} 	Contents contents
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Contents graphs
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Contents tables
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Contents 	${xlsx_file} 	${section} 	${xlsx_sheet}


	# Notes:
	Log 	\nVerifying Notes: 	console=${True}
	VAR 	${section1} 	Note
	VAR 	${section2} 	Second Note
	VAR 	${section3} 	Third Note
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section1}
	${sheet_number} 	Get Substring 	${xlsx_sheet} 	0 	1

	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section1}" section.
	Verify XLSX Report Notes 	${xlsx_file} 	${section1} 	${xlsx_sheet} 	stop_at=${sheet_number}.1 ${section2} 	custom=${True}

	Verify XLSX Report Notes 	${xlsx_file} 	${section2} 	${xlsx_sheet} 	start_at=${sheet_number}.1 ${section2} 	stop_at=${sheet_number}.1.1 ${section3}

	Verify XLSX Report Notes 	${xlsx_file} 	${section3} 	${xlsx_sheet} 	start_at=${sheet_number}.1.1 ${section3}


	# Graphs - when new graphs are required, save them using the function in read_xlsx.py!
	Log 	\nVerifying Graphs: 	console=${True}
	VAR 	${section} 	Data Graph Left Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result FAIL
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Left Result Total TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph Right Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph LR Combined
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}

	VAR 	${section} 	Data Graph ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Graph 	${xlsx_file} 	${section} 	B3 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}


	# Tables:
	Log 	\nVerifying Tables: 	console=${True}
	VAR 	${section} 	Data Table Metric
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result TPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table Result TotalTPS
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table ResultSummary
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	custom=${True}

	VAR 	${section} 	Data Table Polish Lang
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}

	VAR 	${section} 	Data Table ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Table Content 	${xlsx_file} 	${section} 	${xlsx_sheet}


	# Error Details:
	Log 	\nVerifying Error Details: 	console=${True}
	VAR 	${section} 	Error Details
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No Screenshots
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No GBRN
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details No GBET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details Polish Lang
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	VAR 	${section} 	Error Details ST ET
	${xlsx_sheet} 	Get Xlsx Sheet By Name 	${xlsx_file} 	${section}
	Should Not Be Equal 	${xlsx_sheet} 	${0} 	msg=Didn't find "${section}" section.
	Verify XLSX Report Error Details Content 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${xlsx_expected_img_path} 	${xlsx_img_path}

	[Teardown] 	Run Keywords
	...    Stop Reporter CLI	AND
	...    Move File 	${xlsx_file} 	${OUTPUT_DIR}${/}${testdata}${/}${resultdata}.xlsx
