*** Settings ***
Test Tags 	CommandLine 	Features 	API

Resource 	resources/CommandLine_Manager.resource
Resource 	resources/API_Manager.resource
Resource 	../../Common/Database.resource

Variables 	resources${/}API_expected_responses.yaml

Suite Setup 	Common.Basic Suite Initialization Manager

*** Test Cases ***
Valid Request: GET /
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	1s

	${resp_get}= 	Send GET Request To the Manager 	url=/
	&{get_result}= 	Convert To Dictionary 	${resp_get.json()}
	Log 	GET / call restult:${\n} ${get_result} 	console=True

	GROUP  Checking AgentStatus response body
		Should Be Equal As Strings 		${get_result}[POST][AgentStatus][URI] 	${GET}[AgentStatus][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][AgentStatus][Body] 	${GET}[AgentStatus][Body]
	END
	GROUP  Checking Jobs response body
		Should Be Equal As Strings 		${get_result}[POST][Jobs][URI] 			${GET}[Jobs][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Jobs][Body] 		${GET}[Jobs][Body]
	END
	GROUP  Checking Scripts response body
		Should Be Equal As Strings 		${get_result}[POST][Scripts][URI] 		${GET}[Scripts][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Scripts][Body] 		${GET}[Scripts][Body]
	END
	GROUP  Checking File response body
		Should Be Equal As Strings 		${get_result}[POST][File][URI] 			${GET}[File][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][File][Body] 		${GET}[File][Body]
	END
	GROUP  Checking Result response body
		Should Be Equal As Strings 		${get_result}[POST][Result][URI] 		${GET}[Result][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Result][Body] 		${GET}[Result][Body]
	END
	GROUP  Checking Metric response body
		Should Be Equal As Strings 		${get_result}[POST][Metric][URI] 		${GET}[Metric][URI]
		Dictionaries Should Be Equal 	${get_result}[POST][Metric][Body] 		${GET}[Metric][Body]
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: GET /
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	1s

	GROUP  Sending request with invalid url (/GET) not (/)
		VAR 	${expected_result} 		Unrecognised request: 'ParseResult(scheme='', netloc='', path='/GET', params='', query='', fragment='')'
		${resp_get}= 	Send GET Request To the Manager 	url=/GET  expected_status=404  expected_result=${expected_result}
		Log 	GET / call restult:${\n} ${resp_get.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /AgentStatus
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	1s

	${resp_post}  ${request_body}= 	Update Agent Status 	agent_name=${POST_AgentStatus}[Body][AgentName]
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /AgentStatus call restult:${\n} ${resp_result} 	console=True
	Sleep 	2s

	GROUP  Checking response body
		Check ${resp_result} Contains Agents Name 	${POST_AgentStatus}[Body][AgentName]
		Check ${resp_result} Has Status Updated
	END

	Sleep 	1s
	${prerun_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*PreRun*
	GROUP  Checking IPAddress in database
		VAR 	${query} 	SELECT PrimaryMetric, MetricType, SecondaryMetric, MetricValue FROM MetricData WHERE SecondaryMetric = 'IPAddress'
		@{query_result}= 	Query Result DB 	${prerun_DB} 	${query}
		Log 	${query_result}
		Length Should Be 	${query_result} 	2
		VAR 	@{expected_row_0} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress
		VAR 	@{expected_row_1} 	${POST_AgentStatus}[Body][AgentName]  Agent  IPAddress
		VAR 	@{expected_ips} 	${request_body}[AgentIPs][0]  ${request_body}[AgentIPs][1]

		List Should Contain Sub List 	${query_result}[0] 	${expected_row_0}[:-1] 	msg=The saved row in the PreRun database after POST request is invalid.
		List Should Contain Value 	${expected_ips} 	${query_result}[0][-1] 	
		...    msg=The saved row in the PreRun database after POST request is invalid. (wrong ip)
		List Should Contain Sub List 	${query_result}[1] 	${expected_row_0}[:-1] 	msg=The saved row in the PreRun database after POST request is invalid.
		List Should Contain Value 	${expected_ips} 	${query_result}[1][-1] 	
		...    msg=The saved row in the PreRun database after POST request is invalid. (wrong ip)
	END
	GROUP  Checking AgentName, AgentStatus, AgentRobots, AgentCPU, AgentMEM, AgentNET in database
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

Invalid Request: POST /AgentStatus
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	1s

	${ipv4} 	${ipv6}= 	Get Ip Addresses
	VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]

	GROUP  Sending request with missing Status data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_body} 		AgentName=ERR_AGENT  AgentIPs=${Agent_IP}  Robots=${1}  CPU%=${1}  MEM%=${1}  NET%=${1}

		${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /AgentStatus call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with invalid CPU% type (str) not (int)
		VAR 	${expected_result} 		'>' not supported between instances of 'int' and 'str'
		VAR 	&{request_body} 		AgentName=ERR_AGENT  Status=ERR  AgentIPs=${Agent_IP}  Robots=${1}  CPU%=11  MEM%=${1}  NET%=${1}

		${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}  expected_status=500  expected_result=${expected_result}
		Log 	POST /AgentStatus call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /Jobs
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	# ${environ}= 	Evaluate 	dict(os.environ)  modules=os
	# VAR 	&{new_env} 	FIRST=Pierwszy
	# Set To Dictionary 	${environ} 	&{new_env}

	Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs  #envargs=${environ}

	Sleep 	5s

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

	GROUP  Checking AgentName, Abort, UploadMode response body
		Should Be Equal As Integers 	${${resp_result}[EndTime] - ${resp_result}[StartTime]} 	${50 + 10}
		...    msg=StartTime and EndTime don't match scenario run + rampup time.
		Should Be True 	${resp_result}[StartTime] >= ${agent_update} 	msg=StartTime should be grater than the time that the agent was registered.
		# scenario as yaml file and use that in Tests as variable file?
		# test if we change file the scripthash changes?
		Check ${resp_result} Contains Agents Name 	${POST_Jobs}[Body][AgentName]
		Check ${resp_result} Has Abort ${False}
		Check ${resp_result} Has UploadMode imm
	END
	GROUP  Checking EnvironmentVariables response body
		VAR 	${envvars} 	${resp_result}[EnvironmentVariables]
		@{envvars_keys}= 	Get Dictionary Keys 	${envvars}

		Log 	%{PATH}
		VAR 	&{OS} 		vartype=value  value=%{OS}
		VAR 	&{TEMP} 	vartype=path  value=Temp
		VAR 	&{PATH} 	vartype=value  value=%{PATH}
		VAR 	&{expected_envvars} 	OS=${OS}  TEMP=${TEMP}  PATH=${PATH}

		Check ${resp_result} Has Abort ${False}

		Dictionaries Should Be Equal 	${envvars}[${envvars_keys}[0]] 	${expected_envvars}[${envvars_keys}[0]]
		Dictionaries Should Be Equal 	${envvars}[${envvars_keys}[1]] 	${expected_envvars}[${envvars_keys}[1]]
		Dictionaries Should Be Equal 	${envvars}[${envvars_keys}[2]] 	${expected_envvars}[${envvars_keys}[2]]

	END
	GROUP  Checking Schedule response body
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
	GROUP  Checking TestCase name in database
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
	GROUP  Checking Robots in database
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

Invalid Request: POST /Jobs
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -a  1  -r  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Jobs_Issue-#289.rfs

	Sleep 	5s

	Update Agent Status 	${POST_Jobs}[Body][AgentName]
	Sleep 	15s

	GROUP  Sending request with wrong key data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_body} 		Agentname=WRONG_KEY

		${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /Jobs call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	&{request_body} 	AgentName=UNKNOWN
		${resp_post}= 	Send POST Request To the Manager 	url=/Jobs 	request=${request_body}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /Jobs call restult:${\n} ${resp_result} 	console=True

		Length Should Be 	${resp_result}[Schedule]  ${0} 	# no jobs for unknown agent
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /Scripts
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_Scripts}[Body][AgentName]
	Sleep 	2s

	VAR 	${1_File} 	1_Scripts_Issue-#289.robot
	VAR 	${2_File} 	2_Scripts_Issue-#289.robot
	VAR 	${3_File} 	1r_Issue-#289.resource
	VAR 	${4_File} 	resources${/}2r_Issue-#289.resource
	${1_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${1_File}
	${2_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${2_File}
	${3_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${3_File}
	${4_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${4_File}
	VAR 	&{request_body} 	AgentName=${POST_Scripts}[Body][AgentName]

	${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Scripts call restult:${\n} ${resp_result} 	console=True

	Check ${resp_result} Contains Agents Name 	${POST_Scripts}[Body][AgentName]
	GROUP  Checking Scripts response body
		Length Should Be 	${resp_result}[Scripts]  4

		Check ${resp_result}[Scripts][0] Has File ${1_File}
		Check ${resp_result}[Scripts][0] Has Hash ${1_Hash}

		Check ${resp_result}[Scripts][1] Has File ${2_File}
		Check ${resp_result}[Scripts][1] Has Hash ${2_Hash}

		Check ${resp_result}[Scripts][2] Has File ${3_File}
		Check ${resp_result}[Scripts][2] Has Hash ${3_Hash}

		Check ${resp_result}[Scripts][3] Has File ${4_File}
		Check ${resp_result}[Scripts][3] Has Hash ${4_Hash}

		# Dictionaries Should Be Equal 	${resp_result}[Scripts][0] 	${POST_Scripts}[Body][Scripts][0]
		# Dictionaries Should Be Equal 	${resp_result}[Scripts][1] 	${POST_Scripts}[Body][Scripts][1]
		# Dictionaries Should Be Equal 	${resp_result}[Scripts][2] 	${POST_Scripts}[Body][Scripts][2]
		# Dictionaries Should Be Equal 	${resp_result}[Scripts][3] 	${POST_Scripts}[Body][Scripts][3]
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: POST /Scripts
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -a  2  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Scripts_Issue-#289.rfs

	Sleep 	5s

	Update Agent Status 	${POST_Scripts}[Body][AgentName]
	Sleep 	2s

	GROUP  Sending request with wrong key data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_body} 		Agentname=WRONG_KEY

		${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}  expected_status=422  expected_result=${expected_result}
		Log 	POST /Scripts call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	&{request_body} 	AgentName=UNKNOWN_AGENT

		${resp_post}= 	Send POST Request To the Manager 	url=/Scripts 	request=${request_body}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /Scripts call restult:${\n} ${resp_result} 	console=True

		# scripts for unregistered agent?
		# Length Should Be 	${resp_result}[Schedule]  ${0} 	# no jobs for unknown agent
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /File Download
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	VAR 	${1_File} 	1_Issue-#289.robot
	${1_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${1_File}
	VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download  Hash=${1_Hash}

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}
	&{resp_result_download}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call download restult:${\n} ${resp_result_download} 	console=True

	Sleep 	5s
	GROUP  Checking response body
		Length Should Be 	${resp_result_download}  4
		Check ${resp_result_download} Contains Agents Name 	${POST_File}[Body_Download][AgentName]
		Check ${resp_result_download} Has File ${POST_File}[Body_Download][File]
		Check ${resp_result_download} Has FileData ${POST_File}[Body_Download][FileData]
	END
	# GROUP  Checking if files has been downloaded
	# 	Sleep 	3s
	# 	File Should Exist 	${AGENT_DIR}${/}scripts${/}1_Issue-#289.robot
	# END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: POST /File Unknown Action
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Sending request with unknown Action
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${3_File}
		VAR 	${expected_result} 		Not Found
		VAR 	&{request_body} 		AgentName=${POST_File}[Body_Download][AgentName]  Action=UNKNOWN  Hash=${3_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_body}  expected_status=404  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: POST /File Download
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Download][AgentName]
	Sleep 	15s

	GROUP  Sending request with missing Hash data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Download}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	${1_File} 	1_Issue-#289.robot
		${1_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${1_File}
		VAR 	&{request_Download} 	AgentName=UNKNOWN_AGENT  Action=Download  Hash=${1_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True

		# files for unregistered agent?
		# Length Should Be 	${resp_result}[Schedule]  ${0}
		# File Should Not Exist 	${AGENT_DIR}${/}scripts${/}1_Issue-#289.robot
	END
	GROUP  Sending request with unknown Hash
		VAR 	${expected_result} 		Not Found
		VAR 	&{request_Download} 	AgentName=${POST_File}[Body_Download][AgentName]  Action=Download  Hash=34d193a7d30904abec4307dee7df89fa

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Download}  expected_status=404  expected_result=${expected_result}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /File Status
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Status_1][AgentName]
	Sleep 	15s

	GROUP  Checking response body from call with available file
		VAR 	${2_File} 	2_Issue-#289.robot
		${2_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${2_File}
		VAR 	&{request_Status_1} 	AgentName=${POST_File}[Body_Status_1][AgentName]  Action=Status  Hash=${2_Hash}

		${resp_post_1}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_1}
		&{resp_result_status_1}= 	Convert To Dictionary 	${resp_post_1.json()}
		Log 	POST /File call status restult:${\n} ${resp_result_status_1} 	console=True

		Length Should Be 	${resp_result_status_1}  3
		Check ${resp_result_status_1} Contains Agents Name 	${POST_File}[Body_Status_1][AgentName]
		Check ${resp_result_status_1} Has Exists ${POST_File}[Body_Status_1][Exists]
	END
	GROUP  Checking response body from call with missing file but known hash
		VAR 	${1_File} 	1_Issue-#289.robot
		VAR 	${1_Hash} 	b87a12d0e3567a80d6316732c7c3213b
		VAR 	&{request_Status_2} 	AgentName=${POST_File}[Body_Status_2][AgentName]  Action=Status  Hash=${1_Hash}

		${resp_post_2}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status_2}
		&{resp_result_status_2}= 	Convert To Dictionary 	${resp_post_2.json()}
		Log 	POST /File call status restult:${\n} ${resp_result_status_2} 	console=True

		Length Should Be 	${resp_result_status_2}  3
		Check ${resp_result_status_2} Contains Agents Name 	${POST_File}[Body_Status_2][AgentName]
		Check ${resp_result_status_2} Has Exists ${POST_File}[Body_Status_2][Exists]
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: POST /File Status
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Status][AgentName]
	Sleep 	15s

	GROUP  Sending request with missing Hash data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_Status} 	AgentName=${POST_File}[Body_Status][AgentName]  Action=Status

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Status}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	${1_File} 	1_Issue-#289.robot
		${1_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${1_File}
		VAR 	&{request_Status} 	AgentName=UNKNOWN_AGENT  Action=Status  Hash=${1_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True

		# files info for unregistered agent?
		# Length Should Be 	${resp_result}[Schedule]  ${0}
		# File Not Should Exist 	${AGENT_DIR}${/}scripts${/}1_Issue-#289.robot
	END
	GROUP  Sending request with unknown Hash
		VAR 	${unknown_hash} 	34d193a7d30904abec4307dee7df89fa
		VAR 	&{request_Status} 	AgentName=${POST_File}[Body_Status][AgentName]  Action=Status  Hash=${unknown_hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Status}
		&{resp_result_status}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call status restult:${\n} ${resp_result_status} 	console=True

		Check ${resp_result_status} Has Exists ${POST_File}[Body_Status][Exists]
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /File Upload
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}
	
	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	VAR 	${3_File} 	resources${/}3_Issue-#289.robot
	${3_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${3_File}
	VAR 	&{request_Upload} 		 AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=${3_Hash}
	...    File=${3_File}  FileData=${POST_File}[Upload_FileData]

	${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
	&{resp_result_upload}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /File call upload restult:${\n} ${resp_result_upload} 	console=True

	GROUP  Checking response body
		Length Should Be 	${resp_result_upload}  3
		Check ${resp_result_upload} Contains Agents Name 	${POST_File}[Body_Upload][AgentName]
		Check ${resp_result_upload} Has Result ${POST_File}[Body_Upload][Result]
	END
	GROUP  Checking if a file has been downloaded by Manager
		Sleep 	3
		${scenario_dir}= 	List Directories In Directory 	${RESULTS_DIR}  pattern=*POST_File*
		File Should Exist 	${RESULTS_DIR}${/}${scenario_dir}[0]${/}logs${/}resources${/}3_Issue-#289.robot
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Invalid Request: POST /File Upload
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR}

	VAR 	${basefolder} 	${CURDIR}${/}testdata${/}Issue-#289
	VAR 	${script_dir} 	${CURDIR}${/}testdata${/}Issue-#289${/}POST_File_Issue-#289.rfs
	Run Manager CLI  -n  -a  1  -d  ${RESULTS_DIR}  -s  ${script_dir}

	Sleep 	5s

	Update Agent Status 	${POST_File}[Body_Upload][AgentName]
	Sleep 	15s

	GROUP  Sending request with missing Hash data
		VAR 	${expected_result} 		Unprocessable Entity
		VAR 	&{request_Upload} 	AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload
		...    File=resources/3_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Upload}  expected_status=422  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with missing File data
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${3_File}
		VAR 	${expected_result} 		Internal Server Error
		VAR 	&{request_Upload} 	AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=${3_Hash}

		${resp_post}= 	Send POST Request To the Manager 	url=/File  request=${request_Upload}  expected_status=500  expected_result=${expected_result}
		Log 	POST /File call restult:${\n} ${resp_post.text} 	console=True
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	${3_File} 	resources${/}3_Issue-#289.robot
		${3_Hash}= 	Hash File 	${script_dir}  ${basefolder}${/}${3_File}
		VAR 	&{request_Upload} 	AgentName=UNKNOWN_AGENT  Action=Upload  Hash=${3_Hash}
		...    File=resources/3_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call restult:${\n} ${resp_result} 	console=True

		# files send from unregistered agent and saved?
		# Length Should Be 	${resp_result}[Schedule]  ${0}
		# File Not Should Exist 	${AGENT_DIR}${/}scripts${/}1_Issue-#289.robot
	END
	GROUP  Sending request with invalid file name (invalid path should have been handled)
		VAR 	&{request_Upload} 	AgentName=${POST_File}[Body_Upload][AgentName]  Action=Upload  Hash=34d000a7d30904abec4307dee7df89fa
		...    File=resources/:?$%^UNKNOWN_Issue-#289.robot  FileData=${POST_File}[Upload_FileData]

		${resp_post}= 	Send POST Request To the Manager 	url=/File 	request=${request_Upload}
		&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
		&{resp_result_upload}= 	Convert To Dictionary 	${resp_post.json()}
		Log 	POST /File call Upload restult:${\n} ${resp_result_upload} 	console=True

		Check ${resp_result_upload} Has Result Saved

		Sleep 	3s
		${scenario_dir}= 	List Directories In Directory 	${RESULTS_DIR}  pattern=*POST_File*
		File Should Exist 	${RESULTS_DIR}${/}${scenario_dir}[0]${/}logs${/}resources${/}3_Issue-#289.robot
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /Result
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Documentation] 	Emulating listener who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	5s

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
	...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=1  Iteration=5  Sequence=2

	${resp_post}= 	Send POST Request To the Manager 	url=/Result 	request=${request}
	&{resp_result_1}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Result call upload restult:${\n} ${resp_result_1} 	console=True

	GROUP  Checking respone body
		Length Should Be 	${resp_result_1}  2
		Check ${resp_result_1} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_1} Has Result Queued
	END

	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*POST_Result*
	GROUP  Checking Result call data in database
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

