*** Settings ***
Resource	main.resource
Resource	${CURDIR}${/}dir1${/}res1.resource
Resource	${CURDIR}${/}dir1${/}dir2${/}res2.resource
Resource	${CURDIR}${/}dir1${/}dir2${/}res3.resource
Resource	${CURDIR}${/}..${/}res-1.resource
Resource	${CURDIR}${/}..${/}res0.resource

Variables	${CURDIR}${/}dir1${/}vars.py
Variables	${CURDIR}${/}..${/}vars0.py

Library 	OperatingSystem
Metadata	File	${CURDIR}${/}dir1${/}manager_windows_agents_ready.png
Metadata	File	${CURDIR}${/}dir1${/}dir2${/}example.csv
Metadata	File	${CURDIR}${/}dir1${/}dir2${/}dir3${/}*.jpg
Metadata	File	${CURDIR}${/}..${/}dir4${/}*.*
Metadata	File	${CURDIR}${/}..${/}excel_example.xlsx

*** Test Cases ***
0 Test Resource Files Keywords
	Resource Main
	0 Resource Test

1 Test Resource Files Keywords
	Resource One
	1 Resource Test

2 Test Resource Files Keywords
	Resource Two
	2 Resource Test

3 Test Resource Files Keywords
	Resource Three
	3 Resource Test

4 Test Resource Files Keywords
	Resource Zero
	4 Resource Test

5 Test Variable File
	Variable test

6 Test Metadata File
	Metadata test

*** Keywords ***
0 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${stringm}
	...    ${listm}
	No Operation

1 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${string1}
	...    ${list1}
	No Operation

2 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${string2}
	...    ${list2}
	No Operation

3 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${string3}	
	...    ${list3}	
	...    ${string3second}	
	...    ${list3second}
	No Operation

4 Resource Test
	[Documentation] 	${TEST NAME}:	
	...    ${string4}
	...    ${list4}
	No Operation

Variable test
	[Documentation] 	${TEST NAME}:
	...    ${stringpy}	
	...    ${listpy}
	No Operation

Metadata test
	[Documentation] 	${TEST NAME}:
	File Should Exist	${CURDIR}${/}dir1${/}manager_windows_agents_ready.jpg
	Get File	${CURDIR}${/}dir1${/}dir2${/}example.csv
