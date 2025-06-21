*** Settings ***
Documentation 	This resource file contains keywords for Reporter command line only.

Resource 	../../Common/Common.resource

*** Variables ***
${cmd_reporter} 	rfswarm-reporter
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

*** Keywords ***
Open Reporter
	[Arguments]		@{appargs}
	${var}= 	Get Variables
	Log 	${var}
	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout_reporter.txt 	stderr=${OUTPUT DIR}${/}stderr_reporter.txt
	Set Suite Variable 	$process 	${process}
	Sleep	3

Get Reporter PIP Data
	Run Process	pip	show	rfswarm-reporter		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Reporter must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Get Reporter Default Save Path
	${pip_data}=	Get Reporter PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_reporter${/}

Get Reporter INI Location
	${location}=	Get Reporter Default Save Path
	RETURN	${location}${/}RFSwarmReporter.ini
