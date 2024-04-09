*** Settings ***
Resource	main.resource
Resource	${CURDIR}/dir1/res1.resource
Resource	${CURDIR}/dir1/dir2/res2.resource
Resource	${CURDIR}/dir1/dir2/res3.resource
Resource	${CURDIR}/../res0.resource

*** Test Cases ***
0 Test Resource Files Keywords
	Resource Main
	Log 	${stringm}
	Log 	${listm}
1 Test Resource Files Keywords
	Resource One
	Log 	${string1}
	Log 	${list1}
2 Test Resource Files Keywords
	Resource Two
	Log 	${string2}
	Log 	${list2}
3 Test Resource Files Keywords
	Resource Three
	Log 	${string3}
	Log 	${list3}
	Log 	${string3second}
	Log 	${list3second}
4 Test Resource Files Keywords
	Resource Zero
	Log 	${string0}
	Log 	${list0}