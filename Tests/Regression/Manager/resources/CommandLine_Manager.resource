*** Settings ***
Documentation 	This resource file contains keywords for Manager command line only.

Resource 	../../../Common/Common.resource

*** Variables ***
# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun
${global_name} 		${None}
${global_path} 		${None}

*** Keywords ***
# Run Agent
# 	[Arguments]		${options}=None
# 	IF  ${options} == None
# 		${options}= 	Create List
# 	END
# 	Append To List 	${options} 	-d 	${agent_dir}
# 	Create Directory 	${agent_dir}
# 	Empty Directory 	${agent_dir}

# 	Log to console 	${\n}\${options}: ${options}
# 	# ${process}= 	Start Process 	python3 	${pyfile_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
# 	${process}= 	Start Process 	${cmd_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
# 	Set Test Variable 	$process_agent 	${process}

# Run Manager CLI
# 	[Arguments]		${options}=None
# 	IF  ${options} == None
# 		${options}= 	Create List
# 		Create Directory 	${RESULTS_DIR}
# 		Append To List 	${options} 	-d 	${RESULTS_DIR}
# 	END
# 	Log to console 	${\n}\${options}: ${options}
# 	# ${process}= 	Start Process 	python3 	${pyfile_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
# 	${process}= 	Start Process 	${cmd_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
# 	Set Test Variable 	$process_manager 	${process}

# Wait For Manager
# 	[Arguments]		${timeout}=30min
# 	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=terminate
# 	# Should Be Equal As Integers 	${result.rc} 	0
# 	# Log to console 	Manager exited with: ${result.rc}

# 	TRY
# 		Log 	Manager exited with: ${result.rc} 		console=true

# 		Copy File 	${result.stdout_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stdout_manager.txt
# 		Copy File 	${result.stderr_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stderr_manager.txt

# 		Log 	stdout_path: ${result.stdout_path} 	console=True
# 		Log 	stdout: ${result.stdout} 	console=True
# 		Log 	stderr_path: ${result.stderr_path} 	console=True
# 		Log 	stderr: ${result.stderr} 	console=True
# 	EXCEPT 	AS 	${error}
# 		Log 	error: ${error} 		console=true
# 	END

Check Agent Is Running
	[Documentation] 	This keyword checks if the agent is running and returns true or false
	${result}= 	Is Process Running		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log 	Is Agent Running: ${result} 	console=True
	Should Be True 	${result}

# Stop Manager
# 	${running}= 	Is Process Running 	${process_manager}
# 	IF 	${running}
# 		Sleep	3s
# 		IF  '${PLATFORM}' == 'windows'	# Send Signal To Process keyword does not work on Windows
# 			${result}= 	Terminate Process		${process_manager}
# 		ELSE
# 			Send Signal To Process 	SIGINT 	${process_manager}
# 			${result}= 	Wait For Process 	${process_manager}	timeout=30	on_timeout=kill
# 		END
# 	ELSE
# 		TRY
# 			# get result var for process even if not running any more
# 			${result}= 	Get Process Result		${process_manager}
# 		EXCEPT 	AS 	${error}
# 			Log 	error: ${error} 		console=true
# 		END
# 	END

# 	TRY
# 		Copy File 	${result.stdout_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stdout_manager.txt
# 		Copy File 	${result.stderr_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stderr_manager.txt

# 		Log to console 	Terminate Manager Process returned: ${result.rc} 	console=True
# 		Log 	stdout_path: ${result.stdout_path} 	console=True
# 		Log 	stdout: ${result.stdout} 	console=True
# 		Log 	stderr_path: ${result.stderr_path} 	console=True
# 		Log 	stderr: ${result.stderr} 	console=True
# 	EXCEPT 	AS 	${error}
# 		Log 	error: ${error} 		console=true
# 	END

