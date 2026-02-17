*** Test Cases ***
Test Default
	Default
Test ERROR
	Set Log Level 	ERROR
	Test ERROR
Test WARN
	Set Log Level 	WARN
	Test WARN
Test INFO
	Set Log Level 	INFO
	Test INFO
Test DEBUG
	Set Log Level 	DEBUG
	Test DEBUG
Test TRACE
	Set Log Level 	TRACE
	Test TRACE 	2  2

*** Keywords ***
Default
	[Documentation] 	This is a normal keyword.
	${result}= 	Evaluate 	2 + 2
	Should Be Equal As Integers 	${result}	4
	Sleep 	10s

FAIL Keyword
	[Documentation] 	This is a FAIL keyword.
	${result}= 	Evaluate 	2 + 2
	Should Be Equal As Integers 	${result}	5
	Sleep 	10s

Test ERROR
	[Documentation] 	This is a ERROR keyword.
	Log 	Simple ERROR invocation 	level=ERROR
	Sleep 	10s

Test WARN
	[Documentation] 	This is a WARN keyword.
	${result}= 	Evaluate 	2 + 2
	Run Keyword And Warn On Failure
	...    Should Be Equal As Integers 	${result}	5
	Sleep 	10s

Test INFO
	[Documentation] 	This is a INFO keyword.
	${result}= 	Evaluate 	2 + 2
	Should Be Equal As Integers 	${result}	4
	Sleep 	10s

Test DEBUG
	[Documentation] 	This is a DEBUG keyword.
	Log 	Simple DEBUG invocation 	level=DEBUG
	Sleep 	10s

Test TRACE
	[Documentation] 	This is a TRACE keyword.
	[Arguments] 	${str1} 	${str2}
	${result}= 	Evaluate 	${str1} + ${str2}
	Should Be Equal As Integers 	${result}	4
	Sleep 	10s
