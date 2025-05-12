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
${results_dir} 		${None}
${agent_name} 		${None}


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
	VAR 	${scenario_name} 	${langcode}_scenario 		scope=TEST
	VAR 	${results_dir} 		${test_data}${/}results 	scope=TEST
	VAR 	${agent_name} 		${sample} 					scope=TEST
	Create Directory 	${results_dir}
	${robot_file} 	${scenario_file}= 	Create Language Files 	${langcode} 	${sample}
	VAR 	@{mngr_options} 	-g 	1 	-s 	${scenario_file} 	-d 	${results_dir}
	VAR 	@{agnt_options} 	-a 	${agent_name}

	Open Agent 			${agnt_options}
	Open Manager GUI 	${mngr_options}
	Take A Screenshot
	Check If The Agent Is Ready
	Click Tab 	Plan
	Click Button	runplay

	Log To Console	\tStarted run for "${langcode}"
	Wait For the Scenario Run To Finish
	Click Button	csv_report
	Press key.enter 1 Times
	Sleep	3

	Check DB For Metrics 	${langcode} 	${sample}
	Check CSV Files 	${langcode} 	${sample}

Non-ASCII Suite Setup
	Remove Directory 	${OUTPUT DIR}${/}results${/}Issue-#97 	recursive=${True}
	Set Platform

Non-ASCII Suite Teardown
	Copy Directory 		${test_data} 	${OUTPUT DIR}${/}results${/}Issue-#97
	Remove Directory 	${test_data}${/}files 	recursive=${True}
	Remove Directory 	${test_data}${/}results 	recursive=${True}

Non-ASCII Test Setup
	${mgrini}= 	Get Manager INI Location
	Set INI Window Size 	1200 	600

Non-ASCII Test Teardown
	Stop Agent
	Run Keyword		Close Manager GUI ${platform}
	Check Logs

Create Language Files
	[Arguments] 	${langcode} 	${sample}
	Create Directory 	${test_data}${/}files
	VAR 	${robot_file} 		${test_data}${/}files${/}${sample}_sample_test.robot
	VAR 	${scenario_file} 	${test_data}${/}files${/}${scenario_name}.rfs

	Copy File 	${test_data}${/}LANG_sample_test.robot 	${robot_file}
	Copy File 	${test_data}${/}LANG_scenario.rfs 	${scenario_file}

	Change __Lang__ With ${langcode} In ${robot_file}
	Change __Lang_Sample__ With ${sample} In ${robot_file}
	Change __LangRobot__ With ${robot_file} In ${scenario_file}
	Change __LangTest__ With ${sample} Test Case In ${scenario_file}

	RETURN 	${robot_file} 	${scenario_file}

Check DB For Metrics
	[Arguments] 	${langcode} 	${sample}
	Log 	\tChecking run Database 	console=${True}
	${dbfile}= 	Find Result DB 	directory=${results_dir}	result_pattern=*_${scenario_name}*
	${db_query_result}= 	Query Result DB 	${dbfile}
	...    SELECT count(*) FROM MetricData WHERE PrimaryMetric='${sample} Keyword'

	Log 	${db_query_result}[0][0]
	Should Not Be Equal 	${db_query_result}[0][0] 	${0} 	msg=Can't find Language sample string in Metrics DB Table for "${langcode}"!

Check CSV Files
	[Arguments] 	${langcode} 	${sample}
	Log 	\tChecking CSV Files 	console=${True}
	VAR 	@{keywords} 	${sample} Keyword 	${sample} Fail Keyword

	@{test_results}=	List Directories In Directory	${results_dir}		absolute=${True}	pattern=*${scenario_name}
	@{csv_file_paths}=		List Files In Directory		${test_results}[0]	*.csv	absolute=${True}
	Length Should Be	${csv_file_paths}	3	msg=Some CSV files are missing!

	FOR  ${i}  IN RANGE  0  3
		${csv_rows_content_list}=	Convert CSV File Cells To a List		${csv_file_paths}[${i}]		csv_separator=,
		Log To Console	${\n}\tCSV report file found: ${csv_file_paths}[${i}]
		Log 	${csv_rows_content_list}

		${csv_report_file_type}=	Split String From Right		${csv_file_paths}[${i}]	separator=_${scenario_name}_	max_split=1
		VAR 	${csv_report_file_type} 	${csv_report_file_type}[-1]
		IF  '${csv_report_file_type}' == 'summary.csv'
			@{second_row}=		Set Variable	${csv_rows_content_list}[1]
			Log		${second_row}
			IF  '${second_row}[0]' not in @{keywords}
				Fail	msg=CSV summary File did not save correctly in the Result Name column, second row!
			END
			@{third_row}=		Set Variable	${csv_rows_content_list}[1]
			IF  '${third_row}[0]' not in @{keywords}
				Fail	msg=CSV summary File did not save correctly in the Result Name column, third row!
			END

			Length Should Be	${second_row}	9	msg=Some columns in summary.csv are missing in second row, should be 9 of them!
			Length Should Be	${third_row}	9	msg=Some columns in summary.csv are missing in third row, should be 9 of them!

		ELSE IF  '${csv_report_file_type}' == 'raw_result_data.csv'
			${len}=		Get Length	${csv_rows_content_list}
			Should Be True	${len} >= ${3}		msg=Some rows in raw_result_data.csv are missing, should be at least 3!

			FOR  ${j}  IN RANGE  1  ${len}
				@{data_row}=	Set Variable	${csv_rows_content_list}[${j}]
				Log		${data_row}
				IF  '${data_row}[5]' not in @{keywords}
					Fail	msg=CSV raw_result_data File did not save correctly in the Result Name column, ${j+1} row!
				END

				Length Should Be	${data_row}	10	msg=Some columns in raw_result_data.csv are missing in ${j+1}nd row, should be 10 of them!
			END

		ELSE IF  '${csv_report_file_type}' == 'agent_data.csv'
			${len}=		Get Length	${csv_rows_content_list}
			@{expected_status}	Create List  Ready  Running  Critical  Stopping  Warning  Offline?

			FOR  ${j}  IN RANGE  1  ${len}
				@{data_row}=	Set Variable	${csv_rows_content_list}[${j}]
				Log		${data_row}

				Should Be Equal		${data_row}[0]	${agent_name}
				...    msg=CSV agent_data File did not save correctly in the Agentname column, ${j+1} row!
				Length Should Be	${data_row}		9	msg=Some columns in agent_data.csv are missing in ${j+1}nd row, should be 9 of them!
			END
		END
	END

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
