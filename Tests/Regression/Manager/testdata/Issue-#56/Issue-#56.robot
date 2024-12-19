*** Settings ***
Library    InfoLibrary.py

*** Test Cases ***
Example Test Case
	Default Keyword Name
	Quiet Keyword Name
	Doc Keyword 		Doc Keyword Message
	Doc Only Keyword 	Doc Keyword Message
	Info Keyword 		Message for Info Keyword
	${dont_display}=	Return Only Keyword 	Hello
	Argument Keyword 		Arg1

*** Keywords ***
Default Keyword Name
	[Documentation] 	Default Keyword Documentation
	# ...								This keyword demonstrates the default keyword response name method
	# ...								for use by RFSwarm
	Log 	Default Log Message

Quiet Keyword Name
	# ...								This keyword demonstrates the quiet keyword response name method
	# ...								for use by RFSwarm
	Log 	This is a quiet keyword that should not show by default

Argument Keyword
	[Arguments] 	${arg}
	# ...								This keyword demonstrates the quiet keyword response name method
	# ...								for use by RFSwarm
	Log 	${arg}