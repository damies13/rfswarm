*** Settings ***
Resource	${CURDIR}${/}..${/}..${/}..${/}..${/}res0.resource

*** Variables ***
${string3}	str3
@{list3}	list3_0	list3_1

*** Keywords ***
Resource Three
	[Documentation] 	RESOURCE FILE PRIOVIDED	
	RETURN	${CURDIR}\n${EXECDIR}

