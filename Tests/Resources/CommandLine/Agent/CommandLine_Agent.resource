*** Settings ***
Documentation 	This resource file contains keywords for Agent command line only.

Resource 	../../../Common/Common.resource
Resource 	../../../Common/Directories_and_Files.resource
Resource 	../../../Common/INI_PIP_Data.resource
Resource 	../../../Common/Logs.resource
Resource 	../../../Common/RFS_Components.resource
Resource 	../../../Common/Database.resource

Library 	HttpCtrl.Server
Library 	XML


*** Keywords ***
Test Agent Connectivity
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method} 	GET
	Should Be Equal 	${url}		/

	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method}	POST

Ensure Agent is running and then terminate
	[Documentation] 	Terminates Agent if running. If not fail.
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		${result}= 	Terminate Process		${process_agent}
	ELSE
		Fail	msg=Agest is not running!
	END

Reset Agent INI file
	${agent_src_folder}= 	Get Agent Default Save Path
	Remove File 	${agent_src_folder}${/}RFSwarmAgent.ini
	Run Agent CLI
	Sleep 	2
	Stop Agent CLI

Remove Agent INI file
	${agent_src_folder}=	Get Agent Default Save Path
	Remove File				${agent_src_folder}${/}RFSwarmAgent.ini
	File Should Not Exist	${agent_src_folder}${/}RFSwarmAgent.ini

Check if Agent INI file is not empty
	${agent_src_folder}= 		Get Agent Default Save Path
	File Should Exist 			${agent_src_folder}${/}RFSwarmAgent.ini
	File Should Not Be Empty 	${agent_src_folder}${/}RFSwarmAgent.ini

Replace Agent INI File
	[Documentation] 	Replaces current Agent INI file with file specified with \${file_path} argument
	[Arguments] 	${file_path}
	${agent_src_folder}= 	Get Agent Default Save Path
	${v1_0_0_inifile}= 	Normalize Path 	${file_path}
	Copy File 	${v1_0_0_inifile} 	${agent_src_folder}
	File Should Exist 		${agent_src_folder}${/}RFSwarmAgent.ini
	File Should Not Be Empty 	${agent_src_folder}${/}RFSwarmAgent.ini

Get XML Files From Last Run
	[Arguments] 	${result_pattern} 	${path}=${RESULTSDIR}
	${dbfile}= 	Find Result DB 		directory=${path} 	result_pattern=${result_pattern}
	${dbpath} 	${dbfilename}= 	Split Path 	${dbfile}

	@{logdirs}= 	List Directories In Directory 	${dbpath}${/}logs
	Log  	logdirs: ${logdirs}

	VAR 	@{xmlfiles}

	FOR  ${logdir}  IN  @{logdirs}
		VAR 	${logdir_path} 		${dbpath}${/}logs${/}${logdirs}[0]
		@{xmlfiles_single}= 	List Files In Directory
		...    ${logdir_path}
		...    *.xml
		...    absolute=${True}

		Append To List 	${xmlfiles} 	@{xmlfiles_single}
	END

	Log  	xmlfiles: ${xmlfiles}

	RETURN 	${xmlfiles}

#