Invalid Request: POST /Result
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Documentation] 	Emulating listener who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}  -s  ${CURDIR}${/}testdata${/}Issue-#289${/}POST_Result_Issue-#289.rfs

	Sleep 	5s

	Update Agent Status 	${POST_Result}[Body][AgentName]
	Sleep 	15s

	GROUP  Sending request with missing ElapsedTime data
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=1  Iteration=5  Sequence=2

		${resp_post_1}= 	Send POST Request To the Manager 	url=/Result  request=${request}  expected_status=422  expected_result=Unprocessable Entity
		&{resp_result_1}= 	Convert To Dictionary 	${resp_post_1.json()}
		Log 	POST /Result call 2 upload restult:${\n} ${resp_result_1} 	console=True

		Length Should Be 	${resp_result_1}  0
	END
	GROUP  Sending request with invalid ScriptIndex that is not configured in the scenario data
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=5  Robot=1  Iteration=5  Sequence=2

		${resp_post_2}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_2}= 	Convert To Dictionary 	${resp_post_2.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_2} 	console=True

		Length Should Be 	${resp_result_2}  2 	#??? 5th index is not available in original scenario should have failed
		Check ${resp_result_2} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_2} Has Result Queued
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=5  Robot=1  Iteration=5  Sequence=2

		${resp_post_3}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_3}= 	Convert To Dictionary 	${resp_post_3.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_3} 	console=True

		Length Should Be 	${resp_result_3}  2 	#??? UNKNOWN AGENT
		Check ${resp_result_3} Contains Agents Name 	UNKNOWN_AGENT
		Check ${resp_result_3} Has Result Queued
	END
	GROUP  Sending request with negative Robot count
		VAR 	&{request} 	AgentName=${POST_Result}[Body][AgentName]  ResultName=Test POST /Result Keyword  Result=PASS  ElapsedTime=0.003000020980834961
		...    StartTime=1572435546.383  EndTime=1572435546.386  ScriptIndex=1  Robot=-1  Iteration=5  Sequence=2

		${resp_post_4}= 	Send POST Request To the Manager 	url=/Result  request=${request}
		&{resp_result_4}= 	Convert To Dictionary 	${resp_post_4.json()}
		Log 	POST /Result call 1 upload restult:${\n} ${resp_result_4} 	console=True

		Length Should Be 	${resp_result_4}  2 	#??? negative robot count
		Check ${resp_result_4} Contains Agents Name 	${POST_Result}[Body][AgentName]
		Check ${resp_result_4} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory

