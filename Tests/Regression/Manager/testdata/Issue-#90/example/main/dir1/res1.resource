*** Variables ***
${string1}	str1
@{list1}	list1_0	list1_1

*** Keywords ***
Resource One
	[Documentation] 	RESOURCE FILE PRIOVIDED	
	RETURN	${CURDIR}\n${EXECDIR}

