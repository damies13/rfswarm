*** Settings ***
Documentation 	This resource file contains keywords for Manager command line only.

Resource 	../../../Common/Common.resource

Library 	RequestsLibrary

*** Keywords ***
Send ${type} Request To the Manager
	[Arguments] 	${url}=/ 	${request}=${None}
	Create Session 	Manager API  http://localhost:8138
	${resp}= 	Run Keyword 	${type} On Session  Manager API  ${url}  json=${request}

	Should Be Equal As Strings 	${resp.reason}  OK
	Log 	${resp.json()}

	RETURN 	${resp}