Valid Request: POST /Metric
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Documentation] 	Emulating the listener and agent (monitoring scritps) who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	5s

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	VAR 	&{SecondaryMetrics} 	vmstat: Mach Virtual Memory Statistics=(page size of 4096 bytes)  vmstat: Pages free=5091.
	VAR 	&{request} 	AgentName=${POST_Metric}[AgentName]  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
	...    SecondaryMetrics=&{SecondaryMetrics}

	${resp_post}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Metric call upload restult:${\n} ${resp_result} 	console=True

	GROUP  Checking response body
		Length Should Be 	${resp_result}  2
		Check ${resp_result} Has Metric ${POST_Metric}[Body][Metric]
		Check ${resp_result} Has Result Queued
	END

	Sleep 	1s
	${result_DB}= 	Find Result DB 	directory=${RESULTS_DIR} 	result_pattern=*PreRun*
	GROUP  Checking PrimaryMetric(Name), MetricType(Type) in database
		VAR 	${query} 	SELECT Name, Type FROM Metric WHERE Name='${request}[PrimaryMetric]'
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		${last_row}= 	Convert To List 	${last_row}
		Convert List Items To String 		${last_row}
		# ${expected_data} 	Get Dictionary Values 	${request} 	sort_keys=${False}
		Should Be Equal As Strings 	${last_row}[0] 	${request}[PrimaryMetric]
		Should Be Equal As Strings 	${last_row}[1] 	${request}[MetricType]

	END
	GROUP  Checking If AgentName is saved as DataSource in database
		VAR 	${query} 	SELECT Name, Type FROM Metric WHERE Name='${POST_Metric}[AgentName]'
		@{query_result}= 	Query Result DB 	${result_DB} 	${query}
		Log 	${query_result}
		VAR 	${last_row} 	${query_result}[-1]
		${last_row}= 	Convert To List 	${last_row}
		Convert List Items To String 		${last_row}
		Should Be Equal As Strings 	${last_row}[0] 	${POST_Metric}[AgentName]
		Should Be Equal As Strings 	${last_row}[1] 	DataSource

	END
	GROUP  Checking MetricTime and SecondaryMetrics in database
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

