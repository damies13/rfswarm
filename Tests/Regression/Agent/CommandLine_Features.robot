*** Settings ***
Resource 	resources/CommandLine_Agent.resource
Resource 	../../Common/Directories_and_Files.resource
Resource 	../../Common/Logs.resource
Resource 	../../Common/RFS_Components.resource
Resource 	../../Common/Database.resource

Suite Setup 	Common.Basic Suite Initialization Agent

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	Run Agent CLI 	-g 	6 	-c 	ICON
	Wait For Agent Process

	Check Icon Install
Agent Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -v
	${result}= 	Run 	rfswarm-agent -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Agent

Agent Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py -h
	${result}= 	Run 	rfswarm-agent -h
	Log to console 	${\n}${result}
	Should Contain	${result}	AGENTNAME

Agent Command Line INI -i
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini

	Run Agent CLI 	-i	${inifile}
	Log To Console	Run Agent CLI with alternate ini file with variable.
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	${inifile}

	[Teardown]	Stop Agent CLI

Agent Command Line INI --ini
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini

	Run Agent CLI 	--ini	${inifile}
	Log To Console	Run Agent CLI with alternate ini file with variable.
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	${inifile}

	[Teardown]	Stop Agent CLI

Agent Command Line MANAGER -m
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	Log To Console	Run Agent CLI and Manager and see if they will connect.
	Run Agent CLI 		-m 	http://localhost:8138
	Run Manager CLI 	-n
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process	60s
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	Manager Connected

	[Teardown]	Run Keywords	Stop Agent CLI 	Stop Manager CLI

Agent Command Line MANAGER --manager
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	Log To Console	Run Agent CLI and Manager and see if they will connect.
	Run Agent CLI 		--manager 	http://localhost:8138
	Run Manager CLI 	-n
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process	60s
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	Manager Connected

	[Teardown]	Run Keywords	Stop Agent CLI 	Stop Manager CLI

Agent Command Line AGENTDIR -d
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}agentdir

	Log To Console	Run Agent CLI with custom dir.
	Run Agent CLI 	-d 	${agentdir}
	Sleep 	10s
	Stop Agent CLI
	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	Should Not Be Empty		${agentdir_scripts}

	[Teardown]	Stop Agent CLI

Agent Command Line AGENTDIR --agentdir
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}agentdir

	Log To Console	Run Agent CLI with custom dir.
	Run Agent CLI 	--agentdir 	${agentdir}
	Sleep 	10s
	Stop Agent CLI
	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	Should Not Be Empty		${agentdir_scripts}

	[Teardown]	Stop Agent CLI

