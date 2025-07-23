*** Settings ***
Documentation 	
...    This resource file contains the basic keywords for all components that are run in the command line. 
...    Run "Basic Suite Initialization ${component}" keyword to set the basic suite configuration.

Library 	OperatingSystem
Library 	Process
Library 	String
Library 	Collections
Library 	DateTime

Library 	ini_file.py
Library 	get_ip_address.py
Library 	img_common.py

*** Variables ***
${COMPONENT} 		${None} 	# currently used rfswarm component (app)
${PLATFORM} 		${None}
${RESULTS_DIR} 		${None}
${AGENT_DIR} 		${OUTPUT DIR}${/}rfswarm-agent

*** Keywords ***
Basic Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the basic configuration for suite. The component must be chosen between: Manager, Reporter, Agent
	VAR 	${COMPONENT} 	${component} 	scope=SUITE
	Set Platform

	VAR 	${RESULTS_DIR} 		${OUTPUT DIR}${/}results 	scope=SUITE
	${status}= 	Run Keyword And Return Status 	Directory Should Exist 	${RESULTS_DIR}
	IF 	not ${status}
		Create Directory 	${RESULTS_DIR}
	END

	Log 	\t[ === Basic suite configuration has been initiated for ${COMPONENT} === ] 	console=True
	Log 	component = ${COMPONENT} 	console=True
	Log 	platform = ${PLATFORM} 	console=True
	Log 	results dir = ${RESULTS_DIR} 	console=True
	Log 	------------------------------------------------------------------------------\n\n\n 	console=True

Set Platform
	Set Platform By Python
	Set Platform By Tag

Set Platform By Python
	${system}= 		Evaluate 	platform.system() 	modules=platform

	IF 	"${system}" == "Darwin"
		VAR    ${PLATFORM}    macos    scope=SUITE
	END
	IF 	"${system}" == "Windows"
		VAR    ${PLATFORM}    windows    scope=SUITE
	END
	IF 	"${system}" == "Linux"
		VAR    ${PLATFORM}    ubuntu    scope=SUITE
	END

Set Platform By Tag
	Log 	${OPTIONS}
	Log 	${OPTIONS}[include]
	${inclen}= 	Get Length 	${OPTIONS}[include]
	IF 	${inclen} > 0
		Log 	${OPTIONS}[include][0]
		VAR 	${ostag} 	${OPTIONS}[include][0]

		IF 	"${ostag}" == "macos-latest"
			VAR    ${PLATFORM}    macos    scope=SUITE
		END
		IF 	"${ostag}" == "windows-latest"
			VAR    ${PLATFORM}    windows    scope=SUITE
		END
		IF 	"${ostag}" == "ubuntu-latest"
			VAR    ${PLATFORM}    ubuntu    scope=SUITE
		END
	END

