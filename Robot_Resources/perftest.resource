*** Settings ***
Library           OperatingSystem
Library           String

*** Variables ***
${STT_MIN}			15
${STT_MAX}			45

*** Keywords ***
Standard Think Time
	${number}    Evaluate    random.randint(${STT_MIN}, ${STT_MAX})    random
	Log      Standard Think Time (${number})
	Sleep    ${number}

Get Data Row
	[Arguments]    ${FileName}    ${Row}="Random"
	[Documentation]    This keyword gets a row of data from a CSV or TSV file,
	...                takes 1-2 arguments:
	...                 - FileName (Required)
	...                 - Row (Optional) can be Random, Sequential or a number
	...                   defaults to Random
	# Log    Get Data Row: \tFileName: ${FileName} \tRow: ${Row}
	${RAW_FILE} = 	Get File	${FileName}
	@{FILE_LINES} = 	Split To Lines	${RAW_FILE}
	${LINE_COUNT} = 	Get Length    ${FILE_LINES}

	${FILE_SEQUENTIAL_NUM} =	Get Variable Value	${FILE_SEQUENTIAL_NUM}	0

	@{delim_cols} = 	Split String	${FILE_LINES}[0]	,
	${delim_cols_len} = 	Get Length    ${delim_cols}
	${DELIMITER} =	Set Variable If	${delim_cols_len} > 1	,	\t
	@{FILE_COLUMNS} = 	Split String	${FILE_LINES}[0]	${DELIMITER}
	${COLUMNS_COUNT} = 	Get Length    ${FILE_COLUMNS}

	${ROW_NUM} = 	Set Variable    ${Row}
	${ROW_NUM} = 	Run Keyword If    ${Row}=="Random"	Evaluate    random.randint(1, ${LINE_COUNT}-1)    random
					... 	ELSE	Set Variable    ${ROW_NUM}
	${ROW_NUM} = 	Run Keyword If    ${Row}=="Sequential"    Evaluate    ${FILE_SEQUENTIAL_NUM} + 1
					... 	ELSE	Set Variable    ${ROW_NUM}

	Set Test Variable	\${FILE_SEQUENTIAL_NUM}	${FILE_SEQUENTIAL_NUM}

	@{ROW_COLUMNS} = 	Split String	${FILE_LINES}[${ROW_NUM}]	${DELIMITER}
	# :FOR ${I}	Input Text    locator    text
	FOR	${I}	IN RANGE	${COLUMNS_COUNT}
		# Log    \${I} ${I}
		${VAR_NAME} = 	Set Variable    ${FILE_COLUMNS}[${I}]
		${VAR_VALUE} = 	Set Variable    ${ROW_COLUMNS}[${I}]
		# Log    \${VAR_NAME}: ${VAR_NAME}\t\${VAR_VALUE}: ${VAR_VALUE}
		Set Test Variable	${${VAR_NAME}}	${VAR_VALUE}
	END
	# Log Variables

Get File Dir
	${FILE_DIR} = 	Evaluate	os.path.dirname("${SUITE_SOURCE}")	os
	[Return] 	${FILE_DIR}


Apply Pacing
	[Arguments]    ${StartTime}    ${MaxTimesPerHour}
	${SecPerIter}= 	Evaluate 	int(3600/${MaxTimesPerHour})
	${NowTime}= 	Get Time 	epoch
	${TimeTaken}= 	Evaluate 	${NowTime}-${StartTime}
	IF 	${TimeTaken} < ${SecPerIter}
		${TimeLeft}= 	Evaluate 	${SecPerIter}-${TimeTaken}
		Sleep    ${TimeLeft}
	END
