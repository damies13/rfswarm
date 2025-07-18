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
	[Arguments]		${dbfile} 	${sql}
	Log 	dbfile: ${dbfile} 	console=${True}
	${dbfile}= 	Replace String 	${dbfile} 	${/} 	/

	Connect To Database 	sqlite3 	database=${dbfile} 	isolation_level=${None}
	Log 	sql: ${sql} 	console=${True}
	${result}= 	Query 	${sql}
	Log 	sql result: ${result} 	console=${True}
	Disconnect From Database
	RETURN 	${result}