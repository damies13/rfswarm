*** Variables ***
${stringm}	strm
@{listm}	listm_0	listm_1

*** Keywords ***
Resource Main
	[Documentation]	
	...    \n${CURDIR}	
	...    ${EXECDIR}
	RETURN	${CURDIR}\n${EXECDIR}