Agent Command Line ROBOT -r
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14

	Run Process 	whereis 	robot		alias=data	#not working on windows
	${pip_data} 	Get Process Result	data
	Should Not Be Empty 	${pip_data.stdout}		msg=Cant find robotframework pip informations
	${pip_data_list}=	Split String	${pip_data.stdout}
	Log To Console	robot executable: ${pip_data_list}[1]

	${scenario_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	VAR 	${robot_exec} 		${pip_data_list}[1]
	# VAR 	${scenario_dir} 	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs

	Log To Console	Run Agent CLI with custom robot executable.
	Run Agent CLI 		-g 	1 	-r 	${robot_exec}
	Run Manager CLI 	-g 	1 	-n 	-s 	${scenario_dir}
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process	8min
	Stop Agent CLI

	@{test_result}= 	List Directories In Directory	${RESULTS_DIR}	absolute=${True}	pattern=*_Issue-#14
	Log To Console		Result dir: ${test_result}
	Should Not Be Empty 	${test_result}
	@{result_content}=	List Directories In Directory	${test_result}[0]
	Log To Console		Result dir content: ${result_content}
	Should Not Be Empty 	${result_content}
	@{test_logs}=	List Directories In Directory	${test_result}[0]${/}logs
	Log To Console		Logs dirs: ${test_logs}
	Should Not Be Empty 	${test_logs}

	[Teardown]	Run Keywords	Stop Agent CLI 	Stop Manager CLI

Agent Command Line XMLMODE -x
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir

	Log To Console	Run Agent CLI with xmlmode.
	Run Agent CLI 	-x 	-d 	${agentdir}
	Sleep 	10s
	Stop Agent CLI

	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py

	[Teardown]	Stop Agent CLI

Agent Command Line XMLMODE --xmlmode
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir

	Log To Console	Run Agent CLI with xmlmode.
	Run Agent CLI 	--xmlmode 	-d 	${agentdir}
	Sleep 	10s
	Stop Agent CLI

	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py

	[Teardown]	Stop Agent CLI

Agent Command Line AGENTNAME -a
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Server	127.0.0.1	8138

	VAR 	${agent_name} 		Issue-#14AGENTNAME

	Log To Console	Run Agent CLI with custom agent name.
	Run Agent CLI 	-a 	${agent_name}
	Test Agent Connectivity
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${body}=	Get Request Body
	${body}=	Decode Bytes To String	${body} 	UTF-8

	Should Be Equal 	${method}	POST
	Log 	${body}
	Should Contain	${body} 	Issue-#14AGENTNAME

	[Teardown]	Run Keywords	Stop Server 	Stop Agent CLI

Agent Command Line AGENTNAME --agentname
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Server	127.0.0.1	8138

	VAR 	${agent_name} 		Issue-#14AGENTNAME

	Log To Console	Run Agent CLI with custom agent name.
	Run Agent CLI 	--agentname 	${agent_name}
	Test Agent Connectivity
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${body}=	Get Request Body
	${body}=	Decode Bytes To String	${body} 	UTF-8

	Should Be Equal 	${method}	POST
	Log 	${body}
	Should Contain	${body} 	Issue-#14AGENTNAME

	[Teardown]	Run Keywords	Stop Server 	Stop Agent CLI

Agent Command Line PROPERTY -p
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#14${/}property
	VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db

	Create Directory 	${test_dir}
	Log To Console	Run Agent CLI with custom prop.
	Run Agent CLI 		-p 	Issue-#14
	Run Manager CLI 	-n 	-d 	${test_dir}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager
	Sleep 	10s
	Stop Agent CLI
	Stop Manager CLI

	Log To Console 	Checking result data base
	# ${dbfile} 	Find Result DB 		result_pattern=PreRun
	${prop_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM MetricData WHERE MetricType='Agent' AND SecondaryMetric='Issue-#14'

	${len}= 	Get Length 	${prop_result}
	Should Be True 	${len} > 0
	...    msg=Custom propery 'Issue-#14' not found in PreRun db. ${\n}Query Result: ${prop_result}

	[Teardown]	Run Keywords	Stop Agent CLI 	Stop Manager CLI

Agent Yaml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	VAR 	${yamlurl}= 	http://yamlmanager:8001/
	${yamlfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.yaml

	Run Agent CLI 	--ini	${yamlfile} 	-g 	2
	Log To Console	Run Agent CLI with Yaml Configuration File.
	Sleep    20
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	${yamlurl}

	[Teardown]	Stop Agent CLI

Agent Yml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	VAR 	${yamlurl}= 	http://ymlmanager:8003/
	${yamlfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.yml

	Run Agent CLI 	--ini	${yamlfile} 	-g 	2
	Log To Console	Run Agent CLI with Yaml Configuration File.
	Sleep    20
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	${yamlurl}

	[Teardown]	Stop Agent CLI

Agent JSON Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	VAR 	${jsonurl}= 	http://jsonmanager:8002/
	${jsonfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.json

	Run Agent CLI 	--ini	${jsonfile} 	-g 	2
	Log To Console	Run Agent CLI with JSON Configuration File.
	Sleep    20
	Stop Agent CLI
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	${result_stdout}=	Get File	${stdout_agent_path}
	Should Contain	${result_stdout}	${jsonurl}

	[Teardown]	Stop Agent CLI
