*** Settings ***
Library    ./InfoLibrary.py

*** Test Cases ***
Issue #154 Test Case
	Default Keyword Name
	Quiet Keyword Name
	Doc Keyword 		Doc Keyword Message
	Doc Only Keyword 		Doc Keyword Message
	Info Keyword 		Message for Info Keyword

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
