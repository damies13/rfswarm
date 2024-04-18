*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library 	Collections

*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm
${pyfile_agent} 		${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${pyfile_manager} 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process_agent} 		None
${process_manager} 	None

# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun
# ${results_dir} 			${EXECDIR}${/}rfswarm_manager${/}results
# ${results_dir} 			${TEMPDIR}${/}rfswarm_manager${/}results
${results_dir} 			${OUTPUT DIR}${/}results
*** Keywords ***

Show Log
	[Arguments]		${filename}
	Log to console 	${\n}-----${filename}-----
	${filedata}= 	Get File 	${filename}
	Log to console 	${filedata}
	Log to console 	-----${filename}-----${\n}

Run Agent
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	${process}= 	Start Process 	${cmd_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Run Manager CLI
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	Create Directory 	${results_dir}
	Append To List 	${options} 	-d 	${results_dir}
	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	${process}= 	Start Process 	${cmd_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}
	Sleep	5

Wait For Manager
	[Arguments]		${timeout}=10min
	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=kill
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Stop Manager
	${result}= 	Terminate Process		${process_manager}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	Terminate Process returned: ${result.rc}

Stop Agent
	${result}= 	Terminate Process		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	Terminate Process returned: ${result.rc}

Find Result DB
	# ${fols}= 	List Directory 	${results_dir}
	# Log to console 	${fols}
	${fols}= 	List Directory 	${results_dir} 	*_* 	absolute=True
	Log to console 	${fols}
	# ${files}= 	List Directory 	${fols[0]}
	# Log to console 	${files}
	${file}= 	List Directory 	${fols[-1]} 	*.db 	absolute=True
	Log to console 	Result DB: ${file[-1]}
	RETURN 	${file[-1]}

Query Result DB
	[Arguments]		${dbfile} 	${sql}
	Log to console 	dbfile: ${dbfile}
	${dbfile}= 	Replace String 	${dbfile} 	${/} 	/
	# Log to console 	\${dbfile}: ${dbfile}
	Connect To Database Using Custom Params 	sqlite3 	database="${dbfile}", isolation_level=None
	Log to console 	sql: ${sql}
	${result}= 	Query 	${sql}
	Log to console 	sql result: ${result}
	Disconnect From Database
	RETURN 	${result}

Get Modules From Program .py File That Are Not BuildIn
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	[Arguments]		${file_path}	${last_line_number_of_notbuildin}
	${manager_content}	Get File	${file_path}
	${manager_content_lines}	Split String	${manager_content}	separator=\n
	
	${j}	Set Variable	${0}
	${j_old}	Set Variable	${0}
	FOR  ${i}  IN RANGE  0  ${last_line_number_of_notbuildin}
		${j_old}	Set Variable	${j}
		${j}	Get Index From List	${manager_content_lines}	start=${j + 1}		value= 
	END
	${custom_imports_lines}	Set Variable	${manager_content_lines}[${j_old + 1}:${j}]
	Log	${custom_imports_lines}
	
	${imports}	Create List
	${length}	Get Length	${custom_imports_lines}
	FOR  ${i}  IN RANGE  0  ${length}
		@{custom_imports_elements}	Create List
		FOR  ${x}  IN  ${custom_imports_lines}[${i}]
			@{list}	Split String	${x}
			FOR  ${j}  IN  @{list}
				Append To List	${custom_imports_elements}	${j}
			END
		END

		${length2}	Get Length	${custom_imports_elements}
		FOR  ${j}  IN RANGE  0  ${length2}
			IF  '${custom_imports_elements}[${j}]' == 'import' or '${custom_imports_elements}[${j}]' == 'from'
				${module_name}	Split String	${custom_imports_elements}[${j + 1}]	separator=.
				Append To List	${imports}	${module_name}[0]
				BREAK
			END
		END
	END
	
	RETURN	${imports}

Get Install Requires From Setup File
	[Arguments]		${file_path}
	${setup_content}	Get File	${file_path}
	${setup_content_lines}	Split String	${setup_content}	separator=\n
	FOR  ${line}  IN  @{setup_content_lines}
		# There is probably better solution for this:
		${setup_content_elements}	Split String	${line}	separator=s=
		TRY
			IF  '${setup_content_elements}[0]' == '\tinstall_require'
				${install_requires}	Set Variable	${setup_content_elements}[1][2:-3]
				${install_requires}	Split String	${install_requires}	separator=', '

				${refactored_requires}	Create List
				FOR  ${items}  IN  @{install_requires}
					@{sliced_times}		Create List
					@{sliced_times1}	Split String	${items}	separator=>=
					Append To List	${sliced_times}		@{sliced_times1}
					@{sliced_times2}	Split String	${items}	separator=-
					Append To List	${sliced_times}		@{sliced_times2}
					
					FOR  ${i}  IN   @{sliced_times}
						Append To List	${refactored_requires}	${i}

					END
				END

				BREAK
			END
		EXCEPT
			No Operation
		END
	END

	RETURN	${refactored_requires}

#
