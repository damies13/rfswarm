
*** Test Cases ***
Test Scenario 1
	App Login
	Load Page A

Test Scenario 2
	App Login
	Load Page B

*** Keywords ***
App Login
	[Documentation]		Logon to Application
	Sleep 	1
	${random}= 	Evaluate 	random.randint(0, 3)
	Sleep 	${random}

Load Page A
	[Documentation]		Load Page for Business Area A
	${random}= 	Evaluate 	random.uniform(0.5, 5.0)
	Sleep 	${random}

Load Page B
	[Documentation]		Load Page for Business Area B
	${random}= 	Evaluate 	random.uniform(0.25, 3.0)
	Sleep 	${random}
