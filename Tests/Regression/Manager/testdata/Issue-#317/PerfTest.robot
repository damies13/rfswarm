*** Settings ***
Documentation 	Tests to generate addional load on the Manager

# Resource 	../../Common/Common.resource

Library 	RequestsLibrary
# Library 	hash_file.py
Library 	Collections

Test Timeout 	10 minutes

Suite Setup 	Create Session 	Manager API  ${RFS_SWARMMANAGER}

*** Variables ***
${DEFAULT_API_TIMEOUT} 	${30}

${RFS_AGENTNAME} 		Agent Name Not Set
${RFS_SWARMMANAGER} 	http://localhost:8138
${RFS_ROBOT} 			1
${RFS_INDEX} 			1
${RFS_ITERATION} 		1
${SLEEPTIME}			500ms
# ${SLEEPTIME}			1s
# ${SLEEPTIME}			10s

*** Test Cases ***

Send Metric Data to the Manager
	[Documentation] 	Emulating the agent and monitoring scripts who make this call to the manager.

	Send Metric to Manager
	Sleep 	${SLEEPTIME}

Send Result Data to the Manager
	[Documentation] 	Emulating listener who make this call to the manager.

	Send Result to Manager
	Sleep 	${SLEEPTIME}

*** Keywords ***

Send ${type} Request To the Manager
	[Arguments] 	${url}=/  ${request}=${None}  ${expected_status}=OK  ${expected_result}=OK
	# Create Session 	Manager API  ${RFS_SWARMMANAGER}
	${response}= 	Run Keyword 	${type} On Session
	...    Manager API  ${url}
	...    json=${request}
	...    expected_status=${expected_status}
	...    msg=Failed to send request: ${request} to the manager.
	Log 	${response.text}

	TRY
		Log 	${response.json()}
	EXCEPT
		Log 	Couldn't get json from response. Showing text instead.
		Log 	${response.text}
	END

	TRY
		Should Be Equal As Strings 	${response.reason}  ${expected_result}
		...    msg=Expected result doesn't match \${response.reason}: ${response.reason} != ${expected_result}
	EXCEPT
		Log 	Check text message instead of reason from \${response}
		Should Be Equal As Strings 	${response.text}  ${expected_result}
		...    msg=Expected result doesn't match \${response.text}: ${response.text} != ${expected_result}
	END

	RETURN 	${response}

Check ${call_result} Contains Agents Name
	[Arguments] 	${agent_name}
	Convert To String 	${call_result}[AgentName]
	Convert To String 	${agent_name}
	Should Be Equal 	${call_result}[AgentName]  ${agent_name}
	...    msg=Result from request (AgentName='${call_result}[AgentName]') doesn't have valid AgentName: ${agent_name}

Check ${call_result} Has ${type} ${expceted}
	${status}= 	Should Contain 	${call_result}  ${type}
	IF  ${status}
		Fail 	Result body doesn't contain '${type}' key.
	ELSE
		Convert To String 	${call_result}[${type}]
	END
	Convert To String 	${expceted}
	Should Be Equal 	${call_result}[${type}] 	${expceted}
	...    msg=Result from request doesn't have expected value for '${type}' field: ${call_result}[${type}] != ${expceted}

Send Result to Manager
	VAR 	${agentname} 			${RFS_AGENTNAME}
	${basetime}= 	Get Time 	epoch
	${endtime}= 	Evaluate 	${basetime} + 0.${RFS_ITERATION}${RFS_ROBOT}${RFS_INDEX}
	${starttime}= 	Evaluate 	${basetime} - ${RFS_INDEX} + 0.${RFS_ROBOT}${RFS_ITERATION}${RFS_INDEX}

	VAR 	&{request} 	AgentName=${agentname}  ResultName=Simulated Keyword Name  Result=PASS  ElapsedTime=0.0${RFS_ROBOT}${RFS_INDEX}${RFS_ITERATION}
	...    StartTime=${starttime}  EndTime=${endtime}  ScriptIndex=${RFS_INDEX}  Robot=${RFS_ROBOT}  Iteration=${RFS_ITERATION}  Sequence=2

	${resp_post}= 	Send POST Request To the Manager 	url=/Result 	request=${request}
	&{resp_result_1}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Result call upload result:${\n} ${resp_result_1} 	console=True

	GROUP  Check response body
		Length Should Be 	${resp_result_1}  2
		Check ${resp_result_1} Contains Agents Name 	${agentname}
		Check ${resp_result_1} Has Result Queued
	END

Send Metric to Manager
	VAR 	${agentname} 			${RFS_AGENTNAME}
	${endtime}= 	Get Time 	epoch
	VAR 	&{SecondaryMetrics} 	vmstat: Mach Virtual Memory Statistics=(page size of 138${RFS_ROBOT}${RFS_INDEX} bytes)  vmstat: Pages free=${RFS_ROBOT}${RFS_INDEX}${RFS_ITERATION}.
	VAR 	&{request} 	AgentName=${agentname}  PrimaryMetric=my_test_server  MetricType=Simulated Metric  MetricTime=${endtime}
	...    SecondaryMetrics=&{SecondaryMetrics}

	${resp_post}= 	Send POST Request To the Manager 	url=/Metric 	request=${request}
	&{resp_result}= 	Convert To Dictionary 	${resp_post.json()}
	Log 	POST /Metric call upload result:${\n} ${resp_result} 	console=True

	GROUP  Check response body
		Length Should Be 	${resp_result}  2
		Check ${resp_result} Has Metric my_test_server
		Check ${resp_result} Has Result Queued
	END


# 
