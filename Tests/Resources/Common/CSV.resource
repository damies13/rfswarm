*** Settings ***
Resource 	Common.resource
Library    Collections
Library    String

*** Keywords ***
# # # # #
# CSV:  #
# # # # #

Convert CSV File Cells To a List
	[Arguments]		${csv_file_path}	${csv_separator}
	${csv_file_content}=	Get File		${csv_file_path}
	@{csv_rows_list}=	Split String	${csv_file_content}		separator=\n

	@{csv_rows_content_list}=	Create List
	FOR  ${row}  IN  @{csv_rows_list}
		@{csv_row_cells_list}=		Split String	${row}	separator=${csv_separator}
		Append To List	${csv_rows_content_list}	${csv_row_cells_list}
	END

	${status}=	Run Keyword And Return Status	Should Be Empty	@{csv_rows_content_list}[-1]
	IF  ${status} == ${True}
		@{csv_rows_content_list} 	Set Variable 	${csv_rows_content_list}[:-1]
	END

	RETURN	${csv_rows_content_list}

CSV to List
	[Arguments] 	${filepath}
	File Should Exist 	${filepath}
	${f}= 	Evaluate    open($filepath)
	${csvdata}= 	Evaluate    csv.reader($f, delimiter=',') 	modules=csv
	${data}= 			Evaluate    list($csvdata)
	Evaluate    str($f.close())
	${headings}= 			Evaluate    str($data.pop(0))
	RETURN 	${data}

CSV to Dict
	[Arguments] 	${filepath}
	File Should Exist 	${filepath}
	${f}= 	Evaluate    open($filepath)
	${csvdata}= 	Evaluate    csv.DictReader($f, delimiter=',') 	modules=csv
	${data}= 			Evaluate    list($csvdata)
	Evaluate    str($f.close())
	RETURN 	${data}

Show CSV File as Table
	[Arguments] 	${filepath}
	File Should Exist 	${filepath}
	@{FileData}= 	CSV to Dict 	${filepath}
	# Log 	${FileData} 		console=True
	${ColumnWidths}=    Create Dictionary

	FOR    ${key}    ${value}    IN    &{FileData[0]}
		# Log    Current key is ${key} and value is ${value}
		${klength}=    Get Length    ${key}
		Set To Dictionary    ${ColumnWidths}    ${key}=${klength}
	END
	# Log To Console    ${ColumnWidths}

	FOR    ${row}    IN    @{FileData}
		Log 	${row}
		FOR    ${key}    ${value}    IN    &{row}
			# Log    Current key is ${key} and value is ${value}
			${vlength}=    Get Length    ${value}
			IF    ${vlength} > ${ColumnWidths}[${key}]
				Set To Dictionary    ${ColumnWidths}    ${key}=${vlength}
			END
		END
	END
	# Log To Console    ${ColumnWidths}

	VAR    ${SepRow} 	--
	VAR    ${HeadRow} 	|${SPACE}
	VAR    ${SepChar} 	-

	# column headings
	FOR    ${key}    ${value}    IN    &{ColumnWidths}
		# ${SepRow}= 		Catenate 		${SepRow} 		${SepChar * ${value}}
		VAR    ${SepRow} 	${SepRow}${SepChar}${SepChar * ${value}}${SepChar}${SepChar}
		${padded}= 		Format String 	{:<${value}}    ${key}
		# ${HeadRow}= 	Catenate 		${HeadRow} 		${padded}${SPACE}|
		VAR    ${HeadRow} 	${HeadRow}${SPACE}${padded}${SPACE}|
	END

	VAR    ${SepRow} 	${SepRow}${\n}
	VAR    ${HeadRow} 	${HeadRow}${\n}

	VAR    ${tabledata} 	${SepRow}
	VAR    ${tabledata} 	${tabledata}${HeadRow}
	VAR    ${tabledata} 	${tabledata}${SepRow}

	# column values
	FOR    ${row}    IN    @{FileData}
		Log 	${row}
		VAR    ${srow}    |${SPACE}
		FOR    ${key}    ${value}    IN    &{row}
			${padded}= 		Format String 	{:<${ColumnWidths['${key}']}}    ${value}
			VAR    ${srow}    ${srow}${SPACE}${padded}${SPACE}|
		END
		VAR    ${tabledata} 	${tabledata}${srow}${\n}
	END
	VAR    ${tabledata} 	${tabledata}${SepRow}
	Log 		${tabledata} 		console=True


	RETURN 	${FileData}
	# 