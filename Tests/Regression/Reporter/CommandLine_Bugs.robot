*** Settings ***
Resource 	CommandLine_Common.robot

*** Test Cases ***
Check If The Not Buildin Modules Are Included In The Reporter Setup File
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	${imports}	Get Modules From Program .py File That Are Not BuildIn
	...    ${CURDIR}..${/}..${/}..${/}..${/}rfswarm_reporter${/}rfswarm_reporter.py	4

	Log	${imports}

	${requires}	Get Install Requires From Setup File
	...    ${CURDIR}..${/}..${/}..${/}..${/}setup-reporter.py

	Log	${requires}

	FOR  ${i}  IN  @{imports}
		Should Contain	${requires}	${i}
		...    msg="Some modules are not in manager setup file"
	END
