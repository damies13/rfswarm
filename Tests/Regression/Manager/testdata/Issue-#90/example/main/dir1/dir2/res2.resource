*** Settings ***
Resource	${CURDIR}${/}dir3${/}res3.resource

*** Variables ***
${string2}	str2
@{list2}	list2_0	list2_1

*** Keywords ***
Resource Two
	[Documentation] 	RESOURCE FILE PRIOVIDED	
	RETURN	${CURDIR}\n${EXECDIR}

