*** Variables ***
${endpoint} 	my endpoint
${env} 			QAENV

*** Test Cases ***
Send GET on API ${endpoint} on ${env}
	Log Data 1
	Log Data 2
	Log Data 3
	Sleep 	10
Do Not Use Test Case
	Do Not

*** Keywords ***
Do Not
	Log 	Do not use me.

Log Data 1
	Log 	${endpoint}

Log Data 2
	Log 	${env}

Log Data 3
	Log 	${TEST_NAME}
