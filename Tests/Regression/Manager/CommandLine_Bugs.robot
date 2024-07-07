*** Settings ***
Resource 	CommandLine_Common.robot

*** Test Cases ***
Robbot files with same name but different folders
	[Tags]	ubuntu-latest		windows-latest		macos-latest 	Issue #184
	Log To Console 	${\n}TAGS: ${TEST TAGS}
	@{agnt_options}= 	Create List 	-g 	1 	-m 	http://localhost:8138
	Run Agent 	${agnt_options}
	Sleep    1s
	Check Agent Is Running
	Log to console 	${CURDIR}
	${scenariofile}= 	Normalize Path 	${CURDIR}${/}testdata${/}Issue-#184${/}Issue-#184.rfs
	Log to console 	${scenariofile}
	@{mngr_options}= 	Create List 	-g 	1 	-s 	${scenariofile} 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${OUTPUT DIR}${/}stdout_agent.txt 		Robot returned an error
	Should Not Contain 	${OUTPUT DIR}${/}stdout_agent.txt 		please check the log file

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
	@{mngr_options}= 	Create List 	-i 	${testdata}${/}manager.ini 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${OUTPUT DIR}${/}stdout_manager.txt 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${OUTPUT DIR}${/}stderr_manager.txt 		OSError: [Errno 24] Too many open files

	Should Not Contain 	${OUTPUT DIR}${/}stdout_agent.txt 		Manager Disconnected

	@{testdata-dir}= 	List Directory 		${testdata}${/}agent-dir
	Log 	testdata-dir: ${testdata-dir} 		console=True
	@{agent-dir}= 	List Directory 		${testdata}${/}agent-dir
	Log 	agent-dir: ${agent-dir} 		console=True
	@{scripts-dir}= 	List Directory 		${testdata}${/}agent-dir${/}scripts
	Log 	scripts-dir: ${scripts-dir} 		console=True

	@{result_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}agent-dir${/}scripts${/}resources 	*.resource

	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager


Lots Of Resource Files
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #261
	VAR    ${testdata} 		${CURDIR}${/}testdata${/}Issue-#261${/}lotsa_files_test      scope=TEST
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
	@{mngr_options}= 	Create List 	-i 	${testdata}${/}manager.ini 	-n
	Run Manager CLI 	${mngr_options}
	Wait For Manager
	Stop Agent
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

	Should Not Contain 	${OUTPUT DIR}${/}stdout_manager.txt 		OSError: [Errno 24] Too many open files
	Should Not Contain 	${OUTPUT DIR}${/}stderr_manager.txt 		OSError: [Errno 24] Too many open files

	Should Not Contain 	${OUTPUT DIR}${/}stdout_agent.txt 		Manager Disconnected

	@{result_files}= 	List Files In Directory And Sub Directories 	${testdata}${/}agent-dir${/}scripts${/}resources 	*.resource

	Diff Lists    ${expected_files}    ${result_files}    Agent didn't get all files from manager

	[Teardown]	Run Keywords
	...    Stop Agent	AND
	...    Stop Manager
