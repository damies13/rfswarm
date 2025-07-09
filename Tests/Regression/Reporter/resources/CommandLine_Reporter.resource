*** Settings ***
Documentation 	This resource file contains keywords for Reporter command line only.

Resource 	../../../Common/Common.resource

# *** Variables ***
# ${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

# *** Keywords ***
# Open Reporter
# 	[Arguments]		@{appargs}
# 	${var}= 	Get Variables
# 	Log 	${var}
# 	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout_reporter.txt 	stderr=${OUTPUT DIR}${/}stderr_reporter.txt
# 	Set Suite Variable 	$process 	${process}
# 	Sleep	3