Invalid Request: POST /Metric
	[Tags] 	windows-latest  ubuntu-latest  macos-latest  Issue #289  robot:continue-on-failure
	[Documentation] 	Emulating the listener and agent who make this call to the manager.
	[Setup] 	Run Keywords
	...    Set Test Variable 	${RESULTS_DIR}  ${CURDIR}${/}testdata${/}Issue-#289${/}results 	AND
	...    Create Directory 	${RESULTS_DIR} 	AND
	...    Run Manager CLI  -n  -d  ${RESULTS_DIR}

	Sleep 	5s

	Update Agent Status 	${POST_Metric}[AgentName]
	Sleep 	15s

	GROUP  Sending request with missing SecondaryMetrics data
		VAR 	&{request} 	AgentName=${POST_Metric}[AgentName]  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970

		${resp_post_1}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}  expected_status=422  expected_result=Unprocessable Entity
		&{resp_result_1}= 	Convert To Dictionary 	${resp_post_1.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_1} 	console=True

		Length Should Be 	${resp_result_1}  0
	END
	GROUP  Sending request with unregistered AgentName
		VAR 	&{SecondaryMetrics} 	vmstat: Mach Virtual Memory Statistics=(page size of 4096 bytes)  vmstat: Pages free=5091.
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
		...    SecondaryMetrics=&{SecondaryMetrics}

		${resp_post_2}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
		&{resp_result_2}= 	Convert To Dictionary 	${resp_post_2.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_2} 	console=True

		Length Should Be 	${resp_result_2}  2 	#??? UNKNOWN AGENT
		Check ${resp_result_2} Has Metric my_test_server
		Check ${resp_result_2} Has Result Queued
	END
	GROUP  Sending request with invalid SecondaryMetrics format (list) not (dict)
		VAR 	@{SecondaryMetrics} 	Mach Virtual Memory Statistics=(page size of 4096 bytes)  Pages free=5091.
		VAR 	&{request} 	AgentName=UNKNOWN_AGENT  PrimaryMetric=my_test_server  MetricType=AUT Web  MetricTime=1753812970
		...    SecondaryMetrics=@{SecondaryMetrics}

		${resp_post_3}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
		&{resp_result_3}= 	Convert To Dictionary 	${resp_post_3.json()}
		Log 	POST /Metric call upload restult:${\n} ${resp_result_3} 	console=True

		Length Should Be 	${resp_result_3}  2 	#??? will try to save it, but throw exception in manager code
		Check ${resp_result_3} Has Metric my_test_server
		Check ${resp_result_3} Has Result Queued
	END

	[Teardown] 	Run Keywords
	...    Stop Manager CLI 	AND 	Clear Result Directory
