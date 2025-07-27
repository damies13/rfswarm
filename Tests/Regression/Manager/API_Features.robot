*** Settings ***
Test Tags 	CommandLine 	Features 	API

Resource 	resources/CommandLine_Manager.resource
Resource 	resources/API_Manager.resource
Resource 	../../Common/Database.resource

Variables 	resources${/}API_expected_responses.yaml

Suite Setup 	Common.Basic Suite Initialization Manager

*** Test Cases ***
GET /
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Create Directory 	${RESULTS_DIR}
	Sleep 	3s
	${resp_get}= 	Send GET Request To the Manager 	url=/
	&{get_result}= 	Convert To Dictionary 	${resp_get.json()}
	Log 	GET / call restult:${\n} ${get_result} 	console=True

	Log 	------- RESPONSE ------- 	console=${True}
	# Validate GET Response 	AgentStatus
	Should Be Equal As Strings 		${get_result}[POST][AgentStatus][URI] 	${GET}[AgentStatus][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][AgentStatus][Body] 	${GET}[AgentStatus][Body]

	Should Be Equal As Strings 		${get_result}[POST][Jobs][URI] 			${GET}[Jobs][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][Jobs][Body] 		${GET}[Jobs][Body]

	Should Be Equal As Strings 		${get_result}[POST][Scripts][URI] 		${GET}[Scripts][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][Scripts][Body] 		${GET}[Scripts][Body]

	Should Be Equal As Strings 		${get_result}[POST][File][URI] 			${GET}[File][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][File][Body] 		${GET}[File][Body]

	Should Be Equal As Strings 		${get_result}[POST][Result][URI] 		${GET}[Result][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][Result][Body] 		${GET}[Result][Body]

	Should Be Equal As Strings 		${get_result}[POST][Metric][URI] 		${GET}[Metric][URI]
	Dictionaries Should Be Equal 	${get_result}[POST][Metric][Body] 		${GET}[Metric][Body]

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

