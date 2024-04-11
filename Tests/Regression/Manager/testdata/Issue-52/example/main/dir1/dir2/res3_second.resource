*** Variables ***
${string3second}	str3second
@{list3second}	list3second_0	list3second_1

*** Keywords ***
Resource Three Second
	[Documentation] 	RESOURCE FILE PRIOVIDED	
	RETURN	${CURDIR}\n${EXECDIR}