# Stop Agent
# 	${running}= 	Is Process Running 	${process_agent}
# 	IF 	${running}
# 		Sleep	3s
# 		IF  '${PLATFORM}' == 'windows'	# Send Signal To Process keyword does not work on Windows
# 			${result} = 	Terminate Process		${process_agent}
# 		ELSE
# 			Send Signal To Process 	SIGINT 	${process_agent}
# 			${result}= 	Wait For Process 	${process_agent}	timeout=30	on_timeout=kill
# 		END
# 	ELSE
# 		TRY
# 			# get result var for process even if not running any more
# 			${result}= 	Get Process Result		${process_agent}
# 		EXCEPT 	AS 	${error}
# 			Log 	error: ${error} 		console=true
# 		END
# 	END

# 	TRY
# 		Copy File 	${result.stdout_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stdout_agent.txt
# 		Copy File 	${result.stderr_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stderr_agent.txt

# 		Log to console 	Agent returned: ${result.rc}
# 		Log 	stdout_path: ${result.stdout_path} 	console=True
# 		Log 	stdout: ${result.stdout} 	console=True
# 		Log 	stderr_path: ${result.stderr_path} 	console=True
# 		Log 	stderr: ${result.stderr} 	console=True
# 		Show Dir Contents 	${agent_dir}
# 	EXCEPT 	AS 	${error}
# 		Log 	error: ${error} 		console=true
# 	END

Set Global Filename And Default Save Path
	[Documentation]	Sets global default save path as Test Variable and file name for robot test.
	...    You can also provide optional save path.
	[Arguments]		${input_name}	${optional_path}=${None}

	Set Test Variable	${global_name}	${input_name}
	${location}=	Get Manager Default Save Path
	Set Test Variable	${global_path}	${location}

	Set Test Variable 	$file_name 	${global_name}
	IF  '${optional_path}' != '${None}'
		Change Manager INI Option 	Plan 	scriptdir 		${optional_path}
		Change Manager INI Option 	Plan 	scenariodir 	${optional_path}
	END

	Log 	${global_name}
	Log 	${global_path}

Create Testdata Agent INI
	[Arguments] 	${inifile} 	${testdata}
	Create File 	${inifile} 	[Agent]\n
	Append To File 	${inifile} 	agentname = E-5CG2026KN2\n
	Append To File 	${inifile} 	agentdir = ${testdata}${/}agent-dir\n
	Append To File 	${inifile} 	xmlmode = False\n
	Append To File 	${inifile} 	excludelibraries = BuiltIn,String,OperatingSystem,perftest\n
	Append To File 	${inifile} 	properties =\n
	Append To File 	${inifile} 	swarmmanager = http://localhost:8138/\n
	Append To File 	${inifile} 	robotcmd = robot\n

Create Testdata Manager INI
	[Arguments] 	${inifile} 	${testdata}

	Create File 	${inifile} 	[GUI]\n
	Append To File 	${inifile} 	win_width = 1280\n
	Append To File 	${inifile} 	win_height = 720\n
	Append To File 	${inifile} 	graph_list = \n
	Append To File 	${inifile} 	\n
	Append To File 	${inifile} 	[Plan]\n
	Append To File 	${inifile} 	scriptdir = ${testdata}\n
	Append To File 	${inifile} 	scenariodir = ${testdata}\n
	Append To File 	${inifile} 	scenariofile = ${testdata}${/}scenario.rfs\n
	Append To File 	${inifile} 	\n
	Append To File 	${inifile} 	[Run]\n
	Append To File 	${inifile} 	resultsdir = ${testdata}${/}results\n
	Append To File 	${inifile} 	display_index = False\n
	Append To File 	${inifile} 	display_iteration = False\n
	Append To File 	${inifile} 	display_sequence = False\n
	Append To File 	${inifile} 	display_percentile = 90\n
	Append To File 	${inifile} 	\n
	Append To File 	${inifile} 	[Server]\n
	Append To File 	${inifile} 	bindip = \n
	Append To File 	${inifile} 	bindport = 8138\n
	Append To File 	${inifile} 	\n
