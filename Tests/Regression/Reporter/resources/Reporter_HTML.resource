*** Settings ***
Documentation 	This resource file contains keywords for Reporter HTML reports only.

Resource 	../../../Common/Common.resource

Library 	DocTest.VisualTest
Library 	XML 	use_lxml=True
Library 	save_html_image.py

Variables 	report_expected_data.yaml

*** Keywords ***

Parse HTML File
	[Documentation] 	Parse HTML file to the etree object using lxml module.
	[Arguments] 	${html_file}
	File Should Exist 	${html_file}
	${html}= 	Evaluate 	lxml.etree.parse(r'${html_file}', lxml.etree.HTMLParser(encoding="utf-8")) 	modules=lxml.etree

	RETURN 	${html}

Extract All HTML Report Headings
	[Documentation] 	Search for all HTML report section headings. You can change searchable html element from h1 to: h2, h3 ...
	[Arguments] 	${grand_selector} 	${child}=//div 	${heading}=h1
	Log 	${grand_selector}

	VAR 	@{headings}
	TRY
		@{headings} 	Get Elements Texts 	${grand_selector} 	${heading}
	EXCEPT
		No Operation
	END

	@{selectors} 	Get Elements 	${grand_selector} 	${child}
	FOR  ${selector}  IN  @{selectors}
		@{selector_headings} 	Extract All HTML Report Headings 	${selector} 	div
		${headings} 	Combine Lists 	${headings} 	${selector_headings}
	END

	RETURN 	${headings}

Verify HTML Cover Page
	[Arguments] 	${html}
	${cover_section}= 	Get Element 	${html} 	//div[@id="TitlePage"]
	${title} 	Get Element Text 	${cover_section} 	div[@class="title center"]
	${data} 	Get Element Text 	${cover_section} 	div[@class="subtitle center"]
	VAR 	@{cover_txtdata} 	${title} 	${data}

	@{cover_expected} 	Convert To List 	${Cover.text}
	Lists Should Be Equal 	${cover_expected} 		${cover_txtdata}	msg=[ Expected != Converted ]

Get HTML Report Heading Section Object
	[Documentation]
	...    Searches for provided heading name and return whole section object in the given selector such as html.
	...    If not return 0.
	...    You can change searchable html element from h1 to: h2, h3 ...
	[Arguments] 	${grand_selector} 	${heading_name} 	${heading}=h1 	${child}=//div
	Log 	${grand_selector}
	Log 	${child}

	TRY
		@{texts} 	Get Elements Texts 	${grand_selector} 	${heading}
	EXCEPT
		No Operation
	END
	FOR  ${text}  IN  @{texts}
		${status}= 	Run Keyword And Return Status 	Should Contain 	${text} 	${heading_name}
		IF  ${status}
			Log 	${text}
			Log 	${heading_name}
			RETURN 	${grand_selector}
		END

	END

	@{selectors} 	Get Elements 	${grand_selector} 	${child}
	FOR  ${selector}  IN  @{selectors}
		${found_selector} 	Get HTML Report Heading Section Object 	${selector} 	${heading_name} 	${heading} 	child=div
		Log 	${found_selector}
		IF  '${found_selector}' != '${0}'
			RETURN 	${found_selector}
		END

	END

	Log 	Didn't find any matching headings.
	RETURN 	${0}

Read HTML Report Section Text Data
	[Documentation]
	...    Return all available text data in a given container from a given section and it's childs.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section_obj} 	 ${break_at}=${None} 	${container}=p
	Log 	${section_obj}

	TRY
		@{texts} 	Get Elements Texts 	${section_obj} 	${container}
	EXCEPT
		No Operation
	END

	@{childs} 	Get Child Elements 	${section_obj}
	FOR  ${child}  IN  @{childs}
		Log 	${child.tag}
		IF  '${child.tag}' != '${break_at}'
			@{selector_text} 	Read HTML Report Section Text Data 	${child} 	${break_at} 	${container}
			${texts} 	Combine Lists 	${texts} 	${selector_text}
		ELSE
			BREAK
		END

	END

	RETURN 	${texts}

Read HTML Report Section Data Table
	[Documentation] 	Return table data that is in the provided section as nested list: Table = [[header_row], [row1], [row2], ...]
	[Arguments] 	${section_obj}
	${table} 	Get Element 	${section_obj} 	div/table
	@{table_rows} 	Get Elements 	${table} 	tr

	VAR 	@{table_data}

	FOR  ${row}  IN  @{table_rows}
		VAR 	@{row_data}

		@{table_row_cells} 	Get Child Elements 	 ${row}
		FOR  ${cell}  IN  @{table_row_cells}
			${cell_data} 	Get Element Text 	${cell}
			Append To List 	${row_data} 	${cell_data}

		END
		${len} 	Get Length 	${row_data}
		IF  ${len} > 0
			Append To List 	${table_data} 	${row_data}
		END

	END

	RETURN 	${table_data}

