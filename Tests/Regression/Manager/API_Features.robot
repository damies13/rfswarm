*** Settings ***
Test Tags 	CommandLine 	Features 	API

Resource 	resources/CommandLine_Manager.resource
Resource 	resources/API_Manager.resource
Resource 	../../Common/Database.resource

Variables 	resources${/}API_expected_responses.yaml

Suite Setup 	Common.Basic Suite Initialization Manager


*** Test Cases ***
Check Connection To Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${resp_get}= 	Send GET Request To the Manager 	url=/
	&{get_result}= 	Convert To Dictionary 	${resp_get.json()}
	Log 	GET / call restult:${\n} ${get_result} 	console=True

	GROUP  Check AgentStatus response body
		Should Be Equal As Strings 		${get_result}[POST][AgentStatus][URI] 	${GET}[AgentStatus][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][AgentStatus][Body] 	${GET}[AgentStatus][Body]
	END
	GROUP  Check Jobs response body
		Should Be Equal As Strings 		${get_result}[POST][Jobs][URI] 			${GET}[Jobs][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Jobs][Body] 		${GET}[Jobs][Body]
	END
	GROUP  Check Scripts response body
		Should Be Equal As Strings 		${get_result}[POST][Scripts][URI] 		${GET}[Scripts][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Scripts][Body] 		${GET}[Scripts][Body]
	END
	GROUP  Check File response body
		Should Be Equal As Strings 		${get_result}[POST][File][URI] 			${GET}[File][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][File][Body] 		${GET}[File][Body]
	END
	GROUP  Check Result response body
		Should Be Equal As Strings 		${get_result}[POST][Result][URI] 		${GET}[Result][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Result][Body] 		${GET}[Result][Body]
	END
	GROUP  Check Metric response body
		Should Be Equal As Strings 		${get_result}[POST][Metric][URI] 		${GET}[Metric][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Metric][Body] 		${GET}[Metric][Body]
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Getting an Invalid Path From Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	GROUP  Send request with invalid url: (/GET) instead of: (/)
		VAR 	${expected_result} 		Unrecognised request: 'ParseResult(scheme='', netloc='', path='/GET', params='', query='', fragment='')'
		${resp_get}= 	Send GET Request To the Manager 	url=/GET  expected_status=404  expected_result=${expected_result}
		Log 	GET / call restult:${\n} ${resp_get.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Update Agent Status in Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${resp_post}  ${request_body}= 	Update Agent Status 	agent_name=${POST_AgentStatus}[Body][AgentName]
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /AgentStatus call restult:${\n} ${resp_result} 	console=True
	Sleep 	2s

	GROUP  Check response body
		Check ${resp_result} Contains Agents Name 	${POST_AgentStatus}[Body][AgentName]
		Check ${resp_result} Has Status Updated
	END

	Sleep 	1s
	${prerun_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*PreRun*
	GROUP  Check Agent IPAddresses are in Manager PreRun database
		VAR 	${query} 	SELECT PrimaryMetric, MetricType, SecondaryMetric, MetricValue FROM MetricData WHERE SecondaryMetric = 'IPAddress'
		@{query_result}= 	Query Result DB 	${prerun_DB} 	${query}
		Log 	${query_result}
		Length Should Be 	${query_result} 	2
		VAR 	@{expected_row_0} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress
		VAR 	@{expected_row_1} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress
		VAR 	@{expected_ips} 	${request_body}[AgentIPs][0]  ${request_body}[AgentIPs][1]

		List Should Contain Sub List 	${query_result}[0] 	${expected_row_0}[:-1]
		...    msg=The saved row in the PreRun database after POST request is invalid.
		List Should Contain Value 	${expected_ips} 	${query_result}[0][-1] 	
		...    msg=The saved row in the PreRun database after POST request is invalid. (wrong ip)

		List Should Contain Sub List 	${query_result}[1] 	${expected_row_1}[:-1]
		...    msg=The saved row in the PreRun database after POST request is invalid.
		List Should Contain Value 	${expected_ips} 	${query_result}[1][-1] 	
		...    msg=The saved row in the PreRun database after POST request is invalid. (wrong ip)
	END
	GROUP  Check Agent values are in Manager PreRun database. (AgentName, AgentStatus, AgentRobots, AgentCPU, AgentMEM, AgentNET)
		VAR 	${query} 	SELECT AgentName, AgentStatus, AgentRobots, AgentCPU, AgentMEM, AgentNET FROM AgentList
		@{query_result}= 	Query Result DB 	${prerun_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		Remove From Dictionary 	${request_body} 	AgentIPs
		@{expected_row}= 	Get Dictionary Values 	${request_body} 	sort_keys=${False}
		Convert List Items To String 	${expected_row}
		Diff Lists 	${last_row} 	${expected_row} 	message=The saved row in the PreRun database after POST request is invalid.
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Update Agent Status in Manager With Missing Field
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${ipv4} 	${ipv6}= 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]

	GROUP  Send request with missing field: Status
		VAR 	${expected_result} 		{}
		VAR 	&{request_body} 		AgentName=ERR_AGENT  AgentIPs=${Agent_IP}  Robots=${1}  CPU%=${1}  MEM%=${1}  NET%=${1}

		${resp_post}= 	Send POST Request To the Manager
		...    url=/AgentStatus 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /AgentStatus call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Update Agent Status in Manager With Invalid Field Type
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${ipv4} 	${ipv6}= 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]

	GROUP  Send request with invalid field type. CPU% in (str) type istead of (int) type.
		VAR 	${expected_result} 		'>' not supported between instances of 'int' and 'str'
		VAR 	&{request_body} 		AgentName=ERR_AGENT  Status=ERR  AgentIPs=${Agent_IP}  Robots=${1}  CPU%=11  MEM%=${1}  NET%=${1}

		${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}  expected_status=500  expected_result=${expected_result}
		Log 	POST /AgentStatus call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Update Agent Status in Manager With Wrong Field Value
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${ipv4} 	${ipv6}= 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]

	GROUP  Send request with wrong field value. CPU% value is too large.
		# BUG?
		VAR 	&{request_body} 		AgentName=ERR_AGENT  Status=ERR  AgentIPs=${Agent_IP}  Robots=${1}  CPU%=${110}  MEM%=${1}  NET%=${1}

		${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}
		Log 	POST /AgentStatus call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Jobs Assigned to the Agent by Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}  AND
	...    Set Environment Variable 	MY_OS  ${PLATFORM}

	${environ}= 	Evaluate 	dict(os.environ)  modules=os
	VAR 	&{new_env} 	MY_OS=${PLATFORM}
	Set To Dictionary 	${environ} 	&{new_env}

	Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs  envargs=${environ}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	${agent_update}= 	Get Time 	format=epoch
	Update Agent Status 	${POST_Jobs}[Body][AgentName]
	Sleep 	15s

	VAR 	${robot_1} 			1_Issue-#289.robot
	VAR 	${robot_2} 			2_Issue-#289.robot
	VAR 	${testcase_1} 		Example Test Case One One
	VAR 	${testcase_2} 		Example Test Case Two One
	VAR 	&{request_body} 	AgentName=${POST_Jobs}[Body][AgentName]

	${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Jobs call restult:${\n} ${resp_result} 	console=True

	GROUP  Check Agent values in response body. (AgentName, Abort, UploadMode)
		Should Be Equal As Integers 	${${resp_result}[EndTime] - ${resp_result}[StartTime]} 	${50 + 10}
		...    msg=StartTime and EndTime don't match scenario run + rampup time.
		Should Be True 	${resp_result}[StartTime] >= ${agent_update} 	msg=StartTime should be grater than the time that the agent was registered.
		Check ${resp_result} Contains Agents Name 	${POST_Jobs}[Body][AgentName]
		Check ${resp_result} Has Abort ${False}
		Check ${resp_result} Has UploadMode imm
	END
	GROUP  Check EnvironmentVariables values in response body
		VAR 	${envvars} 	${resp_result}[EnvironmentVariables]
		@{envvars_keys}= 	Get Dictionary Keys 	${envvars}

		Log 	%{PATH}
		VAR 	&{OS} 		vartype=value  value=%{MY_OS}
		VAR 	&{PATH} 	vartype=value  value=%{PATH}
		VAR 	&{expected_envvars} 	MY_OS=${OS}  PATH=${PATH}

		Check ${resp_result} Has Abort ${False}

		Dictionaries Should Be Equal 	${envvars}[${envvars_keys}[0]] 	${expected_envvars}[${envvars_keys}[0]]
		Dictionaries Should Be Equal 	${envvars}[${envvars_keys}[1]] 	${expected_envvars}[${envvars_keys}[1]]
	END
	GROUP  Check Schedule values in response body
		VAR 	${schedule} 	${resp_result}[Schedule]
		Log 	${schedule}
		@{schedule_keys}= 	Get Dictionary Keys 	${schedule}
		Remove Keys From Dictionary 	${schedule} 	ScriptHash  StartTime  EndTime  id

		Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[0]] 	${POST_Jobs.Body}[Schedule][${11}]
		Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[1]] 	${POST_Jobs.Body}[Schedule][${21}]
		Dictionaries Should Be Equal 	${schedule}[${schedule_keys}[2]] 	${POST_Jobs.Body}[Schedule][${22}]
	END

	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*POST_Jobs*
	GROUP  Check TestCase values is in Manager scenario database
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
	END
	GROUP  Check Robots value is in Manager scenario database
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
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Jobs Assigned by the Manager to an Agent Whose Field Is Incorrect
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Jobs}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request with wrong field: Agentname instead of AgentName
		VAR 	${expected_result} 		{}
		VAR 	&{request_body} 		Agentname=WRONG_KEY

		${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /Jobs call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Jobs Assigned to an Agent Who is Unregistered in the Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Jobs}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request with unregistered AgentName
		VAR 	&{request_body} 	AgentName=UNKNOWN
		${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /Jobs call restult:${\n} ${resp_result} 	console=True

		Length Should Be 	${resp_result}[Schedule]  ${0} 	# no jobs for unknown agent
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Scripts Information From Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Scripts}[Body][AgentName]
	Sleep 	2s

	VAR 	${1_File} 	1_Scripts_Issue-#289.robot
	VAR 	${2_File} 	2_Scripts_Issue-#289.robot
	VAR 	${3_File} 	1r_Issue-#289.resource
	VAR 	${4_File} 	resources${/}2r_Issue-#289.resource
	${1_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${1_File}
	${2_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${2_File}
	${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
	${4_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${4_File}
	VAR 	&{request_body} 	AgentName=${POST_Scripts}[Body][AgentName]

	${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Scripts call restult:${\n} ${resp_result} 	console=True

	Check ${resp_result} Contains Agents Name 	${POST_Scripts}[Body][AgentName]
	GROUP  Check Scripts response body
		Length Should Be 	${resp_result}[Scripts]  4

		VAR 	&{1_Data} 	File=${1_File}  Hash=${1_Hash}
		Should Contain 	${resp_result}[Scripts]  ${1_Data}

		VAR 	&{2_Data} 	File=${2_File}  Hash=${2_Hash}
		Should Contain 	${resp_result}[Scripts]  ${2_Data}

		VAR 	&{3_Data} 	File=${3_File}  Hash=${3_Hash}
		Should Contain 	${resp_result}[Scripts]  ${3_Data}

		VAR 	&{4_Data} 	File=${4_File}  Hash=${4_Hash}
		Should Contain 	${resp_result}[Scripts]  ${4_Data}
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Scripts Information From Manager For Unregistered Agent
	[Documentation] 	Unregistered Agent should get scripts information as part of the Manager's recovery system.
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Scripts}[Body][AgentName]
	Sleep 	2s

	VAR 	${1_File} 	1_Scripts_Issue-#289.robot
	VAR 	${2_File} 	2_Scripts_Issue-#289.robot
	VAR 	${3_File} 	1r_Issue-#289.resource
	VAR 	${4_File} 	resources${/}2r_Issue-#289.resource
	${1_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${1_File}
	${2_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${2_File}
	${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
	${4_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${4_File}

	GROUP  Send request with unregistered AgentName
		VAR 	&{request_body} 	AgentName=UNKNOWN_AGENT

		${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /Scripts call restult:${\n} ${resp_result} 	console=True

		Length Should Be 	${resp_result}[Scripts]  4

		VAR 	&{1_Data} 	File=${1_File}  Hash=${1_Hash}
		Should Contain 	${resp_result}[Scripts]  ${1_Data}

		VAR 	&{2_Data} 	File=${2_File}  Hash=${2_Hash}
		Should Contain 	${resp_result}[Scripts]  ${2_Data}

		VAR 	&{3_Data} 	File=${3_File}  Hash=${3_Hash}
		Should Contain 	${resp_result}[Scripts]  ${3_Data}

		VAR 	&{4_Data} 	File=${4_File}  Hash=${4_Hash}
		Should Contain 	${resp_result}[Scripts]  ${4_Data}
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Scripts Information From Manager With Wrong Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -a  2  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Scripts}[Body][AgentName]
	Sleep 	2s

	GROUP  Send request with wrong field: agentName instead of AgentName
		VAR 	${expected_result} 		{}
		VAR 	&{request_body} 		agentName=WRONG_KEY

		${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /Scripts call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Request File Operation With Unknown Action
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Send request with unknown Action
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
		VAR 	${expected_result} 		Not Found
		VAR 	&{request_body} 		AgentName=${POST_File}[Body_Download][AgentName]  Action=UNKNOWN  Hash=${3_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_body}
		...    expected_status=404  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Download a File From Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 		${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	VAR 	${1_File} 	1_Issue-#289.robot
	${1_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${1_File}
	VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download  Hash=${1_Hash}

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}
	&{resp_result_download}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call download restult:${\n} ${resp_result_download} 	console=True

	Sleep 	5s
	GROUP  Check response body
		Length Should Be 	${resp_result_download}  4
		Check ${resp_result_download} Contains Agents Name 	${POST_File}[Body_Download][AgentName]
		Check ${resp_result_download} Has File ${1_File}
		Check ${resp_result_download} Has Hash ${1_Hash}
		IF  '${PLATFORM}' == 'windows'
			Check ${resp_result_download} Has FileData ${POST_File}[Body_Download][FileData_W]
		ELSE
			Check ${resp_result_download} Has FileData ${POST_File}[Body_Download][FileData_U_M]
		END
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Download a File From Manager From Unregistered Agent
	[Documentation] 	Unregistered Agent should be able to download files as part of the Manager's recovery system.
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Send request with unregistered Agent
		VAR 	${1_File} 	1_Issue-#289.robot
		${1_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${1_File}
		VAR 	&{request_Download} 	AgentName=UNKNOWN_AGENT  Action=Download  Hash=${1_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		&{resp_result_download}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call download restult:${\n} ${resp_result_download} 	console=True

		Length Should Be 	${resp_result_download}  4
		Check ${resp_result_download} Contains Agents Name 	UNKNOWN_AGENT
		Check ${resp_result_download} Has File ${1_File}
		Check ${resp_result_download} Has Hash ${1_Hash}
		IF  '${PLATFORM}' == 'windows'
			Check ${resp_result_download} Has FileData ${POST_File}[Body_Download][FileData_W]
		ELSE
			Check ${resp_result_download} Has FileData ${POST_File}[Body_Download][FileData_U_M]
		END
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Download a File From Manager With Missing Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Send request with missing field: Hash
		VAR 	${expected_result} 		{}
		VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download

		${resp_post}= 	Send POST Request To the Manager
		...    url=/File  request=${request_Download}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Download a File From Manager With Unknown Hash
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Send request with unknown Hash
		VAR 	${expected_result} 		Not Found
		VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download  Hash=34d193a7d30904abec4307dee7df89fa

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}  expected_status=404  expected_result=${expected_result}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get Available File Status From Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Status_1][AgentName]
	Sleep 	15s

	VAR 	${2_File} 	2_Issue-#289.robot
	${2_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${2_File}
	VAR 	&{request_Status_1} 	AgentName=${POST_File}[Body_Status_1][AgentName]  Action=Status  Hash=${2_Hash}

	${resp_post_1}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_1}
	&{resp_result_status_1}= 	Convert To Dictionary 	${resp_post_1.json()}
	Log 	POST /File call status restult:${\n} ${resp_result_status_1} 	console=True

	GROUP  Check response body from call with available file
		Length Should Be 	${resp_result_status_1}  3
		Check ${resp_result_status_1} Contains Agents Name 	${POST_File}[Body_Status_1][AgentName]
		Check ${resp_result_status_1} Has Exists True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get File Status With Unknown Hash From Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Status_1][AgentName]
	Sleep 	15s

	VAR 	${1_File} 				???.robot
	VAR 	${unknown_Hash} 		b87a12d0e3567a80d6316732c7c3213b
	VAR 	&{request_Status_2} 	AgentName=${POST_File}[Body_Status_2][AgentName]  Action=Status  Hash=${unknown_Hash}

	${resp_post_2}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_2}
	&{resp_result_status_2}= 	Convert To Dictionary 	${resp_post_2.json()}
	Log 	POST /File call status restult:${\n} ${resp_result_status_2} 	console=True

	GROUP  Check response body from call with unknown hash
		Length Should Be 	${resp_result_status_2}  3
		Check ${resp_result_status_2} Contains Agents Name 	${POST_File}[Body_Status_2][AgentName]
		Check ${resp_result_status_2} Has Exists False
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get File Status From Manager From Unregistered Agent
	[Documentation] 	Unregistered Agent should be able to get files status as part of the Manager's recovery system.
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Status][AgentName]
	Sleep 	15s

	GROUP  Send request with unregistered AgentName
		VAR 	${1_File} 	1_Issue-#289.robot
		${1_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${1_File}
		VAR 	&{request_Status} 	AgentName=UNKNOWN_AGENT  Action=Status  Hash=${1_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True

		Length Should Be 	${resp_result}  3
		Check ${resp_result} Contains Agents Name 	UNKNOWN_AGENT
		Check ${resp_result} Has Exists True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Get File Status From Manager With Missing Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Status][AgentName]
	Sleep 	15s

	GROUP  Send request with missing field: Hash
		VAR 	${expected_result} 		{}
		VAR 	&{request_Status} 		AgentName=${POST_File}[Body_Status][AgentName]  Action=Status

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Status}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Upload a File to the Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}
	
	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	VAR 	${3_File} 	resources${/}3_Issue-#289.robot
	${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
	VAR 	&{request_Upload} 		 AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=${3_Hash}
	...    File=${3_File}  FileData=${POST_File}[Upload_FileData]

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
	&{resp_result_upload}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call upload restult:${\n} ${resp_result_upload} 	console=True

	GROUP  Check response body
		Length Should Be 	${resp_result_upload}  3
		Check ${resp_result_upload} Contains Agents Name 	${POST_File}[Body_Upload][AgentName]
		Check ${resp_result_upload} Has Result Saved
	END
	GROUP  Check if a file has been downloaded by Manager in scenario logs
		Sleep 	3
		${scenario_dir}= 	List Directories In Directory 	${RESULTS_DIR}  pattern=*POST_File*
		File Should Exist 	${RESULTS_DIR}${/}${scenario_dir}[0]${/}logs${/}resources${/}3_Issue-#289.robot
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Upload a File to the Manager From Unregistered Agent
	[Documentation]
	...    Unregistered Agent should be able to get files status as part of the Manager's recovery system.
	...    When Manager closes unexpectedly, Agent continous sending files to the Manager after restarting it.
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	GROUP  Send request with unregistered Agent
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
		VAR 	&{request_Upload} 	AgentName=UNKNOWN_AGENT  Action=Upload  Hash=${3_Hash}
		...    File=resources/3_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
		&{resp_result_upload}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result_upload} 	console=True

		Length Should Be 	${resp_result_upload}  3
		Check ${resp_result_upload} Contains Agents Name 	UNKNOWN_AGENT
		Check ${resp_result_upload} Has Result Saved
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Upload a File to the Manager With Missing Hash Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	GROUP  Send request with missing field: Hash
		VAR 	${expected_result} 		{}
		VAR 	&{request_Upload} 	AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload
		...    File=resources/3_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Upload}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Upload a File to the Manager With Missing FileData Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${scenario_dir}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	GROUP  Sending request with missing field: FileData
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${scenario_dir}  ${basefolder}${/}${3_File}
		VAR 	${expected_result} 		Internal Server Error
		VAR 	&{request_Upload} 	AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=${3_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Upload}  expected_status=500  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Result Data to the Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Documentation] 	Emulating listener who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
	...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=1  Iteration=5  Sequence=2

	${resp_post}= 	Send POST Request To the Manager 	url=/Result 	request=${request}
	&{resp_result_1}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Result call upload restult:${\n} ${resp_result_1} 	console=True

	GROUP  Check respone body
		Length Should Be 	${resp_result_1}  2
		Check ${resp_result_1} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_1} Has Result Queued
	END

	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*POST_Result*
	GROUP  Check Result request data in Manager database. (AgentName, ResultName, Result, ElapsedTime, StartTime, EndTime, ScriptIndex, Robot, Iteration, Sequence)
		VAR 	${query} 	SELECT agent, result_name, result, elapsed_time, start_time, end_time, script_index, robot, iteration, sequence FROM Results
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		${last_row}= 	Convert To List 	${last_row}
		Convert List Items To String 		${last_row}
		${expected_row} 	Get Dictionary Values 	${request} 	sort_keys=${False}
		Diff Lists 	${last_row} 	${expected_row} 	message=The saved row in the Scenario database after POST request is invalid.

	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Result Data to the Manager With Wrong ScriptIndex Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Documentation]
	...    Emulating listener who make this call to the manager.
	...
	...    This is the part of the Manager's recovery system.
	...    If the Manager crashes the Agent could send the missing result data to the Manager PreRun DB 
	...    (we can recover stuff from PreRun DB into result db and then generate result from it)
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request with invalid ScriptIndex that is not configured in the scenario file
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=5  Robot=1  Iteration=5  Sequence=2

		${resp_post_2}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_2}= 	Convert To Dictionary 	${resp_post_2.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_2} 	console=True

		Length Should Be 	${resp_result_2}  2
		Check ${resp_result_2} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_2} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Result Data to the Manager With Missing Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request with missing field: ElapsedTime
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=1  Iteration=5  Sequence=2

		${resp_post_1}= 	Send POST Request To the Manager 	url=/Result  request=${request}  expected_status=422  expected_result={}
		&{resp_result_1}= 	Convert To Dictionary 	${resp_post_1.json()}
		Log 	POST /Result call 2 upload restult:${\n} ${resp_result_1} 	console=True

		Length Should Be 	${resp_result_1}  0
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Result Data to the Manager From Unregistered Agent
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Documentation]
	...    Unregistered Agent should be able to send results data to the Manager
	...    as part of the Manager's recovery system.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request from unregistered Agent
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=2  Robot=1  Iteration=5  Sequence=2

		${resp_post_3}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_3}= 	Convert To Dictionary 	${resp_post_3.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_3} 	console=True

		Length Should Be 	${resp_result_3}  2
		Check ${resp_result_3} Contains Agents Name 	UNKNOWN_AGENT
		Check ${resp_result_3} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Result Data to the Manager With Wrong Field Value in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	GROUP  Send request with wrong field value: Negative Robot count
		# PROBABLY A BUG BUT NOT THAT IMPORTANT
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=-1  Iteration=5  Sequence=2

		${resp_post_4}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_4}= 	Convert To Dictionary 	${resp_post_4.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_4} 	console=True

		Length Should Be 	${resp_result_4}  2
		Check ${resp_result_4} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_4} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Metric Data to the Manager
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Positive-Test
	[Documentation] 	Emulating the agent and monitoring scritps who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	VAR 	&{SecondaryMetrics} 	vmstat: Mach Virtual Memory Statistics=(page size of 4096 bytes)  vmstat: Pages free=5091.
	VAR 	&{request} 	AgentName=${POST_Metric}[AgentName]  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
	...    SecondaryMetrics=&{SecondaryMetrics}

	${resp_post}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Metric call upload restult:${\n} ${resp_result} 	console=True

	GROUP  Check response body
		Length Should Be 	${resp_result}  2
		Check ${resp_result} Has Metric ${POST_Metric}[Body][Metric]
		Check ${resp_result} Has Result Queued
	END

	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*PreRun*
	GROUP  Check PrimaryMetric(Name), MetricType(Type) in Manager database
		VAR 	${query} 	SELECT Name, Type FROM Metric WHERE Name='${request}[PrimaryMetric]'
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		${last_row}= 	Convert To List 	${last_row}
		Convert List Items To String 		${last_row}
		Should Be Equal As Strings 	${last_row}[0] 	${request}[PrimaryMetric]
		Should Be Equal As Strings 	${last_row}[1] 	${request}[MetricType]
	END
	GROUP  Check If AgentName is saved as DataSource in Manager database
		VAR 	${query} 	SELECT Name, Type FROM Metric WHERE Name='${POST_Metric}[AgentName]'
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		${last_row}= 	Convert To List 	${last_row}
		Convert List Items To String 		${last_row}
		Should Be Equal As Strings 	${last_row}[0] 	${POST_Metric}[AgentName]
		Should Be Equal As Strings 	${last_row}[1] 	DataSource

	END
	GROUP  Check MetricTime and SecondaryMetrics in Manager database
		VAR 	${setup_query} 	SELECT ID FROM Metric WHERE Name='${request}[PrimaryMetric]'
		@{setup_query_result}= 	Query Result DB 	${result_DB} 	${setup_query}
		VAR 	${ParentID} 	${setup_query_result}[-1][0]
		VAR 	${setup_query} 	SELECT ID FROM Metric WHERE Name='${POST_Metric}[AgentName]'
		@{setup_query_result}= 	Query Result DB 	${result_DB} 	${setup_query}
		VAR 	${DataSource} 	${setup_query_result}[-1][0]

		@{keys}= 	Get Dictionary Keys 	${SecondaryMetrics}  sort_keys=${False}
		@{values}= 	Get Dictionary Values 	${SecondaryMetrics}  sort_keys=${False}
		VAR 	${query} 	SELECT ParentID, Time, Key, Value, DataSource FROM Metrics WHERE ParentID='${ParentID}'
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}

		VAR 	${first_row} 	${query_result}[0]
		${first_row}= 	Convert To List 	${first_row}
		VAR 	@{expected_first_row} 	${ParentID}  ${request}[MetricTime]  ${keys}[0]  ${values}[0]  ${DataSource}
		Convert List Items To String 		${first_row}
		Convert List Items To String 		${expected_first_row}
		Diff Lists 	${first_row}  ${expected_first_row}  message=The saved row in the PreRun database after POST request is invalid.

		VAR 	${second_row} 	${query_result}[1]
		${second_row}= 	Convert To List 	${second_row}
		VAR 	@{expected_second_row} 	${ParentID}  ${request}[MetricTime]  ${keys}[1]  ${values}[1]  ${DataSource}
		Convert List Items To String 		${second_row}
		Convert List Items To String 		${expected_second_row}
		Diff Lists 	${second_row}  ${expected_second_row}  message=The saved row in the PreRun database after POST request is invalid.

	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Metric Data to the Manager From Unregistered Agent
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Documentation]
	...    Unregistered Agent should be able to send metric data to the Manager
	...    as part of the Manager's recovery system.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	GROUP  Send request from unregistered Agent
		VAR 	&{SecondaryMetrics} 	vmstat: Mach Virtual Memory Statistics=(page size of 4096 bytes)  vmstat: Pages free=5091.
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
		...    SecondaryMetrics=&{SecondaryMetrics}

		${resp_post_2}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
		&{resp_result_2}= 	Convert To Dictionary 	${resp_post_2.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_2} 	console=True

		Length Should Be 	${resp_result_2}  2
		Check ${resp_result_2} Has Metric my_test_server
		Check ${resp_result_2} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Metric Data to the Manager With Missing Field in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	GROUP  Send request with missing field: SecondaryMetrics
		VAR 	&{request} 	AgentName=${POST_Metric}[AgentName]  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970

		${resp_post_1}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}  expected_status=422  expected_result={}
		&{resp_result_1}= 	Convert To Dictionary 	${resp_post_1.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_1} 	console=True

		Length Should Be 	${resp_result_1}  0
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Send Metric Data to the Manager With Wrong Value Type in Request
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure  Negative-Test
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	7s
	${stdout}  ${stderr}= 	Find Log 	Manager
	Wait Until the File Is Not Empty 	${stdout} 	timeout=15

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	GROUP  Send request with invalid value format: SecondaryMetrics in (list) type not (dict)
		VAR 	@{SecondaryMetrics} 	Mach Virtual Memory Statistics=(page size of 4096 bytes)  Pages free=5091.
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
		...    SecondaryMetrics=@{SecondaryMetrics}

		${resp_post_3}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
		&{resp_result_3}= 	Convert To Dictionary 	${resp_post_3.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_3} 	console=True

		Length Should Be 	${resp_result_3}  2
		Check ${resp_result_3} Has Metric my_test_server
		Check ${resp_result_3} Has Result Queued

	END
	GROUP  Check the Manager's output for the TypeError exception
		Sleep 	5s
		${stdout}  ${stderr} = 		Find Log 	Manager
		${stderr_content}= 			Read Log 	${stderr}
		Should Contain 	${stderr_content} 		TypeError 	Missing TypeError Excaption in Manager's stderr file.
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory
