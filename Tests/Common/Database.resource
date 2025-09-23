*** Settings ***
Library 	DatabaseLibrary

Resource 	Common.resource

*** Keywords ***
# # # # # # #
# Database: #
# # # # # # #

Find Result DB
	[Arguments] 	${directory}=${RESULTS_DIR} 	${result_pattern}=*_*
	${fols}= 	List Directory 	${directory} 	${result_pattern} 	absolute=True
	Log 	${fols} 	console=${True}

	${file}= 	List Directory 	${fols[-1]} 	*.db 	absolute=True
	Log 	Result DB: ${file[-1]} 	console=${True}
	RETURN 	${file[-1]}

Query Result DB
	[Arguments]		${dbfile} 	${sql} 	${info}=${True}
	Log 	dbfile: ${dbfile} 	console=${info}
	${dbfile}= 	Replace String 	${dbfile} 	${/} 	/

	Connect To Database 	sqlite3 	database=${dbfile} 	isolation_level=${None}
	Log 	sql: ${sql} 	console=${info}
	${result}= 	Query 	${sql}
	Log 	sql result: ${result} 	console=${info}
	Disconnect From Database
	RETURN 	${result}

Wait Until the Query Is Not Empty
	[Arguments]		${dbfile}  ${sql}  ${timeout}=${300}

	VAR 	${iter} 	0
	TRY
		WHILE    True 	limit=${timeout} seconds
			${iter}= 	Evaluate  ${iter} + 1
			IF    ${iter} == 30
				Log 	Query '${sql}' is returning empty row after ${iter} seconds.  level=WARN
			END
			
			TRY
				Sleep 	1s
				${query_result}= 	Query Result DB 	${dbfile}  ${sql}  info=${False}
				${len}= 	Get Length 	${query_result}
				Should Be True 	${len} > 0
			EXCEPT
				CONTINUE
			END
			BREAK
		END
	EXCEPT
		Fail 		Query '${sql}' is returning empty row after ${timeout} seconds.
	END
