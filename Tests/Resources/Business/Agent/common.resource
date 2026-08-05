*** Settings ***
Documentation    Resource file for business level keywords for Agent test cases
...    All Manager keywords are running in no GUI mode
Resource    ../../CommandLine/Agent/CommandLine_Agent.resource

*** Keywords ***
Run Agent with Default Settings
	[Arguments] 	${debug_lvl}=1
	VAR 	${url} 	http://localhost:8138
	VAR 	@{agnt_options}= 	-g  ${debug_lvl}  -m  ${url}
	Run Agent CLI 	@{agnt_options}

Run Agent with Custom Name
	[Arguments] 	${agent_name}  ${debug_lvl}=1
	VAR 	@{agnt_options} 	-g  ${debug_lvl}  -a  ${agent_name}
	Run Agent CLI 	@{agnt_options}

Run Agent with Custom INI File
	[Arguments] 	${ini_file}  ${debug_lvl}=1
	VAR 	@{agnt_options} 	-g  ${debug_lvl}  -i  ${ini_file}
	Run Agent CLI 	@{agnt_options}

Stop Agent
	Stop Agent CLI

Run Manager with Default Settings
	[Arguments] 	${debug_lvl}=1
	VAR 	@{mngr_options} 	-n  -g  ${debug_lvl}
	Run Manager CLI 	@{mngr_options}

Run Manager with "${scenario_path}" and "${results_path}"
	[Arguments] 	${debug_lvl}=1
	VAR 	@{mngr_options}= 	-n  -g  ${debug_lvl}  -s  ${scenario_path}  -d  ${results_path}
	Run Manager CLI 	@{mngr_options}

Run Manager with Custom Result Directory
	[Arguments] 	${results_dir}  ${debug_lvl}=1
	VAR 	@{mngr_options}= 	-n  -g  ${debug_lvl}  -d  ${results_dir}
	Run Manager CLI 	@{mngr_options}

Stop Manager
	Stop Manager CLI

Stop Agent and Manager
	Stop Agent CLI
	Stop Manager CLI

Start Manager Mock Server
	Start Server	127.0.0.1	8138

Show Test Information
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	Log to console 	${CURDIR}

Show Manager Logs
	${stdout_manager_path} 	${stderr_manager_path} 	Find Log 	Manager
	Show Log 	${stdout_manager_path}
	Show Log 	${stderr_manager_path}

Show Agent Logs
	${stdout_agent_path} 	${stderr_agent_path} 	Find Log 	Agent
	Show Log 	${stdout_agent_path}
	Show Log 	${stderr_agent_path}

Check ${component} Logs
	Check Logs 	${component}
