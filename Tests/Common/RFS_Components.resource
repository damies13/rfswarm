*** Settings ***
Resource 	Common.resource

Resource 	Directories_and_Files.resource
Resource 	INI_PIP_Data.resource
Resource 	Logs.resource

*** Variables ***
${CMD_AGENT} 		rfswarm-agent
${CMD_MANAGER} 		rfswarm-manager
${CMD_REPORTER} 	rfswarm-reporter

${PROCESS_AGENT} 		${None}
${PROCESS_MANAGER} 		${None}
${PROCESS_REPORTER} 	${None}

${PYFILE_MANAGER} 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${PYFILE_AGENT} 	${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${PYFILE_REPORTER} 	${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

*** Keywords ***
# # # # # # # # # # # # #
# Open/Close component  #
# # # # # # # # # # # # #

Run ${component_name} CLI
	[Documentation] 	Open one of the RFSwarm applications for CLI purposes. Pass the: Manager, Reporter or Agent
	[Arguments] 	@{appargs}  ${noargs}=${False}  ${envargs}=${None}
	${comp} 	Convert To Lower Case 	${component_name}
	${len} 		Get Length 	${appargs}

	IF  ${noargs} == ${False}
		IF  '${component_name}' == 'Manager' and ${len} == ${0} #( '-d' not in ${appargs} and '--dir' not in ${appargs} )
			Append To List 	${appargs} 	-d 	${RESULTS_DIR}
		ELSE IF  '${component_name}' == 'Manager' and ${len} != ${0} and ( '-d' not in ${appargs} and '--dir' not in ${appargs} )
			Create Manager INI File If It Does Not Exist
			Change Manager INI Option 	Run 	resultsdir 	${RESULTS_DIR}
		ELSE IF  '${component_name}' == 'Agent' and ( '-d' not in ${appargs} and '--agentdir' not in ${appargs} )
			Append To List 	${appargs} 	-d 	${AGENT_DIR}
			Create Directory 	${AGENT_DIR}
			Empty Directory 	${AGENT_DIR}
		END
	END

	Log 	${\n}Starting ${component_name} ... 	console=${True}
	${args}= 	Evaluate 	" ".join(@{appargs})
	Log 	\t\${args}: ${args} 	console=${True}

	${tname} 		Convert To Save Path 	${TEST NAME}
	Create Directory 	${OUTPUT DIR}${/}stdout${/}${tname}${/}
	Create File 		${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt
	Create File 		${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt
	${process}= 	Start Process 	${CMD_${comp}}  @{appargs}  alias=${component_name}
	...    stdout=${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt  stderr=${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt
	...    env=${envargs}

	Log 	${process}
	VAR 	${PROCESS_${comp}} 		${process} 	scope=SUITE

	${result}= 	Wait Until Keyword Succeeds 	45sec 	500ms 	Process Should Be Running 	${process}

	${running}= 	Is Process Running 	${PROCESS_${comp}}
	IF 	not ${running}
		${result}= 	Get Process Result 	${PROCESS_${comp}}

		Log		rc: ${result.rc} 		console=True
		Log		stdout_path: ${result.stdout_path} 		console=True
		Log		stderr_path: ${result.stderr_path} 		console=True

		Show Log 	${result.stdout_path}
		Show Log 	${result.stderr_path}

		Fail 		${component_name} didn't start!

	END

	Log 	*=== ${component_name} started ===* 	console=${True}

Stop ${component_name} CLI
	[Documentation] 	Closes one of the RFSwarm applications with CLI only. Pass the: Manager, Reporter or Agent
	${comp} 	Convert To Lower Case 	${component_name}

	${running}= 	Is Process Running 	${PROCESS_${comp}}
	IF 	${running}
		Sleep	1s
		IF  '${PLATFORM}' == 'windows'	# Send Signal To Process keyword does not work on Windows
			${result}= 	Terminate Process 	${PROCESS_${comp}}
		ELSE
			Send Signal To Process 	SIGINT 	${PROCESS_${comp}}
			${result}= 	Wait For Process 	${PROCESS_${comp}} 	timeout=30 	on_timeout=kill
		END
	ELSE
		Log 	${component_name} is not running! 	console=${True}
		TRY
			${result}= 	Get Process Result 	${PROCESS_${comp}}
		EXCEPT 	AS 	${error}
			Log 	error: ${error} 		console=true
		END

		RETURN
	END

	Log 	*=== ${component_name} closed with CLI signal ===* 	console=${True}
	TRY
		Log 	${component_name} exited with: ${result.rc} 	console=${True}
		# Should Be Equal As Integers 	${result.rc} 	0

		Log		stdout_path: ${result.stdout_path} 		console=True
		Log		stderr_path: ${result.stderr_path} 		console=True

		Show Log 	${result.stdout_path}
		Show Log 	${result.stderr_path}

	EXCEPT 	AS 	${error}
		Log 	error: ${error} 		console=true

	END

	Sleep 	0.5
	Run Keyword And Ignore Error 	Check Logs 	${component_name} 	# TODO: remove ignore error and check if test cases fail. Log issues for failing test cases
	${running}= 	Is Process Running 	${PROCESS_${comp}}
	Run Keyword If 	${running} 	Fail 	Failed to close ${component_name}

	[Teardown] 	Run Keywords
	...    Set Suite Variable 	${PROCESS_${comp}} 	${None} 	AND 	Kill If Still Running 	${CMD_${comp}}

Wait For ${component_name} Process
	[Documentation] 	Pass the: Manager, Reporter or Agent
	[Arguments] 	${timeout}=30min
	${comp} 	Convert To Lower Case 	${component_name}

	${result}= 	Wait For Process 	${PROCESS_${comp}} 	timeout=${timeout} 	on_timeout=terminate

	TRY
		Log 	${component_name} exited with: ${result.rc} 	console=${True}
		# Should Be Equal As Integers 	${result.rc} 	0

		Log		rc: ${result.rc} 		console=True
		Log		stdout_path: ${result.stdout_path} 		console=True
		Log		stderr_path: ${result.stderr_path} 		console=True

		Show Log 	${result.stdout_path}
		Show Log 	${result.stderr_path}

	EXCEPT 	AS 	${error}
		Log 	error: ${error} 	console=${True}

	END

	Sleep 	0.5
	Run Keyword And Ignore Error 	Check Logs 	${component_name}
