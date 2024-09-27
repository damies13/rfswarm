*** Settings ***
Resource	main.resource
Resource	${CURDIR}${/}dir1${/}res1.resource
Resource	${CURDIR}${/}dir1${/}dir2${/}res2.resource
Resource	${CURDIR}${/}..${/}dir4${/}res-1.resource

*** Test Cases ***
0 Test Resource Files Keywords
	Resource Main
	0 Resource Test

*** Keywords ***
0 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${stringm}
	...    ${listm}
	No Operation

