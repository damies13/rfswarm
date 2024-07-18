*** Settings ***
Resource 	CommandLine_Common.robot

*** Test Cases ***
Environment Variable Substitution in Robot/Resource files
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #165
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	@{agnt_options}= 	Create List 	-g 	1 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}

	@{expected_files}= 	List Files In Directory And Sub Directories 	${CURDIR}${/}testdata${/}Issue-#165

	Set Environment Variable 		RF_DIRECTORY 			${CURDIR}${/}testdata${/}Issue-#165${/}rf_dir
	Set Environment Variable 		RF_MAGICNUM 			Thirteen

	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#165${/}Issue-#165.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	# Should Contain 	${stdout_agent} 		Thirteen

	Should Not Contain 	${stdout_agent} 		Robot returned an error
	Should Not Contain 	${stderr_agent} 		Robot returned an error
	Should Not Contain 	${stdout_agent} 		please check the log file
	Should Not Contain 	${stderr_agent} 		please check the log file

	@{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts

	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager


	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager
