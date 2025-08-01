*** Settings ***
Documentation 	This resource file contains keywords for Manager command line only.

Resource 	../../../Common/Common.resource

Library 	RequestsLibrary
Library 	hash_file.py

*** Keywords ***
Send ${type} Request To the Manager
	[Arguments] 	${url}=/  ${request}=${None}  ${expected_status}=OK  ${expected_result}=OK
	Create Session 	Manager API  http://localhost:8138
	${resp}= 	Run Keyword 	${type} On Session  Manager API  ${url}  json=${request}  expected_status=${expected_status}

	Log 	${resp.text}
	TRY
		Log 	${resp.json()}
	EXCEPT
		Log 	${resp.text}
	END
	TRY
		Should Be Equal As Strings 	${resp.reason}  ${expected_result}
	EXCEPT
		Should Be Equal As Strings 	${resp.text}  ${expected_result}
	END

	RETURN 	${resp}

Update Agent Status
	[Arguments] 	${agent_name}=myagent  ${status}=Ready  ${Agent_IP}=${None}  ${Robots}=${0}  ${CPU}=${4.7}  ${MEM}=${30.97}  ${NET}=${0.01}
	IF  ${Agent_IP} == ${None}
		${ipv4} 	${ipv6}= 	Get Ip Addresses
		VAR 	@{Agent_IP} 	${ipv4}[0]  ${ipv6}[0]
	END
	VAR 	&{request_body} 	AgentName=${agent_name}  Status=${status}  AgentIPs=${Agent_IP}  Robots=${Robots}  CPU%=${CPU}  MEM%=${MEM}  NET%=${NET}

	${resp_post}= 	Send POST Request To the Manager 	url=/AgentStatus 	request=${request_body}

	RETURN 	${resp_post}  ${request_body}

Check ${call_result} Contains Agents Name
	[Arguments] 	${agent_name}
	Convert To String 	${call_result}[AgentName]
	Convert To String 	${agent_name}
	Should Be Equal As Strings 	${call_result}[AgentName] 	${agent_name}

Check ${call_result} Has ${type} ${expceted}
	Convert To String 	${call_result}[${type}]
	Convert To String 	${expceted}
	Should Be Equal As Strings 	${call_result}[${type}] 	${expceted}

# Verify Metrics Row
# 	[Arguments] 	${row}  ${ParentID}  ${DataSource}  ${Key}  ${Value}  ${Time}
# 	Convert List Items To String 		${row}
# 	Should Be Equal As Strings 	${row}[0] 	${ParentID}
# 	Should Be Equal As Strings 	${row}[1] 	${Time}
# 	Should Be Equal As Strings 	${row}[2] 	${SecondaryMetric}
# 	Should Be Equal As Strings 	${row}[3] 	${ParentID}
# 	Should Be Equal As Strings 	${row}[4] 	${ParentID}

