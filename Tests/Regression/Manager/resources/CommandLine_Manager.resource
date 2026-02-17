*** Settings ***
Documentation 	This resource file contains keywords for Manager command line only.

Resource 	../../../Common/Common.resource
Resource 	../../../Common/Directories_and_Files.resource
Resource 	../../../Common/Logs.resource
Resource 	../../../Common/INI_PIP_Data.resource
Resource 	../../../Common/RFS_Components.resource
Resource 	../../../Common/Database.resource


*** Variables ***
# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun
${global_name} 		${None}
${global_path} 		${None}

*** Keywords ***
Check Agent Is Running
	[Documentation] 	This keyword checks if the agent is running and returns true or false
	${result}= 	Is Process Running		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log 	Is Agent Running: ${result} 	console=True
	Should Be True 	${result}

Set Global Filename And Default Save Path
	[Documentation]	Sets global default save path as Test Variable and file name for robot test.
	...    You can also provide optional save path.
	[Arguments]		${input_name}	${optional_path}=${None}

	Create Manager INI File If It Does Not Exist
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

Verify Data in Database From Runned Test With ${log_level} Log Level
	[Documentation] 	Keyword for "Verify Data in Database From Runned Tests With Different Log Levels" Test Case.
	${testfolder}= 	Normalize Path 	${CURDIR}${/}..${/}testdata${/}Issue-#216
	VAR 	${scenariofile} 	${testfolder}${/}${log_level}_scenario.rfs
	VAR 	@{mngr_options} 	-n  -s  ${scenariofile}  -d  ${RESULTS_DIR}

	Run Agent CLI
	Run Manager CLI 	@{mngr_options}
	Wait For Manager Process

	${dbfile}= 	Find Result DB 	result_pattern=*_${log_level}_*
	${result}= 	Query Result DB 	${dbfile} 	Select * from Summary;
	Log 	${result}
	Should Be True 	len(${result[0]}) > 0
	Should Be Equal 	${result[0][0]} 	This is a ${log_level} keyword.

	@{run_result_dirs}= 	List Directories In Directory 	${RESULTS_DIR} 	pattern=*_${log_level}_* 	absolute=${True}
	@{logs_dir}= 	List Directories In Directory 	${run_result_dirs}[-1] 	absolute=${True}
	@{run_logs}= 	List Directories In Directory 	${logs_dir}[0]
	${logs_num}= 	Get Length 	${run_logs}
	Should Be True 	${logs_num} > 0

	[Teardown]	Run Keywords
	...    Stop Agent CLI 		AND
	...    Stop Manager CLI 	AND
	...    Check Logs 	Manager 	AND
	...    Check Logs 	Agent