Extract All Images From HTML Report Section
	[Documentation]
	...    Extract all images from the given section and save them in the given path.
	...    Provide ${base_name} to specify base for image name.
	...    The ${img_num} argument is only used for naming purposes and its logical count is related to the implementation of the regression.
	[Arguments] 	${section} 	${output_folder} 	${base_name} 	${img_num}=${1}
	Log 	${section}

	TRY
		@{img_containers} 	Get Elements 	${section} 	img
	EXCEPT
		No Operation
	END
	FOR  ${img}  IN  @{img_containers}
		${image_data}= 	Get Element Attribute 	${img} 	src
		Log 	${image_data}
		Log 	${img_num}
		@{splitted_img_data} 	Split String 	${image_data} 	, 	max_split=1 	# Need to separate img data from informations.
		Log 	${splitted_img_data}[1]
		${base64_string} 	Convert To String 	${splitted_img_data}[1]
		Save Html Embeded Image 	${base64_string} 	${base_name}_${img_num} 	${output_folder}

		VAR 	${img_num} 	${img_num + 1}

	END

	@{childs} 	Get Child Elements 	${section}
	FOR  ${child}  IN  @{childs}
		${child_img_num} 	Extract All Images From HTML Report Section 	${child} 	${output_folder} 	${base_name} 	${img_num}
		VAR 	${img_num} 	${child_img_num}
	END

	RETURN 	${img_num} 	# *Only for image count

Verify HTML Report Contents
	[Documentation]
	...    Verify the section for the given section name and section object for the expected text.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${break_at}=${None}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata}= 	Read HTML Report Section Text Data 	${section_obj} 	${break_at}
	@{expected_contents} 	Convert To List 	${${section}.text}
	${len} 	Get Length 	${section_txtdata}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Contain 	${section_txtdata}[${i}] 	${expected_contents}[${i}] 	msg=Can't find ${section_txtdata}[${i}] in the ${section} section.
	END

Verify HTML Report Notes
	[Documentation]
	...    Verify the section for the given section name and section object for the expected text.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${break_at}=${None}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata}= 	Read HTML Report Section Text Data 	${section_obj} 	${break_at}
	@{expected_notes} 	Convert To List 	${${section}.text}
	${len} 	Get Length 	${expected_notes}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${expected_notes}[${i}] 	${section_txtdata}[${i}]
		...    msg=[ Expected != Converted ] Can't find ${section_txtdata}[${i}] in the ${section} section.
	END

Verify HTML Report Graph
	[Documentation]
	...    Verify the section for the given section name and section object for the expected image.
	...    Also provide the paths to the expected html images directory and the directory where the image will be saved.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	${img_count} 	Extract All Images From HTML Report Section 	${section_obj} 	${html_img_path} 	${section}
	${normalized_section} 	Replace String 	${section} 	${SPACE} 	_
	VAR 	${img_name} 	${normalized_section}_${img_count - 1}_image.png
	Convert Image To Black And White 	${html_img_path}${/}${img_name}
	Compare Images 	${html_expected_img_path}${/}${img_name} 	${html_img_path}${/}${img_name}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify HTML Report Table Content
	[Documentation]
	...    Verify the section for the given section name and section object for the expected table content.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj}
	Log 	\t- ${section} 	console=${True}

	${section_table} 	Read HTML Report Section Data Table 	${section_obj}
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

	IF  '${rows_numbers}[0]' != '_'
		@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
		@{first_row_expected} 	Convert To List 	${${section}.first_row}
		Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[1]' != '_'
		@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
		@{last_row_expected} 	Convert To List 	${${section}.last_row}
		Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[2]' != '_'
		@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
		@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
		Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[3]' != '_'
		@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
		@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
		Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[4]' != '_'
		@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
		@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
		Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]
	END

Verify HTML Report Error Details Content
	[Documentation]
	...    Verify the section for the given section name and section object for the expected table content and screenshots.
	...    Also provide the paths to the expected html images directory and the directory where the image will be saved.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}
	Log 	\t- ${section} 	console=${True}

	${section_table} 	Read HTML Report Section Data Table 	${section_obj}
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

	${last_img_num} 	Extract All Images From HTML Report Section 	${section_obj} 	${html_img_path} 	${section}
	${normalized_section} 	Replace String 	${section} 	${SPACE} 	_
	FOR  ${img_num}  IN RANGE  1  ${last_img_num}
		VAR 	${img_name} 	${normalized_section}_${img_num}_image.png
		Compare Images 	${html_expected_img_path}${/}${img_name} 	${html_img_path}${/}${img_name}

	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	IF  '${rows_numbers}[0]' != '_'
		@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
		@{first_row_expected} 	Convert To List 	${${section}.first_row}
		Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[1]' != '_'
		@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
		@{last_row_expected} 	Convert To List 	${${section}.last_row}
		Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[2]' != '_'
		@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
		@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
		Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[3]' != '_'
		@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
		@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
		Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]
	END

	IF  '${rows_numbers}[4]' != '_'
		@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
		@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
		Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]
	END
