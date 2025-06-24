*** Settings ***
Documentation 	This resource file contains keywords for Reporter XLSX reports only.

Resource 	../../../Common/Common.resource

Library 	DocTest.VisualTest

Library 	../read_xlsx.py

Variables 	../report_expected_data.yaml

*** Keywords ***

Verify XLSX Cover Page
	[Arguments] 	${xlsx_file}
	@{xlsx_sheets}= 	Read All Xlsx Sheets 	${xlsx_file}
	List Should Contain Value 	${xlsx_sheets} 	Cover
	@{cover_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	Cover
	@{cover_expected} 	Convert To List 	${Cover.text}

	${len} 	Get Length 	${cover_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${cover_expected}[${i}] 	${cover_txtdata}[${i}][0] 	msg=[ Expected != Converted ]
	END

Verify XLSX Report Contents
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} XLSX
	END

	@{section_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section_txtdata}

Verify XLSX Report Notes
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section_txtdata}
	@{notes_expected} 	Convert To List 	${${section}.text}

	${len} 	Get Length 	${notes_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${notes_expected}[${i}] 	${section_txtdata}[${i}][0] 	msg=[ Expected != Converted ]
	END

Verify XLSX Report Graph
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected image. Provide full xlsx file path.
	...    It is required to specify in which cell the image is stored.
	...    Also provide the paths to the expected xlsx images directory and the directory where the image will be saved.
	[Arguments] 	${xlsx_file} 	${section} 	${cell_id} 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	${img}= 	Extract Image From Xlsx Sheet 	${xlsx_file} 	${xlsx_sheet} 	${cell_id} 	${xlsx_img_path}
	Convert Image To Black And White 	${xlsx_img_path}${/}${img}
	Compare Images 	${xlsx_expected_img_path}${/}${img} 	${xlsx_img_path}${/}${img}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify XLSX Report Table Content
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected table text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_table}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_expected} 	Convert To List 	${${section}.header}
	@{st_header_row} 	Convert To List 	${section_table}[0]
	Length Should Be 	${section_table} 	${st_length_expected}
	Lists Should Be Equal 	${st_header_expected} 	${st_header_row} 	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify XLSX Report Error Details Content
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected table text and images. Provide full xlsx file path.
	...    Also provide the paths to the expected xlsx images directory and the directory where the image will be saved.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path}
	...    ${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_table}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_col_expected} 	Convert To List 	${${section}.header_col}
	Length Should Be 	${section_table} 	${st_length_expected}
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
		IF  '${row}[0]' not in @{st_header_col_expected}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${st_header_col_expected}.
		END

		${img}= 	Extract Image From Xlsx Sheet 	${xlsx_file} 	${xlsx_sheet} 	B${i + 3} 	${xlsx_img_path}
		IF  '${img}' != '${0}'
			Log 	Image was found in B${i} cell.
			Compare Images 	${xlsx_expected_img_path}${/}${img} 	${xlsx_img_path}${/}${img}
		END

	END

	# !need to convert empty expected list value to the ${space} where screenshot should be!
	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	${empty_i} 	Get Index From List 	${first_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${first_row_expected} 	${empty_i}
		Insert Into List 	${first_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	${empty_i} 	Get Index From List 	${last_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${last_row_expected} 	${empty_i}
		Insert Into List 	${last_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	${empty_i} 	Get Index From List 	${quater_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${quater_row_expected} 	${empty_i}
		Insert Into List 	${quater_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	${empty_i} 	Get Index From List 	${mid_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${mid_row_expected} 	${empty_i}
		Insert Into List 	${mid_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	${empty_i} 	Get Index From List 	${upper_mid_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${upper_mid_row_expected} 	${empty_i}
		Insert Into List 	${upper_mid_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]
