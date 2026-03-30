*** Settings ***
Resource 	../../Resources/CommandLine/Agent/CommandLine_Agent.resource
Resource 	../../Resources/Business/Agent/common.resource

Suite Setup 	Common.Basic Suite Initialization Agent

*** Test Cases ***
Install Application Icon or Desktop Shortcut
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #145

	GROUP 	Start the Agent with the -c ICON to create app icons and shortcut
		Run Agent CLI 	-g  6  -c  ICON
	END
	Sleep 	2
	Show Agent Logs
	Check Icon Install

Agent Command Line INI -i
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the -i argument
		${inifile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini
		Run Agent CLI 	-g  1  -i  ${inifile}
	END
	Stop Agent CLI
	GROUP 	Check in logs if Agent loaded INI file
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	${inifile}
	END

	[Teardown]	Stop Agent CLI

Agent Command Line INI --ini
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the --ini argument
		${inifile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#14${/}RFSwarmAgent.ini
		Run Agent CLI 	-g  1  --ini  ${inifile}
	END
	Stop Agent CLI
	GROUP 	Check in logs if Agent loaded INI file
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	${inifile}
	END

	[Teardown]	Stop Agent CLI

Agent Command Line MANAGER -m
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the -m argument
		VAR 	${url}= 	http://localhost:8138
		Run Agent CLI 	-g  1  -m  ${url}
	END
	Run Manager with Default Settings
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process	60s
	Stop Agent
	GROUP 	Check in logs if Agent has connected to the Manager
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	Manager Connected
	END

	[Teardown] 	Stop Agent and Manager

Agent Command Line MANAGER --manager
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the --manager argument
		VAR 	${url}= 	http://localhost:8138
		Run Agent CLI 	-g  1  --manager  ${url}
	END
	Run Manager with Default Settings
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process	60s
	Stop Agent
	GROUP 	Check in logs if Agent has connected to the Manager
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	Manager Connected
	END

	[Teardown] 	Stop Agent and Manager

Agent Command Line AGENTDIR -d
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the -d argument
		VAR 	${agentdir}= 	${CURDIR}${/}testdata${/}Issue-#14${/}agentdir
		Run Agent CLI 	-d  ${agentdir}
	END
	Sleep 	10s
	Stop Agent
	GROUP 	Check if Agent has created script files in the custom directory
		@{agentdir_dirs}=	List Directories In Directory	${agentdir}
		List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
		@{agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
		FOR  ${agentdir_script}  IN  @{agentdir_scripts}
			Should Not Be Empty		${agentdir_script}
		END
	END

	[Teardown] 	Run Keywords
	...    Stop Agent 	AND
	...    Remove Directory 	${agentdir} 	recursive=${True}

Agent Command Line AGENTDIR --agentdir
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the --agentdir argument
		VAR 	${agentdir}= 	${CURDIR}${/}testdata${/}Issue-#14${/}agentdir
		Run Agent CLI 	--agentdir  ${agentdir}
	END
	Sleep 	10s
	Stop Agent
	GROUP 	Check if Agent has created script files in the custom directory
		@{agentdir_dirs}=	List Directories In Directory	${agentdir}
		List Should Contain Value	${agentdir_dirs}	scripts		msg=Can't find scripts dir in custom Agent dir
		@{agentdir_scripts}=	List Files In Directory		${agentdir}${/}scripts
		FOR  ${agentdir_script}  IN  @{agentdir_scripts}
			Should Not Be Empty		${agentdir_script}
		END
	END

	[Teardown] 	Run Keywords
	...    Stop Agent 	AND
	...    Remove Directory 	${agentdir} 	recursive=${True}

Agent Command Line ROBOT -r
	[Tags]	ubuntu-latest 	macos-latest 	Issue #14

	GROUP 	Set Test Variables
		${robot_exec}= 		Find Robot Framework Executable
		${scenario_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#14${/}Issue-#14.rfs
	END
	GROUP 	Run Agent with the -r argument (custom robot executable)
		Run Agent CLI 	-g  1  -r  ${robot_exec}
	END
	Run Manager with "${scenario_dir}" and "${results_dir}"
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process 	8min
	Stop Agent
	Show Manager Logs
	Show Agent Logs

	GROUP 	Check if Manager's Logs directory is not empty
		@{test_result}= 	List Directories In Directory
		...    ${RESULTS_DIR}	absolute=${True}	pattern=*_Issue-#14
		Log 	Result dir: ${test_result} 	console=${True}
		Should Not Be Empty 	${test_result}
		@{result_content}=	List Directories In Directory	${test_result}[0]
		Log 	Result dir content: ${result_content} 	console=${True}
		Should Not Be Empty 	${result_content}
		@{test_logs}=	List Directories In Directory	${test_result}[0]${/}logs
		Log 	Logs dirs: ${test_logs} 	console=${True}
		Should Not Be Empty 	${test_logs}
	END

	[Teardown] 	Stop Agent and Manager

Agent Command Line XMLMODE -x
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the -x argument
		VAR 	${agentdir} 	${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir
		Run Agent CLI 	-g  1  -x  -d  ${agentdir}
	END
	Sleep 	10s
	Stop Agent
	GROUP 	Check if Agent didn't create RFSListener python files
		@{agentdir_dirs}= 	List Directories In Directory 	${agentdir}
		List Should Contain Value 	${agentdir_dirs} 	scripts 	msg=Can't find scripts dir in custom Agent dir
		${agentdir_scripts}= 	List Files In Directory 	${agentdir}${/}scripts
		List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
		List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py
	END

	[Teardown] 	Stop Agent

Agent Command Line XMLMODE --xmlmode
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Run Agent with the --xmlmode argument
		VAR 	${agentdir} 	${CURDIR}${/}testdata${/}Issue-#14${/}xmlmode_dir
		Run Agent CLI 	-g  1  --xmlmode  -d  ${agentdir}
	END
	Sleep 	10s
	Stop Agent
	GROUP 	Check if Agent didn't create RFSListener python files
		@{agentdir_dirs}= 	List Directories In Directory 	${agentdir}
		List Should Contain Value 	${agentdir_dirs} 	scripts 	msg=Can't find scripts dir in custom Agent dir
		${agentdir_scripts}= 	List Files In Directory 	${agentdir}${/}scripts
		List Should Not Contain Value 	${agentdir_scripts} 	RFSListener3.py
		List Should Not Contain Value 	${agentdir_scripts} 	RFSListener2.py
	END

	[Teardown] 	Stop Agent

Agent Command Line AGENTNAME -a
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Manager Mock Server

	GROUP 	Run Agent with the -a argument
		VAR 	${agent_name} 		Issue-#14AGENTNAME
		Run Agent CLI 	-g  1  -a  ${agent_name}
	END
	Test Agent Connectivity
	GROUP 	Check if request body has custom Agent name
		Wait For Request 	20
		Reply By 			200
		${method}= 	Get Request Method
		${body}= 	Get Request Body
		${body}= 	Decode Bytes To String 	${body} 	UTF-8

		Should Be Equal 	${method} 	POST
		Log 	${body}
		Should Contain 		${body} 	Issue-#14AGENTNAME
	END

	[Teardown]	Run Keywords	Stop Server 	Stop Agent CLI

Agent Command Line AGENTNAME --agentname
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14
	[Setup] 	Start Manager Mock Server

	GROUP 	Run Agent with the --agentname argument
		VAR 	${agent_name} 		Issue-#14AGENTNAME
		Run Agent CLI 	-g  1  --agentname  ${agent_name}
	END
	Test Agent Connectivity
	GROUP 	Check if request body has custom Agent name
		Wait For Request 	20
		Reply By 			200
		${method}= 	Get Request Method
		${body}= 	Get Request Body
		${body}= 	Decode Bytes To String 	${body} 	UTF-8

		Should Be Equal 	${method} 	POST
		Log 	${body}
		Should Contain 		${body} 	Issue-#14AGENTNAME
	END

	[Teardown]	Run Keywords	Stop Server 	Stop Agent CLI

Agent Command Line PROPERTY -p
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #14

	GROUP 	Set Test Variables
		VAR 	${test_dir} 		${CURDIR}${/}testdata${/}Issue-#14${/}property
		VAR 	${dbfile} 			${test_dir}${/}PreRun${/}PreRun.db
	END

	Create Directory 	${test_dir}
	GROUP 	Run Agent with the -p argument (custom propety)
		Run Agent CLI 		-p 	Issue-#14
	END
	Run Manager with Custom Result Directory 	${test_dir}
	Wait Until Created 	${dbfile}
	Wait Until the Agent Connects to the Manager

	GROUP 	Check Manager's result database
		# this should be in manager's database immediately after it connect's
		VAR 	${query}= 	SELECT * FROM MetricData WHERE MetricType='Agent' AND SecondaryMetric='Issue-#14'
		Wait Until the Query Is Not Empty 	${dbfile}  sql=${query}
		${prop_result} 	Query Result DB 	${dbfile}  sql=${query}

		${len}= 	Get Length 	${prop_result}
		Should Be True 	${len} > 0
		...    msg=Custom propery 'Issue-#14' not found in PreRun db. ${\n}Query Result: ${prop_result}
	END

	[Teardown]	Stop Agent and Manager

Agent Yaml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	GROUP 	Set Test Variables
		VAR 	${yamlurl}= 	http://yamlmanager:8001/
		${yamlfile}=		Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.yaml
	END
	GROUP 	Run Agent with Yaml configuration file
		Run Agent CLI 	-g  2  --ini  ${yamlfile}
	END
	Sleep 	20s
	Stop Agent
	GROUP 	Check if Agent log file contains Manager url from Yaml file
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	${yamlurl}
	END

	[Teardown]	Stop Agent

Agent Yml Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	GROUP 	Set Test Variables
		VAR 	${yamlurl}= 	http://ymlmanager:8003/
		${yamlfile}= 			Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.yml
	END
	GROUP 	Run Agent with Yml configuration file
	Run Agent CLI 	-g  2  --ini  ${yamlfile}
	END
	Sleep 	20s
	Stop Agent
	GROUP 	Check if Agent log file contains Manager url from Yml file
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	${yamlurl}
	END

	[Teardown]	Stop Agent

Agent JSON Configuration File
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #172

	GROUP 	Set Test Variables
		VAR 	${jsonurl}= 	http://jsonmanager:8002/
		${jsonfile}= 			Normalize Path	${CURDIR}${/}testdata${/}Issue-#172${/}agent-config.json
	END
	GROUP 	Run Agent with JSON configuration file
		Run Agent CLI 	-g  2  --ini  ${jsonfile}
	END
	Sleep 	20
	Stop Agent
	GROUP 	Check if Agent log file contains Manager url from JSON file
		${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
		${result_stdout}=	Get File	${stdout_agent_path}
		Should Contain	${result_stdout}	${jsonurl}
	END

	[Teardown]	Stop Agent

Report Test Case Times
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #376
	
	GROUP 	Set Test Variables
		${scenario_dir}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#376${/}Issue376.rfs
	END
	Run Agent with Default Settings
	Run Manager with "${scenario_dir}" and "${results_dir}"
	Wait Until the Agent Connects to the Manager
	Wait For Manager Process
	Stop Agent

	Show Manager Logs
	Show Agent Logs

	GROUP 	Check Manager's result database
		${dbfile}= 	Find Result DB
		${result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary;
		${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
		Should Be True	${result[0][0]} > 0
		Should Be Equal As Numbers	${result[0][0]} 	5

		@{query_result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary;

		Should Be Equal 	${query_result}[0][0] 	RFSwarm Demo Test
		Should Be Equal 	${query_result}[1][0] 	Create Some Files
		Should Be Equal 	${query_result}[2][0] 	List Some Files
		Should Be Equal 	${query_result}[3][0] 	Remove Some Files
		Should Be Equal 	${query_result}[4][0] 	Show the RFS Variables
	END

	[Teardown] 	Stop Agent and Manager
