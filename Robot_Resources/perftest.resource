*** Settings ***
Documentation     perftest.resource - v0.0.2
...                Keywords to make using RFSwarm Easier

Library           OperatingSystem
Library           String

*** Variables ***
${STT_MIN}    15
${STT_MAX}    45

*** Keywords ***
Standard Think Time
	[Documentation]    This keyword will choose a random number between a predifined
	...                minimum and maximum time, and then sleep for that many seconds
	...                - The default minimum is 15 seconds
	...                - The default maximum is 45 seconds
	...                The default valuses can be changed by overriding the test
	...                variables ${STT_MIN} and ${STT_MAX}
	${number}    Evaluate    random.randint(${STT_MIN}, ${STT_MAX})    random
	Log    Standard Think Time (${number})
	Sleep    ${number}

Get Data Row
	[Arguments]    ${FileName}    ${Row}="Random"
	[Documentation]    This keyword gets a row of data from a CSV or TSV file,
	...                takes 1-2 arguments:
	...                 - FileName (Required)
	...                 - Row (Optional) can be Random, Sequential or a number
	...                   defaults to Random
	# Log    Get Data Row: \tFileName: ${FileName} \tRow: ${Row}
	${RAW_FILE} = 	Get File	${FileName}
	@{FILE_LINES} = 	Split To Lines	${RAW_FILE}
	${LINE_COUNT} = 	Get Length    ${FILE_LINES}

	${FILE_SEQUENTIAL_NUM} =	Get Variable Value	${FILE_SEQUENTIAL_NUM}	0

	@{delim_cols} = 	Split String	${FILE_LINES}[0]	,
	${delim_cols_len} = 	Get Length    ${delim_cols}
	${DELIMITER} =	Set Variable If	${delim_cols_len} > 1	,	\t
	@{FILE_COLUMNS} = 	Split String	${FILE_LINES}[0]	${DELIMITER}
	${COLUMNS_COUNT} = 	Get Length    ${FILE_COLUMNS}

	${ROW_NUM} = 	Set Variable    ${Row}
	${ROW_NUM} = 	Run Keyword If    ${Row}=="Random"	Evaluate    random.randint(1, ${LINE_COUNT}-1)    random
					... 	ELSE	Set Variable    ${ROW_NUM}
	${ROW_NUM} = 	Run Keyword If    ${Row}=="Sequential"    Evaluate    ${FILE_SEQUENTIAL_NUM} + 1
					... 	ELSE	Set Variable    ${ROW_NUM}

	Set Test Variable	\${FILE_SEQUENTIAL_NUM}	${FILE_SEQUENTIAL_NUM}

	@{ROW_COLUMNS} = 	Split String	${FILE_LINES}[${ROW_NUM}]	${DELIMITER}
	# :FOR ${I}	Input Text    locator    text
	FOR	${I}	IN RANGE	${COLUMNS_COUNT}
		# Log    \${I} ${I}
		${VAR_NAME} = 	Set Variable    ${FILE_COLUMNS}[${I}]
		${VAR_VALUE} = 	Set Variable    ${ROW_COLUMNS}[${I}]
		# Log    \${VAR_NAME}: ${VAR_NAME}\t\${VAR_VALUE}: ${VAR_VALUE}
		Set Test Variable	${${VAR_NAME}}	${VAR_VALUE}
	END
	# Log Variables

Get File Dir
	[Documentation]    This keyword returns directory where the test suite is located
	...                e.g. if the ${SUITE_SOURCE} is c:\path\to\testsuite.robot
	...                     this keyword would return c:\path\to
	${FILE_DIR}=    Evaluate    os.path.dirname("${SUITE_SOURCE}")    os
	RETURN    ${FILE_DIR}

Apply Pacing
	[Documentation]    This keyword is used to ensure your tests do not exceed a desired rate limit
	...                i.e. do not exceed n tests per robot per hour
	...
	...                This should be used as the last keyword in your test case
	...
	...                Pass 2 arguments to this keyword:
	...                - StartTime: This should be the epoch time for when the test started
	...                             and can be created using `${StartTime}= 	Get Time 	epoch`
	...                - MaxTimesPerHour: This is a number representing the manximum number of times
	...                                   per hour you want the test to run
	...
	...                This keyword will substract the start time from the current time to work out
	...                how many seconds the test took, and also the number of seconds the test should
	...                take, and then calculates the number of seconds to sleep to maintain the rate
	...                limit, if the number of seconds to sleep is 0 or less the keyword will exit immidatly
	[Arguments]    ${StartTime}    ${MaxTimesPerHour}
	${SecPerIter}=    Evaluate    int(3600/${MaxTimesPerHour})
	${NowTime}=    Get Time    epoch
	${TimeTaken}=    Evaluate    ${NowTime}-${StartTime}
	IF    ${TimeTaken} < ${SecPerIter}
		${TimeLeft}=    Evaluate    ${SecPerIter}-${TimeTaken}
		Sleep    ${TimeLeft}
	END

Syncronise On Timestamp
	[Documentation]    This keyword is to assist with spike testing by making all robots wait untill a specific
	...                point in time as defined by the mask argument.
	...
	...                The default mask is '0', but you can pass any string of numbers as the mask
	...                This keyword will get the current time in seconds (epoch time) and then calculate the number
	...                of seconds untill the last n digits of the future epoch time will match the mask, and will
	...                then sleep that many seconds.
	...
	...                All robots containing this keyword will sleep untill the same second matching the mask and
	...                then continue at the same second, thus creating an artificial spike on the system under test
	...
	...                Examples of the maximum time a robot will wait based on the mask used:
	...                Mask '0' (default)     10 seconds
	...                Mask '00'              100 seconds     1 Minute 40 Seconds
	...                Mask '000'             1000 seconds    16 Minutes 40 Seconds
	...                Mask '0000'            10000 seconds   2 Hours 46 Minutes 40 Seconds
	...
	...                Using another number other than 0 doesn't change the maximum time a robot will wait, it only
	...                changes the time used for a syncronisation point, e.g. a mask of '88' will wait untill the next
	...                epoch time ends with 88 which is still upto 100 seconds from the current epoch time.
	...                (300-200=100 and 388-288=100)
	[Arguments]    ${mask}=0
	${lenmask}=    Get Length    ${mask}
	${now}=    Get Time    epoch
	${strnow}=    Convert To String    ${now}
	${lennow}=    Get Length    ${strnow}
	${nowprefix}=    Evaluate    ${strnow}[:-${lenmask + 1}]
	${nowinc}=    Evaluate    ${strnow}[-${lenmask + 1}]
	IF    ${nowinc} == 9
		${nowprefix}=    Evaluate    ${strnow}[:-${lenmask + 2}]
		${nowinc}=    Evaluate    ${strnow}[-${lenmask + 2}:-${lenmask}]
		${nowinc}=    Convert To Integer    ${nowinc}
		${WaitTill}=    Catenate    SEPARATOR=    ${nowprefix}    ${nowinc + 1}    ${mask}
	ELSE
		${nowinc}=    Convert To Integer    ${nowinc}
		${WaitTill}=    Catenate    SEPARATOR=    ${nowprefix}    ${nowinc + 1}    ${mask}
	END
	${WaitTill}=    Convert To Integer    ${WaitTill}
	${SecToWait}=    Evaluate    ${WaitTill} - ${now}
	Log    Wait untill: ${WaitTill} \t Seconds To Wait: ${SecToWait} 	console=true
	Sleep    ${SecToWait}
