*** Settings ***
Resource 	CommandLine_Common.robot
Suite Setup 	Set Platform

Suite Setup 	Set Platform

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	@{agent_options}= 	Create List 	-g 	6 	-c 	ICON
	Run Agent 	${agent_options}
	Sleep    2
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

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
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14	# can't get agent output in windows

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini
	VAR		@{agnt_options}		-i	${inifile}

	Run Agent 	${agnt_options}
	Log To Console	Run Agent with alternate ini file with variable.
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${result_stdout}=	Get File	${OUTPUT DIR}${/}stdout_agent.txt
	Should Contain	${result_stdout}	${inifile}

	[Teardown]	Stop Agent

Agent Command Line INI --ini
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14	# can't get agent output in windows

	${inifile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini
	VAR		@{agnt_options}		--ini	${inifile}

	Run Agent 	${agnt_options}
	Log To Console	Run Agent with alternate ini file with variable.
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${result_stdout}=	Get File	${OUTPUT DIR}${/}stdout_agent.txt
	Should Contain	${result_stdout}	${inifile}

	[Teardown]	Stop Agent

Agent Command Line MANAGER -m
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14 	# can't get agent output in windows

	VAR 	@{agnt_options} 	-m 	http://localhost:8138
	VAR 	@{mngr_options} 	-n

	Log To Console	Run Agent and Manager and see if they will connect.
	Run Agent 	${agnt_options}
	Run Manager CLI 	${mngr_options}
	Wait For Manager	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${result_stdout}=	Get File	${OUTPUT DIR}${/}stdout_agent.txt
	Should Contain	${result_stdout}	Manager Connected

	[Teardown]	Run Keywords	Stop Agent	Stop Manager

Agent Command Line MANAGER --manager
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14 	# can't get agent output in windows

	VAR 	@{agnt_options} 	--manager 	http://localhost:8138
	VAR 	@{mngr_options} 	-n

	Log To Console	Run Agent and Manager and see if they will connect.
	Run Agent 	${agnt_options}
	Run Manager CLI 	${mngr_options}
	Wait For Manager	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${result_stdout}=	Get File	${OUTPUT DIR}${/}stdout_agent.txt
	Should Contain	${result_stdout}	Manager Connected

	[Teardown]	Run Keywords	Stop Agent	Stop Manager

Agent Command Line AGENTDIR -d
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}agentdir
	VAR 	@{agnt_options} 	-d 	${agentdir}

	Log To Console	Run Agent with custom dir.
	Run Agent 	${agnt_options}
	Sleep 	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	Should Not Be Empty		${agentdir_scripts}

	[Teardown]	Stop Agent

Agent Command Line AGENTDIR --agentdir
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}agentdir
	VAR 	@{agnt_options} 	--agentdir 	${agentdir}

	Log To Console	Run Agent with custom dir.
	Run Agent 	${agnt_options}
	Sleep 	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	Should Not Be Empty		${agentdir_scripts}

	[Teardown]	Stop Agent

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
	VAR 	@{agnt_options} 	-g 	1 	-r 	${robot_exec}
	VAR 	@{mngr_options} 	-g 	1 	-n 	-s 	${scenario_dir}

	Log To Console	Run Agent with custom robot executable.
	Run Agent 	${agnt_options}
	Sleep 	5s
	Run Manager CLI 	${mngr_options}
	Wait For Manager	8min
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	@{test_result}= 	List Directories In Directory	${results_dir}	absolute=${True}	pattern=*_Issue-#14
	Log To Console		Result dir: ${test_result}
	Should Not Be Empty 	${test_result}
	@{result_content}=	List Directories In Directory	${test_result}[0]
	Log To Console		Result dir content: ${result_content}
	Should Not Be Empty 	${result_content}
	@{test_logs}=	List Directories In Directory	${test_result}[0]${/}logs
	Log To Console		Logs dirs: ${test_logs}
	Should Not Be Empty 	${test_logs}

	[Teardown]	Run Keywords	Stop Agent	Stop Manager

Agent Command Line XMLMODE -x
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir
	VAR 	@{agnt_options} 	-x 	-d 	${agentdir}

	Log To Console	Run Agent with xmlmode.
	Run Agent 	${agnt_options}
	Sleep 	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt

	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py

	[Teardown]	Stop Agent

Agent Command Line XMLMODE --xmlmode
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	${agentdir} 		${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir
	VAR 	@{agnt_options} 	--xmlmode 	-d 	${agentdir}

	Log To Console	Run Agent with xmlmode.
	Run Agent 	${agnt_options}
	Sleep 	10s
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt

	@{agentdir_dirs}=	List Directories In Directory	${agentdir}
	List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
	${agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
	List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py

	[Teardown]	Stop Agent

Agent Command Line AGENTNAME -a
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Server	127.0.0.1	8138

	VAR 	${agent_name} 		Issue-#14AGENTNAME
	VAR 	@{agnt_options} 	-a 	${agent_name}

	Log To Console	Run Agent with custom agent name.
	Run Agent 	${agnt_options}
	Test Agent Connectivity
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${body}=	Get Request Body
	${body}=	Decode Bytes To String	${body} 	UTF-8

	Should Be Equal 	${method}	POST
	Log 	${body}
	Should Contain	${body} 	Issue-#14AGENTNAME
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt

	[Teardown]	Run Keywords	Stop Server 	Stop Agent

Agent Command Line AGENTNAME --agentname
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Server	127.0.0.1	8138

	VAR 	${agent_name} 		Issue-#14AGENTNAME
	VAR 	@{agnt_options} 	--agentname 	${agent_name}

	Log To Console	Run Agent with custom agent name.
	Run Agent 	${agnt_options}
	Test Agent Connectivity
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${body}=	Get Request Body
	${body}=	Decode Bytes To String	${body} 	UTF-8

	Should Be Equal 	${method}	POST
	Log 	${body}
	Should Contain	${body} 	Issue-#14AGENTNAME
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt

	[Teardown]	Run Keywords	Stop Server 	Stop Agent

Agent Command Line PROPERTY -p
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	VAR 	@{agnt_options} 	-p 	Issue-#14
	VAR 	@{mngr_options} 	-n

	Log To Console	Run Agent with custom prop.
	Run Agent 	${agnt_options}
	Run Manager CLI 	${mngr_options}
	Sleep	20s
	Stop Agent
	Stop Manager

	Log To Console 	Checking result data base
	${dbfile} 	Find Result DB 		result_pattern=PreRun
	${prop_result} 	Query Result DB 	${dbfile}
	...    SELECT * FROM MetricData WHERE MetricType='Agent' AND SecondaryMetric='Issue-#14'

	${len}= 	Get Length 	${prop_result}
	Should Be True 	${len} > 0
	...    msg=Custom propery 'Issue-#14' not found in PreRun db. ${\n}Query Result: ${prop_result}

	[Teardown]	Run Keywords	Stop Agent	Stop Manager