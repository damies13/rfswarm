
*** Test Cases ***

Check OS
	${uname}= 	Evaluate 	sys.platform		sys
	Log 	${uname}
	Log to console 	${uname}

Check Dir
	Log to console 	${CURDIR}