POST /AgentStatus
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Create Directory 	${RESULTS_DIR}
	${ipv4} 	${ipv6} 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]
	VAR 	&{request_body} 	AgentName=${POST_AgentStatus}[Body][AgentName]  Status=Ready  AgentIPs=${Agent_IP}  Robots=${0}  CPU%=${4.7}  MEM%=${30.97}  NET%=${0.01}

	Sleep 	3s
	${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}
	&{post_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /AgentStatus call restult:${\n} ${post_result} 	console=True

	Log 	------- RESPONSE ------- 	console=${True}
	Dictionaries Should Be Equal 	${post_result} 	${POST_AgentStatus}[Body]

	Log 	------- DATABASE ------- 	console=${True}
	Sleep 	1s
	${prerun_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*PreRun*

	VAR 	${query} 	SELECT AgentName, AgentStatus, AgentRobots, AgentCPU, AgentMEM, AgentNET FROM AgentList
	@{query_result}= 	Query Result DB 	${prerun_DB} 	${query}
	Log 	${query_result}
	VAR 	${last_row} 	${query_result}[-1]
	Remove From Dictionary 	${request_body} 	AgentIPs
	@{expected_row}= 	Get Dictionary Values 	${request_body} 	sort_keys=${False}
	Convert List Items To String 	${expected_row}
	Diff Lists 	${last_row} 	${expected_row} 	message=The saved row in the PreRun database after POST request is invalid.

	VAR 	${query} 	SELECT PrimaryMetric, MetricType, SecondaryMetric, MetricValue FROM MetricData WHERE SecondaryMetric = 'IPAddress'
	@{query_result}= 	Query Result DB 	${prerun_DB} 	${query}
	Log 	${query_result}
	Length Should Be 	${query_result} 	2
	VAR 	@{expected_row_0} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress  ${ipv4}[0]
	VAR 	@{expected_row_1} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress  ${ipv6}[0]
	TRY
		Diff Lists 	${query_result}[0] 	${expected_row_0} 	message=The saved row in the PreRun database after POST request is invalid.
		Diff Lists 	${query_result}[1] 	${expected_row_1} 	message=The saved row in the PreRun database after POST request is invalid.
	EXCEPT
		Diff Lists 	${query_result}[1] 	${expected_row_0} 	message=The saved row in the PreRun database after POST request is invalid.
		Diff Lists 	${query_result}[0] 	${expected_row_1} 	message=The saved row in the PreRun database after POST request is invalid.
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

POST /Jobs
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Agent CLI  -a  ${POST_Jobs}[Body][AgentName] 	AND
	...    Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs

	Create Directory 	${RESULTS_DIR}
	VAR 	${robot_1} 			1_Issue-#289.robot
	VAR 	${robot_2} 			2_Issue-#289.robot
	VAR 	${testcase_1} 		Example Test Case One One
	VAR 	${testcase_2} 		Example Test Case Two One
	VAR 	&{request_body} 	AgentName=${POST_Jobs}[Body][AgentName]

	Sleep 	50s
	${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}
	&{post_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Jobs call restult:${\n} ${post_result} 	console=True

	Log 	------- RESPONSE ------- 	console=${True}
	VAR 	${schedule} 	${post_result}[Schedule]
	Log 	${schedule}
	@{schedule_keys}= 	Get Dictionary Keys 	${schedule}
	# FOR  ${key}  IN  @{schedule_keys}
	# 	Remove From Dictionary 	${schedule}[${key}]  ScriptHash  StartTime  EndTime  id
	# END
	Remove Keys From Dictionary  ${schedule}  ScriptHash  StartTime  EndTime  id

	Should Be Equal As Strings 		${post_result}[AgentName] 	${POST_Jobs}[Body][AgentName]
	Should Be Equal As Strings 		${post_result}[Abort] 		${POST_Jobs}[Body][Abort]
	Should Be Equal As Strings 		${post_result}[UploadMode] 	${POST_Jobs}[Body][UploadMode]

	Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[0]] 	${POST_Jobs.Body}[Schedule][${11}]
	Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[1]] 	${POST_Jobs.Body}[Schedule][${21}]
	Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[2]] 	${POST_Jobs.Body}[Schedule][${22}]

	Log 	------- DATABASE ------- 	console=${True}
	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*POST_Jobs*

	VAR 	${query} 	SELECT MetricValue FROM MetricData WHERE PrimaryMetric = 'Time' AND SecondaryMetric = 'Start'
	@{query_result}= 	Query Result DB 	${result_DB} 	${query}
	Log 	${query_result}
	VAR 	${first_row} 	${query_result}[0][0]
	#Should Be Equal 	${first_row} 	${post_result}[StartTime] 				??? in db greater by 1 sec

	VAR 	${query} 	SELECT MetricValue FROM MetricData WHERE PrimaryMetric = '1' AND SecondaryMetric = '${robot_1}'
	@{query_result}= 	Query Result DB 	${result_DB} 	${query}
	Log 	${query_result}
	VAR 	${last_row} 	${query_result}[-1][0]
	Should Be Equal 	${last_row} 	${testcase_1}

	VAR 	${query} 	SELECT MetricValue FROM MetricData WHERE PrimaryMetric = '2' AND SecondaryMetric = '${robot_2}'
	@{query_result}= 	Query Result DB 	${result_DB} 	${query}
	Log 	${query_result}
	VAR 	${last_row} 	${query_result}[-1][0]
	Should Be Equal 	${last_row} 	${testcase_2}

	VAR 	${query} 	SELECT MetricValue FROM MetricData WHERE PrimaryMetric = 'Robots_1' AND SecondaryMetric = '${testcase_1}'
	@{query_result}= 	Query Result DB 	${result_DB} 	${query}
	Log 	${query_result}
	VAR 	${last_row} 	${query_result}[-1][0]
	Should Be Equal 	${last_row} 	1

	VAR 	${query} 	SELECT MetricValue FROM MetricData WHERE PrimaryMetric = 'Robots_2' AND SecondaryMetric = '${testcase_2}'
	@{query_result}= 	Query Result DB 	${result_DB} 	${query}
	Log 	${query_result}
	VAR 	${last_row} 	${query_result}[-1][0]
	Should Be Equal 	${last_row} 	2

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Stop Agent CLI 	AND 	Clear Result Directory

