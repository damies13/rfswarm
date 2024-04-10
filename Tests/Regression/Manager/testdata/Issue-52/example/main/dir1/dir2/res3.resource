*** Settings ***
Resource	res3_second.resource

*** Variables ***
${string3}	str3
@{list3}	list3_0	list3_1

*** Keywords ***
Resource Three
	Resource Three Second
	Log 	${string3second}
	Log 	${list3second}

	RETURN	${CURDIR}\n${EXECDIR}