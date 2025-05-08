*** Settings ***
Library			String
Library			Collections
Library			RequestsLibrary
Library			json

Suite Setup 	Set Initial Sim Values


*** Variables ***
${HOST}                Undefined
${USERNAME}            Undefined
${PASSWORD}            Undefined

${LastCPU}             0
${LastMEM}             0
${LastSQLRate}         0
${LastSQLLong}         0


*** Tasks ***
Simulated Web Server 1
	VAR 	${HOST} 	SimWeb1 	scope=SUITE
	${stats}=	Collect Stats
	${epoch}=		Get Time	epoch
	Post AUT Stats		${HOST} 	AUT Web 	${epoch}    ${stats}
	Sleep    5

Simulated Web Server 2
	VAR 	${HOST} 	SimWeb2 	scope=SUITE
	${stats}=	Collect Stats
	${epoch}=		Get Time	epoch
	Post AUT Stats		${HOST} 	AUT Web 	${epoch}    ${stats}
	Sleep    5

Simulated Web Server 3
	VAR 	${HOST} 	SimWeb3 	scope=SUITE
	${stats}=	Collect Stats
	${epoch}=		Get Time	epoch
	Post AUT Stats		${HOST} 	AUT Web 	${epoch}    ${stats}
	Sleep    5

Simulated DB Server 1
	VAR 	${HOST} 	SimDB1 		scope=SUITE
	${stats}=	Collect Stats
	${epoch}=		Get Time	epoch
	Post AUT Stats		${HOST} 	AUT DB 	${epoch}    ${stats}
	Sleep    5

Simulated DB Server 2
	VAR 	${HOST} 	SimDB2 		scope=SUITE
	${stats}=	Collect Stats
	${epoch}=		Get Time	epoch
	Post AUT Stats		${HOST} 	AUT DB 	${epoch}    ${stats}
	Sleep    5

*** Keywords ***
Set Initial Sim Values
	${initCPU}= 	Rand Range 	1 	3
	VAR 	${LastCPU} 		${initCPU} 			scope=SUITE
	${initMEM}= 	Rand Range 	10 	20
	VAR 	${LastMEM} 		${initMEM} 			scope=SUITE


Collect Stats
	${stats}=	Create Dictionary

	${cpuval}= 	GenSimCPU
	Set To Dictionary	${stats} 	CPU		${cpuval}
	${memval}= 	GenSimMEM
	Set To Dictionary	${stats} 	MEM		${memval}

	RETURN 	${stats}

GenSimCPU
	${currmax}= 	Evaluate    int(${LastCPU} * 100 * 1.1)
	${currmin}= 	Evaluate    int(${LastCPU} * 100 * 0.9)
	${newv100}= 	Rand Range 	${currmin} 	${currmax}
	${new1}= 	Evaluate    ${newv100} / 100
	VAR 	${LastCPU} 		${new1} 	scope=SUITE
	RETURN 	${new1}

GenSimMEM
	${currmax}= 	Evaluate    int(${LastMEM} * 100 * 1.02)
	${currmin}= 	Evaluate    int(${LastMEM} * 100 * 0.98)
	${newv100}= 	Rand Range 	${currmin} 	${currmax}
	${new1}= 	Evaluate    ${newv100} / 100
	VAR 	${LastMEM} 		${new1} 	scope=SUITE
	RETURN 	${new1}

Post AUT Stats
	[Documentation]		SSH: Post AUT Stats
	[Arguments]		${AUT}	${AUTType}	${AUTTime}    ${Stats}

	# keyword from Requests Library, reuse the session rather than creating a new one if possible
	${exists}= 	Session Exists	rfs
	IF 	not(${exists})
		Create Session	rfs 	${RFS_SWARMMANAGER}
	END

	${data}=	Create Dictionary
	Set To Dictionary	${data} 	AgentName				${RFS_AGENTNAME}
	Set To Dictionary	${data} 	PrimaryMetric		${AUT}
	Set To Dictionary	${data} 	MetricType			${AUTType}
	Set To Dictionary	${data} 	MetricTime			${AUTTime}
	Set To Dictionary	${data} 	SecondaryMetrics	${Stats}

	# keyword from json Library
	${string_json}= 	json.Dumps	${data}

	# keyword from Requests Library
	${resp}=	POST On Session 	rfs 	/Metric 	${string_json}
	Log	${resp}
	Log	${resp.content}
	Should Be Equal As Strings	${resp.status_code}	200

Rand Range
	[Arguments] 	${min}		${max}
	${random}= 	Evaluate 	random.randint(${min}, ${max})
	RETURN 		${random}