POST /Scripts
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Agent CLI  -a  ${POST_Scripts}[Body][AgentName] 	AND
	...    Run Manager CLI  -n  -a  2  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs

	Create Directory 	${RESULTS_DIR}
	VAR 	${robot_1} 			1_Issue-#289.robot
	VAR 	${robot_2} 			2_Issue-#289.robot
	VAR 	${testcase_1} 		Example Test Case One One
	VAR 	${testcase_2} 		Example Test Case Two One
	VAR 	&{request_body} 	AgentName=${POST_Scripts}[Body][AgentName]

	Sleep 	50s
	${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}
	&{post_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Scripts call restult:${\n} ${post_result} 	console=True

	Log 	------- RESPONSE ------- 	console=${True}
	Should Be Equal As Strings 		${post_result}[AgentName] 	${POST_Scripts}[Body][AgentName]

	Dictionaries Should Be Equal 	${post_result}[Scripts][0] 	${POST_Scripts}[Body][Scripts][0]
	Dictionaries Should Be Equal 	${post_result}[Scripts][1] 	${POST_Scripts}[Body][Scripts][1]

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Stop Agent CLI 	AND 	Clear Result Directory

POST /File
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Agent CLI  -a  ${POST_File}[Body_Download][AgentName] 	AND
	...    Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs

	Create Directory 	${RESULTS_DIR}
	VAR 	${robot_1} 			1_Issue-#289.robot
	VAR 	${robot_2} 			2_Issue-#289.robot
	VAR 	${testcase_1} 		Example Test Case One One
	VAR 	${testcase_2} 		Example Test Case Two One
	VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download  Hash=${POST_File}[Body_Download][Hash]
	VAR 	&{request_Status_1} 		AgentName=${POST_File}[Body_Status_1][AgentName]  Action=Status  Hash=${POST_File}[Body_Status_1][Hash]
	VAR 	&{request_Status_2} 		AgentName=${POST_File}[Body_Status_2][AgentName]  Action=Status  Hash=${POST_File}[Body_Status_2][Hash]
	VAR 	&{request_Upload} 		AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=${POST_File}[Body_Upload][Hash]
	...    File=resources/3_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

	Sleep 	45s
	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}
	&{post_result_download}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call download restult:${\n} ${post_result_download} 	console=True

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_1}
	&{post_result_status_1}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call status restult:${\n} ${post_result_status_1} 	console=True

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_2}
	&{post_result_status_2}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call status restult:${\n} ${post_result_status_1} 	console=True

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
	&{post_result_upload}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call upload restult:${\n} ${post_result_upload} 	console=True

	Log 	------- RESPONSE ------- 	console=${True}
	Length Should Be 	${post_result_download}  4
	Should Be Equal As Strings 		${post_result_download}[AgentName] 	${POST_File}[Body_Download][AgentName]
	Should Be Equal As Strings 		${post_result_download}[Hash] 		${POST_File}[Body_Download][Hash]
	Should Be Equal As Strings 		${post_result_download}[File] 		${POST_File}[Body_Download][File]
	Should Be Equal As Strings 		${post_result_download}[FileData] 	${POST_File}[Body_Download][FileData]

	Length Should Be 	${post_result_status_1}  3
	Should Be Equal As Strings 		${post_result_status_1}[AgentName] 	${POST_File}[Body_Status_1][AgentName]
	Should Be Equal As Strings 		${post_result_status_1}[Hash] 		${POST_File}[Body_Status_1][Hash]
	Should Be Equal As Strings 		${post_result_status_1}[Exists] 		${POST_File}[Body_Status_1][Exists]

	Length Should Be 	${post_result_status_2}  3
	Should Be Equal As Strings 		${post_result_status_2}[AgentName] 	${POST_File}[Body_Status_2][AgentName]
	Should Be Equal As Strings 		${post_result_status_2}[Hash] 		${POST_File}[Body_Status_2][Hash]
	Should Be Equal As Strings 		${post_result_status_2}[Exists] 		${POST_File}[Body_Status_2][Exists]

	Length Should Be 	${post_result_upload}  3
	Should Be Equal As Strings 		${post_result_upload}[AgentName] 	${POST_File}[Body_Upload][AgentName]
	Should Be Equal As Strings 		${post_result_upload}[Hash] 		${POST_File}[Body_Upload][Hash]
	Should Be Equal As Strings 		${post_result_upload}[Result] 		${POST_File}[Body_Upload][Result]

	Log 	------- DATABASE ------- 	console=${True}


	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Stop Agent CLI 	AND 	Clear Result Directory

POST /Result
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	${ipv4} 	${ipv6} 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]
	VAR 	&{request_body} 	AgentName=${POST_AgentStatus}[Body][AgentName]  Status=Ready  AgentIPs=${Agent_IP}  Robots=${0}  CPU%=${4.7}  MEM%=${30.97}  NET%=${0.01}

	Sleep 	3s
	Create Session 	Manager API  http://localhost:8138
	${resp_post}= 	POST On Session  Manager API  /AgentStatus  json=${request_body}

	Should Be Equal As Strings 	${resp_post.reason}  OK
	Log 	${resp_post.json()}
	&{get_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /AgentStatus call restult:${\n} ${get_result} 	console=True

	Dictionaries Should Be Equal 	${get_result} 	${POST_AgentStatus.Body}


	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Stop Agent CLI 	AND 	Clear Result Directory

POST /Metric
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR} 	${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	${ipv4} 	${ipv6} 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]
	VAR 	&{request_body} 	AgentName=${POST_AgentStatus}[Body][AgentName]  Status=Ready  AgentIPs=${Agent_IP}  Robots=${0}  CPU%=${4.7}  MEM%=${30.97}  NET%=${0.01}

	Sleep 	3s
	Create Session 	Manager API  http://localhost:8138
	${resp_post}= 	POST On Session  Manager API  /AgentStatus  json=${request_body}

	Should Be Equal As Strings 	${resp_post.reason}  OK
	Log 	${resp_post.json()}
	&{get_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /AgentStatus call restult:${\n} ${get_result} 	console=True

	Dictionaries Should Be Equal 	${get_result} 	${POST_AgentStatus.Body}


	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Stop Agent CLI 	AND 	Clear Result Directory
