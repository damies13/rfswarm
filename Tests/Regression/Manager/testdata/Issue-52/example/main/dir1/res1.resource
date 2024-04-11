*** Variables ***
${string1}	str1
@{list1}	list1_0	list1_1

*** Keywords ***
Resource One
	[Documentation]	
	...    \n${CURDIR}	
	...    ${EXECDIR}
	RETURN	${CURDIR}\n${EXECDIR}