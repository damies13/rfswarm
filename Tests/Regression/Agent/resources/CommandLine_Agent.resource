*** Settings ***
Documentation 	This resource file contains keywords for Agent command line only.

Resource 	../../../Common/Common.resource

Library 	HttpCtrl.Server

*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 		rfswarm
${pyfile_agent} 	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${pyfile_manager} 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process_agent} 	${None}
${process_manager} 	${None}

# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun

*** Keywords ***
Run Agent
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	${process}= 	Start Process 	${cmd_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Run Manager CLI
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	IF  '-d' not in ${options}
		Create Directory 	${RESULTS_DIR}
		Append To List 	${options} 	-d 	${RESULTS_DIR}
	END
	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	${process}= 	Start Process 	${cmd_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}
	Sleep	5

Wait For Manager
	[Arguments]		${timeout}=10min
	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=kill
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Stop Manager
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Sleep	3s
		IF  '${PLATFORM}' == 'windows'	# Send Signal To Process keyword does not work on Windows
			${result}= 	Terminate Process		${process_manager}
		ELSE
			Send Signal To Process 	SIGINT 	${process_manager}
			${result}= 	Wait For Process 	${process_manager}	timeout=30	on_timeout=kill
		END
	ELSE
		# get result var for process even if not running any more
		${result}= 	Get Process Result		${process_manager}
	END
	Log		${result.stdout}
	Log		${result.stderr}

	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	Process returned: ${result.rc}

Stop Agent
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		Sleep	3s
		IF  '${PLATFORM}' == 'windows'	# Send Signal To Process keyword does not work on Windows
			${result} = 	Terminate Process		${process_agent}
		ELSE
			Send Signal To Process 	SIGINT 	${process_agent}
			${result}= 	Wait For Process 	${process_agent}	timeout=30	on_timeout=kill
		END
	ELSE
		# get result var for process even if not running any more
		${result}= 	Get Process Result		${process_agent}
	END
	Log		${result.stdout}
	Log		${result.stderr}
	# Should Be Equal As Integers 	${result.rc} 	0

Test Agent Connectivity
	#[Setup] 	Start Server	127.0.0.1	8138

	# wait for GET poll to /
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method} 	GET
	Should Be Equal 	${url}		/

	# wait for POST to /Jobs
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method}	POST
	#Should Be Equal 	${url}		/Jobs

	#[Teardown]	Stop Server

Get Agent PIP Data
	Run Process		pip		show	rfswarm-agent		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Agent must be installed with pip
	Log		${pip_data.stdout}
	RETURN		${pip_data.stdout}

Get Agent Default Save Path
	${pip_data}=	Get Agent PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_agent${/}

#
