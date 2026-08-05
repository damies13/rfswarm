*** Settings ***
Documentation		This Demo Test is for demonstrating and troubleshooting RFSwarm,
...							It's known to work on any OS and only requires robot framework installed, no other libraries
...							It also demonstrates the custom variables created by RFSwarm

Library         OperatingSystem

*** Variables ***
${PATH}         ${CURDIR}/example.txt
${alpha}	abcdefghijklmnopqrstuvwxyz
${alpha10}	${alpha * 10}
${alpha100}	${alpha10 * 10}
${alpha1k}	${alpha100 * 10}
${FPATH}	${CURDIR}/Robot_${RFS_ROBOT}

*** Test Cases ***
RFSwarm Demo Test
	# Create File          ${PATH}    Some text
	# File Should Exist    ${PATH}
	# Copy File            ${PATH}    ~/file.txt
	Create Some Files
	Sleep    5

	List Some Files
	Sleep    5

	Remove Some Files
	Sleep    5

	RFS Variables


*** Keywords ***
Create Some Files
	[Documentation]		Create Some Files
	Create Directory	${FPATH}
	FOR	${i}	IN RANGE	100
		Create File		${FPATH}/I${RFS_ITERATION}_i${i}_test.txt    ${alpha1k}
	END
	Wait Until Created	${FPATH}/I${RFS_ITERATION}_i99_test.txt

List Some Files
	[Documentation]		List Some Files
	${FILS}=	List Files In Directory 	${FPATH}

Remove Some Files
	[Documentation]		Remove Some Files
	Remove Files	${FPATH}/I${RFS_ITERATION}_*_test.txt
	Wait Until Removed	${FPATH}/I${RFS_ITERATION}_i99_test.txt

RFS Variables
	[Documentation]		Show the RFS Variables
	Log		${RFS_AGENTNAME}
	Log		${RFS_AGENTVERSION}
	Log		${RFS_DEBUGLEVEL}
	Log		${RFS_EXCLUDELIBRARIES}
	Log		${RFS_INDEX}
	Log		${RFS_ITERATION}
	Log		${RFS_ROBOT}
	Log		${RFS_SWARMMANAGER}


#
