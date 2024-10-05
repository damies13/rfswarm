*** Settings ***
Test Tags       Bugs 	CommandLine

Resource 	CommandLine_Common.robot

Suite Setup 		Create Directory 	${results_dir}

*** Variables ***
@{robot_data}=	example.robot	Example Test Case
${scenario_name}=	test_scenario

*** Test Cases ***
Robot files with same name but different folders
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #184
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	@{agnt_options}= 	Create List 	-g 	1 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#184${/}Issue-#184.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	${stdout_manager}= 		Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${stdout_agent} 		Robot returned an error
	Should Not Contain 	${stderr_agent} 		Robot returned an error
	Should Not Contain 	${stdout_agent} 		please check the log file
	Should Not Contain 	${stderr_agent} 		please check the log file

	${dbfile}= 	Find Result DB
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary;
	Should Be True	${result[0][0]} > 0
	Should Be Equal As Numbers	${result[0][0]} 	4
	${result}= 	Query Result DB 	${dbfile} 	Select count(*) from Summary where _pass > 0;
	Should Be True	${result[0][0]} > 0
	Should Be Equal As Numbers	${result[0][0]} 	4
	${result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary;
	Should Contain 	${result} 	${{ ('Folder A Log Variables AAA',) }}
	Should Contain 	${result} 	${{ ('Folder B Log Variables BBB',) }}
	${result}= 	Query Result DB 	${dbfile} 	Select result_name from Summary where _pass > 0;
	Should Contain 	${result} 	${{ ('Folder A Log Variables AAA',) }}
	Should Contain 	${result} 	${{ ('Folder B Log Variables BBB',) }}

Check If The Not Buildin Modules Are Included In The Manager Setup File
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	${imports}	Get Modules From Program .py File That Are Not BuildIn
	...    ${CURDIR}..${/}..${/}..${/}..${/}rfswarm_manager${/}rfswarm.py

	Log	${imports}

	${requires}	Get Install Requires From Setup File
	...    ${CURDIR}..${/}..${/}..${/}..${/}setup-manager.py

	Log	${requires}

	FOR  ${i}  IN  @{imports}
		Run Keyword And Continue On Failure
		...    Should Contain	${requires}	${i}
		...    msg="Some modules are not in Manager setup file"
	END

Circular Reference Resource Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #261
	VAR    ${testdata} 		${CURDIR}${/}testdata${/}Issue-#261${/}circular_test      scope=TEST
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	Create Testdata Agent INI 	${testdata}${/}agent.ini
	Create Testdata Manager INI 	${testdata}${/}manager.ini

	@{expected_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}resources 	*.resource

	@{agnt_options}= 	Create List 	-i 	${testdata}${/}agent.ini
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#184${/}Issue-#184.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-i 	${testdata}${/}manager.ini 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent

	${stdout_manager}= 		Read Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Read Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Read Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Read Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${stdout_manager} 		RuntimeError
	Should Not Contain 	${stderr_manager} 		RuntimeError
	Should Not Contain 	${stdout_manager} 		Exception
	Should Not Contain 	${stderr_manager} 		Exception

	Should Not Contain 	${stdout_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stderr_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stdout_manager}		OSError
	Should Not Contain 	${stderr_manager} 		OSError
	Should Not Contain 	${stdout_manager} 		Errno 24
	Should Not Contain 	${stderr_manager} 		Errno 24
	Should Not Contain 	${stdout_manager} 		Too many open files
	Should Not Contain 	${stderr_manager} 		Too many open files

	Should Not Contain 	${stdout_agent} 		Manager Disconnected

	# @{testdata-dir}= 	List Directory 		${testdata}
	# Log 	testdata-dir: ${testdata-dir} 		console=True
	# @{agent-dir}= 	List Directory 		${testdata}${/}agent-dir
	# Log 	agent-dir: ${agent-dir} 		console=True
	# @{scripts-dir}= 	List Directory 		${testdata}${/}agent-dir${/}scripts
	# Log 	scripts-dir: ${scripts-dir} 		console=True

	# @{result_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}agent-dir${/}scripts${/}resources 	*.resource
	@{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts${/}resources 	*.resource
	# @{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts 	*.resource


	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Circular Reference Resource Files 2
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #261
	VAR    ${testdata} 		${CURDIR}${/}testdata${/}Issue-#261${/}circular_test2      scope=TEST
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	Create Testdata Agent INI 	${testdata}${/}agent.ini
	Create Testdata Manager INI 	${testdata}${/}manager.ini

	@{expected_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}resources

	@{agnt_options}= 	Create List 	-i 	${testdata}${/}agent.ini
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#184${/}Issue-#184.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-i 	${testdata}${/}manager.ini 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent

	${stdout_manager}= 		Read Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Read Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Read Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Read Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${stdout_manager} 		RuntimeError
	Should Not Contain 	${stderr_manager} 		RuntimeError
	Should Not Contain 	${stdout_manager} 		Exception
	Should Not Contain 	${stderr_manager} 		Exception

	Should Not Contain 	${stdout_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stderr_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stdout_manager}		OSError
	Should Not Contain 	${stderr_manager} 		OSError
	Should Not Contain 	${stdout_manager} 		Errno 24
	Should Not Contain 	${stderr_manager} 		Errno 24
	Should Not Contain 	${stdout_manager} 		Too many open files
	Should Not Contain 	${stderr_manager} 		Too many open files

	Should Not Contain 	${stdout_agent} 		Manager Disconnected

	# @{testdata-dir}= 	List Directory 		${testdata}
	# Log 	testdata-dir: ${testdata-dir} 		console=True
	# @{agent-dir}= 	List Directory 		${testdata}${/}agent-dir
	# Log 	agent-dir: ${agent-dir} 		console=True
	# @{scripts-dir}= 	List Directory 		${testdata}${/}agent-dir${/}scripts
	# Log 	scripts-dir: ${scripts-dir} 		console=True

	# @{result_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}agent-dir${/}scripts${/}resources 	*.resource
	@{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts${/}resources
	# @{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts 	*.resource


	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Lots Of Resource Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #261
	VAR 	${testdata} 		${CURDIR}${/}testdata${/}Issue-#261${/}lotsa_files_test      scope=TEST
	VAR 	${agent_dir} 		${agent_dir}${/}${TEST NAME}      scope=TEST
	Create Testdata Agent INI 	${testdata}${/}agent.ini
	Create Testdata Manager INI 	${testdata}${/}manager.ini

	@{expected_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}resources 	*.resource

	@{agnt_options}= 	Create List 	-i 	${testdata}${/}agent.ini
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#184${/}Issue-#184.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-i 	${testdata}${/}manager.ini 	-n 	-d 	${results_dir}
	Run Manager CLI 	${mngr_options}
	# It can take a while for the agent to download 3500+ files
	Wait For Manager 	60min
	Stop Agent

	${stdout_manager}= 		Read Log 	${OUTPUT DIR}${/}stdout_manager.txt
	${stderr_manager}= 		Read Log 	${OUTPUT DIR}${/}stderr_manager.txt
	${stdout_agent}= 		Read Log 	${OUTPUT DIR}${/}stdout_agent.txt
	${stderr_agent}= 		Read Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${stdout_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stderr_manager} 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${stdout_manager}			OSError
	Should Not Contain 	${stderr_manager} 		OSError
	Should Not Contain 	${stdout_manager} 		Errno 24
	Should Not Contain 	${stderr_manager} 		Errno 24
	Should Not Contain 	${stdout_manager} 		Too many open files
	Should Not Contain 	${stderr_manager} 		Too many open files

	Should Not Contain 	${stdout_agent} 		Manager Disconnected

	# @{testdata-dir}= 	List Directory 		${testdata}
	# Log 	testdata-dir: ${testdata-dir} 		console=True
	# @{agent-dir}= 	List Directory 		${testdata}${/}agent-dir
	# Log 	agent-dir: ${agent-dir} 		console=True
	@{scripts-dir}= 	List Directory 		${agent_dir}${/}scripts
	Log 	scripts-dir: ${scripts-dir}
	@{resources-dir}= 	List Directory 		${agent_dir}${/}scripts${/}resources
	Log 	scripts-dir: ${resources-dir}

	# @{result_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}agent-dir${/}scripts${/}resources 	*.resource
	@{result_files}= 	List Files In Directory And Sub Directories 	${agent_dir}${/}scripts${/}resources 	*.resource

	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager

Verify If Manager Runs With Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	@{mngr_options}		Create List		-n

	${passed} = 	Run Keyword And Return Status 	File Should Exist 	${global_path}${/}RFSwarmManager.ini
	IF 	${passed}
		Show Log 	${global_path}${/}RFSwarmManager.ini
		Remove File 	${global_path}${/}RFSwarmManager.ini
		File Should Not Exist 	${global_path}${/}RFSwarmManager.ini
	END

	Run Manager CLI	${mngr_options}
	${running}= 	Is Process Running		${process_manager}
	IF 	not ${running}
		Fail	msg=Manager is not running!
	END
	Wait Until Created  	${global_path}${/}RFSwarmManager.ini
	Sleep    0.5
	${result} = 	Terminate Process		${process_manager}
	${running}= 	Is Process Running		${process_manager}
	IF 	${running}
		Fail	msg=Manager did not close!
	END
	Log 	${result.stdout}
	Log 	${result.stderr}
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

 	File Should Exist	${global_path}${/}RFSwarmManager.ini
	Show Log 	${global_path}${/}RFSwarmManager.ini
	File Should Not Be Empty	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with existing ini file.
	Run Manager CLI	${mngr_options}
	${running}= 	Is Process Running		${process_manager}
	IF 	not ${running}
		Fail	msg=Manager is not running!
	END
	Sleep    0.5
	${result} = 	Terminate Process		${process_manager}
	${running}= 	Is Process Running		${process_manager}
	IF 	${running}
		Fail	msg=Manager did not close!
	END

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}

Verify If Manager Runs With No Existing INI File From Current Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	@{mngr_options}		Create List		-n
	Remove File		${global_path}${/}RFSwarmManager.ini
	File Should Not Exist	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with no existing ini file.

	Run Manager CLI	${mngr_options}
	${running}= 	Is Process Running		${process_manager}
	IF 	not ${running}
		Fail	msg=Manager is not running!
	END
	${result} = 	Terminate Process		${process_manager}
	${running}= 	Is Process Running		${process_manager}
	IF 	${running}
		Fail	msg=Manager did not close!
	END
	Log 	${result.stdout}
	Log 	${result.stderr}
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}

Verify If Manager Runs With Existing INI File From Previous Version NO GUI
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #49
	[Setup]	Set Global Filename And Default Save Path	${robot_data}[0]

	@{mngr_options}		Create List		-n
	Remove File		${global_path}${/}RFSwarmManager.ini
	File Should Not Exist	${global_path}${/}RFSwarmManager.ini
	${v1_0_0_inifile}=		Normalize Path		${CURDIR}${/}testdata${/}Issue-#49${/}v1_0_0${/}RFSwarmManager.ini
	Copy File	${v1_0_0_inifile}		${global_path}
	File Should Exist	${global_path}${/}RFSwarmManager.ini
	File Should Not Be Empty	${global_path}${/}RFSwarmManager.ini
	Log To Console	Running Manager with existing ini file.

	Run Manager CLI	${mngr_options}
	${running}= 	Is Process Running		${process_manager}
	IF 	not ${running}
		Fail	msg=Manager is not running!
	END
	${result} = 	Terminate Process		${process_manager}
	${running}= 	Is Process Running		${process_manager}
	IF 	${running}
		Fail	msg=Manager did not close!
	END
	Log 	${result.stdout}
	Log 	${result.stderr}
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

	# [Teardown]	Run Keywords
	# ...    Run Keyword		Close Manager GUI ${platform}
