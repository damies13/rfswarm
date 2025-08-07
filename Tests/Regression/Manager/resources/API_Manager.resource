*** Settings ***
Documentation 	This resource file contains keywords for Manager command line only.

Resource 	../../../Common/Common.resource

Library 	RequestsLibrary
Library 	hash_file.py

*** Keywords ***
Send ${type} Request To the Manager
	[Arguments] 	${url}=/  ${request}=${None}  ${expected_status}=OK  ${expected_result}=OK
	Create Session 	Manager API  http://localhost:8138
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
		...    msg=Expected result doesn't match \${response.text}: ${response.reason} != ${expected_result}
	END

	RETURN 	${response}

Update Agent Status
	[Arguments] 	${agent_name}=myagent  ${status}=Ready  ${Agent_IP}=${None}
	...    ${Robots}=${0}  ${CPU}=${4.7}  ${MEM}=${30.97}  ${NET}=${0.01}
	IF  ${Agent_IP} == ${None}
		${ipv4} 	${ipv6}= 	Get Ip Addresses
		VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]
	END
	VAR 	&{request_body} 	AgentName=${agent_name}  Status=${status}  AgentIPs=${Agent_IP}
	...    Robots=${Robots}  CPU%=${CPU}  MEM%=${MEM}  NET%=${NET}

	${response_post}= 	Send POST Request To the Manager
	...    url=/AgentStatus
	...    request=${request_body}

	RETURN 	${response_post}  ${request_body}

Check ${call_result} Contains Agents Name
	[Arguments] 	${agent_name}
	Convert To String 	${call_result}[AgentName]
	Convert To String 	${agent_name}
	Should Be Equal 	${call_result}[AgentName]  ${agent_name}
	...    msg=Result from request (AgentName='${call_result}[AgentName]') doesn't have valid AgentName: ${agent_name}

Check ${call_result} Has ${type} ${expceted}
	${status}= 	Should Contain 	${call_result}  ${type}
	IF  not ${status}
		Fail 	Result body doesn't contain '${type}' key.
	ELSE
		Convert To String 	${call_result}[${type}]
	END
	Convert To String 	${expceted}
	Should Be Equal 	${call_result}[${type}] 	${expceted}
	...    msg=Result from request doesn't have expected value for '${type}' field: ${call_result}[${type}] != ${expceted}
