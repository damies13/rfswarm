*** Test Cases ***

Check OS
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${uname}= 	Evaluate 	sys.platform		sys
	Log 	${uname}
	Log to console 	${uname}

Check Dir
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	Log to console 	${CURDIR}
	Log to console 	${EXECDIR}
