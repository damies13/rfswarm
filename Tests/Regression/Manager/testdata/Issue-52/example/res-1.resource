*** Variables ***
${string-1}	str-1
@{list-1}	list-1_0	list-1_1

*** Keywords ***
Resource Minus One
	[Documentation] 	RESOURCE FILE PRIOVIDED	
	RETURN	${CURDIR}\n${EXECDIR}