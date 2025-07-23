*** Settings ***
Documentation 	This resource file contains keywords for Reporter DOCX reports only.

Resource 	../../../Common/Common.resource

Library 	DocTest.VisualTest
Library 	read_docx.py

Variables 	report_expected_data.yaml

*** Keywords ***
Verify DOCX Cover Page
	[Arguments] 	${docx_data}
	Dictionary Should Contain Key 	${docx_data} 	Cover
	@{cover_txtdata} 	Convert To List 	${docx_data}[Cover][text]
	@{cover_expected} 	Convert To List 	${Cover.text}
	Lists Should Be Equal 	${cover_expected} 		${cover_txtdata}	msg=[ Expected != Converted ]

Verify DOCX Report Contents
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata} 	Convert To List 	${docx_data}[${section}][text]
	Log 	${section_txtdata}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} DOCX
	END

Verify DOCX Report Notes
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata} 	Convert To List 	${docx_data}[${section}][text]
	Log 	${section_txtdata}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} DOCX
	END

	@{notes_expected} 	Convert To List 	${${section}.text}

	${len} 	Get Length 	${notes_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${notes_expected}[${i}] 	${section_txtdata}[${i}] 	msg=[ Expected != Converted ]
	END

Verify DOCX Report Graph
	[Documentation]
	...    Verify the section for the given section name for the expected image. Provide full docx file path.
	...    Also provide the paths to the expected docx images directory and the directory where the image will be saved.
	[Arguments] 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	@{img_names}= 	Extract DOCX Images Under Heading 	${section} 	${docx_file} 	${docx_img_path}
	VAR 	${img_name} 	${img_names}[0]
	Convert Image To Black And White 	${docx_img_path}${/}${img_name}
	Compare Images 	${docx_expected_img_path}${/}${img_name} 	${docx_img_path}${/}${img_name}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify DOCX Report Table Content
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected table text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_table} 	Convert To List 	${docx_data}[${section}][table]
	Log 	${section_table}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} DOCX
	END

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

Verify DOCX Report Error Details Content
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected table text and images.
	...    Provide full docx file path for image comparison.
	...    Also provide the paths to the expected docx images directory and the directory where the image will be saved.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} DOCX
	END

	@{section_table}= 	Convert To List 	${docx_data}[${section}][table]
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

	END

	@{img_names}= 	Extract DOCX Images Under Heading 	${section} 	${docx_file} 	${docx_img_path}
	FOR  ${img_name}  IN  @{img_names}
		Compare Images 	${docx_expected_img_path}${/}${img_name} 	${docx_img_path}${/}${img_name}
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
