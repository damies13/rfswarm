*** Variables ***
${stringm}	strm
@{listm}	listm_0	listm_1

*** Keywords ***
Resource Main
	[Documentation] 	RESOURCE FILE PRIOVIDED
	RETURN	${CURDIR}\n${EXECDIR}

