*** Settings ***
Library 	OperatingSystem
Library 	Process

*** Variables ***

${pyfile_agent} 		${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${pyfile_manager} 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process_agent} 		None
${process_manager} 	None


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
	${process}= 	Start Process 	python3 	${pyfile_agent}  ${options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Run Manager CLI
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	Log to console 	\${options}: ${options}
	${process}= 	Start Process 	python3 	${pyfile_manager}  ${options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}

Wait For Manager
	${result}= 	Wait For Process		${process_manager}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Stop Manager
	${result}= 	Terminate Process		${process_manager}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Stop Agent
	${result}= 	Terminate Process		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}