Utilisation Stats
	${cpupct}= 	Evaluate 	psutil.cpu_percent(interval=1, percpu=True) 									modules=psutil
	Log 	\n${cpupct} 	console=True
	${loadavg}= 	Evaluate 	psutil.getloadavg() 														modules=psutil
	Log 	${loadavg} 	console=True
	${mem}= 		Evaluate 	psutil.virtual_memory() 													modules=psutil
	Log 	${mem}
	${proc}= 		Evaluate 	list(psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username'])) 	modules=psutil
	Log 	${proc}

Make Clipboard Not None
	Evaluate 	clipboard.copy("You should never see this after copy") 	modules=clipboard

Change ${str1} With ${str2} In ${file}
	${file_content}	Get File	${file}
	Remove File		${file}
	${file_content}	Replace String	${file_content}	${str1}	${str2}
	Create File		${file}	${file_content}

Get Python Version Info
	${vinfo}= 	Evaluate 	sys.version_info 	modules=sys
	RETURN		${vinfo}

Diff Lists
	[Arguments] 	${list_a} 		${list_b} 	${message}

	${status}= 	Run Keyword And Return Status 	Lists Should Be Equal 	${list_a} 	${list_b}
	IF 	not ${status}
		Log		${list_a}
		Log		${list_b}
		${Missing_List_From_A}= 	Create List
		${Missing_List_From_B}= 	Create List

		FOR 	${item} 	IN 		@{list_b}
			${status}= 	Run Keyword And Return Status 	List Should Contain Value 	${list_a} 	${item}
			IF 	not ${status}
				Append To List 	${Missing_List_From_A} 	${item}
			END
		END

		FOR 	${item} 	IN 		@{list_a}
			${status}= 	Run Keyword And Return Status 	List Should Contain Value 	${list_b} 	${item}
			IF 	not ${status}
				Append To List 	${Missing_List_From_B} 	${item}
			END
		END
		Log 		\nItems from list B missing from list A: ${Missing_List_From_A} 	console=True
		Log 		Items from list A missing from list B: ${Missing_List_From_B} 	console=True
		Lists Should Be Equal 	${list_a} 	${list_b} 		msg=${message}
	END

Kill If Still Running
	[Documentation] 	Provide command name, for example: rfswarm-agent
	[Arguments]		${cmd_name}
	${processes}= 	Evaluate 	list(psutil.process_iter()) 	modules=psutil
	# Log 	${processes}
	FOR 	${p} 	IN 	@{processes}
		TRY
			IF 	$cmd_name in $p.name()
				Evaluate 	$p.kill()
			END
		EXCEPT 	# Match any error.
			Log 	Failed to kill process: ${cmd_name}
		END
	END

# End ${component_name} If Still Running
# 	${comp} 	Convert To Lower Case 	${component_name}

# 	${result}= 	Wait For Process 	${PROCESS_${comp}} 	timeout=60
# 	${running}= 	Is Process Running 	${PROCESS_${comp}}
# 	IF 	not ${running}
# 		Should Be Equal As Integers 	${result.rc} 	0
# 		Check Logs
# 	ELSE
# 		Take A Screenshot
# 		${result} = 	Terminate Process		${PROCESS_${comp}}
# 		# Should Be Equal As Integers 	${result.rc} 	0
# 		Check Logs
# 		Fail 	Had to Terminate Process
# 	END

# # # # # # # # #
# System date:  #
# # # # # # # # #

Resync Date With Time Server
	[Arguments] 	${old_date}
	IF 	"${PLATFORM}" == "macos"
		${result}= 	Run Process 	sudo  systemsetup  -setusingnetworktime  on
		Log 	${result.stdout}
		Log 	${result.stderr}
		${result}= 	Run Process 	sudo  systemsetup  -setnetworktimeserver  time.apple.com
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	date  +%Y-%m-%d
		Should Not Be Equal As Strings 	${result.stdout} 	${old_date}
		Log 	Back to original date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END
	IF 	"${PLATFORM}" == "windows"
		${result}= 	Run Process 	powershell.exe  w32tm  /resync 	shell=${True}
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	powershell.exe  Get-Date  -Format  'yyyy-MM-dd' 	shell=${True}
		Should Not Be Equal As Strings 	${result.stdout} 	${old_date}
		Log 	Back to original date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END
	IF 	"${PLATFORM}" == "ubuntu"
		${result}= 	Run Process 	sudo  hwclock  --systohc
		Log 	${result.stdout}
		Log 	${result.stderr}
		${result}= 	Run Process 	sudo  timedatectl  set-ntp  true
		Log 	${result.stdout}
		Log 	${result.stderr}
		${result}= 	Run Process 	sudo  ntpdate  -u  time.google.com
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	date  +%Y-%m-%d
		Should Not Be Equal As Strings 	${result.stdout} 	${old_date}
		Log 	Back to original date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END

Set Date Manually
	[Arguments] 	${input_date}
	IF 	"${PLATFORM}" == "macos"
		${result}= 	Run Process 	sudo  date  -f  '%Y-%m-%d'  '${input_date}'
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	date  +%Y-%m-%d
		Should Be Equal As Strings 	${result.stdout} 	${input_date}
		Log 	New date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END
	IF 	"${PLATFORM}" == "windows"
		${result}= 	Run Process 	powershell.exe  Set-Date  -Date  (Get-Date '${input_date}' -Format 'yyyy-MM-dd') 	shell=${True}
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	powershell.exe  Get-Date  -Format  'yyyy-MM-dd' 	shell=${True}
		Should Be Equal As Strings 	${result.stdout} 	${input_date}
		Log 	New date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END
	IF 	"${PLATFORM}" == "ubuntu"
		${result}= 	Run Process 	sudo  timedatectl  set-ntp  false
		Log 	${result.stdout}
		Log 	${result.stderr}
		${input_date_epoch}= 	Convert Date 	${input_date} 	date_format=%Y-%m-%d 	result_format=epoch
		${input_date_epoch}= 	Convert To Integer 	${input_date_epoch}
		${result}= 	Run Process 	sudo  date  +%s  -s  @${input_date_epoch}
		Log 	${result.stdout}
		Log 	${result.stderr}
		# ${result}= 	Run Process 	sudo  date  -s  ${input_date}  +%Y-%m-%d
		# Log 	${result.stdout}
		# Log 	${result.stderr}

		${result}= 	Run Process 	date  +%Y-%m-%d
		Should Be Equal As Strings 	${result.stdout} 	${input_date}
		Log 	New date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END

