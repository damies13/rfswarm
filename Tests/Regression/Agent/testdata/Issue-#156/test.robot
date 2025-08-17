*** Variables ***
${endpoint} 	my endpoint
${env} 			QAENV

*** Test Cases ***
Send GET on API ${endpoint} on ${env}
	Log 	${endpoint}
	Log 	${env}
	Log 	${TEST_NAME}
	Sleep 	10
