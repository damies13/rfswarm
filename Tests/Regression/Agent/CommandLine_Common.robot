*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library 	Collections
Library 	HttpCtrl.Server

Library 	ini_file_a.py

*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm
${pyfile_agent} 		${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${pyfile_manager} 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${process_agent} 		None
${process_manager} 	None
${platform}		None
${COMPONENT} 	Agent
${component_name} 	Agent
${AGENT_DIR} 		${OUTPUT DIR}${/}rfswarm-agent

# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun
# ${results_dir} 			${EXECDIR}${/}rfswarm_manager${/}results
# ${results_dir} 			${TEMPDIR}${/}rfswarm_manager${/}results
${results_dir} 			${OUTPUT DIR}${/}results
*** Keywords ***
Set Platform
	Create Directory 	${results_dir}
	Set Platform By Python
	Set Platform By Tag

Set Platform By Python
	${system}= 		Evaluate 	platform.system() 	modules=platform

	IF 	"${system}" == "Darwin"
		Set Suite Variable    ${platform}    macos
	END
	IF 	"${system}" == "Windows"
		Set Suite Variable    ${platform}    windows
	END
	IF 	"${system}" == "Linux"
		Set Suite Variable    ${platform}    ubuntu
	END

Set Platform By Tag
	# [Arguments]		${ostag}
	Log 	${OPTIONS}
	Log 	${OPTIONS}[include]
	Log 	${OPTIONS}[include][0]
	${ostag}= 	Set Variable 	${OPTIONS}[include][0]

	IF 	"${ostag}" == "macos-latest"
		Set Suite Variable    ${platform}    macos
	END
	IF 	"${ostag}" == "windows-latest"
		Set Suite Variable    ${platform}    windows
	END
	IF 	"${ostag}" == "ubuntu-latest"
		Set Suite Variable    ${platform}    ubuntu
	END

Show Log
	[Arguments]		${filename}
	Log to console 	${\n}--VVV--${filename}--VVV--
	${filedata}= 	Get File 	${filename}
	Log 	${filedata} 	console=True
	Log to console 	--ɅɅɅ--${filename}--ɅɅɅ--${\n}

# Run Agent old
# 	[Arguments]		${options}=None
# 	IF  ${options} == None
# 		${options}= 	Create List
# 	END
# 	Log to console 	${\n}\${options}: ${options}
# 	# ${process}= 	Start Process 	python3 	${pyfile_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
# 	${process}= 	Start Process 	${cmd_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
# 	Set Test Variable 	$process_agent 	${process}

# Run Manager CLI old
# 	[Arguments]		${options}=None
# 	IF  ${options} == None
# 		${options}= 	Create List
# 	END
# 	IF  '-d' not in ${options}
# 		Create Directory 	${results_dir}
# 		Append To List 	${options} 	-d 	${results_dir}
# 	END
# 	Log to console 	${\n}\${options}: ${options}
# 	# ${process}= 	Start Process 	python3 	${pyfile_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
# 	${process}= 	Start Process 	${cmd_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
# 	Set Test Variable 	$process_manager 	${process}
# 	Sleep	5

Wait For Manager
	[Arguments]		${timeout}=10min
	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=kill
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Stop Manager
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Sleep	3s
		IF  '${platform}' == 'windows'	# Send Signal To Process keyword does not work on Windows
			${result}= 	Terminate Process		${process_manager}
		ELSE
			Send Signal To Process 	SIGINT 	${process_manager}
			${result}= 	Wait For Process 	${process_manager}	timeout=30	on_timeout=kill
		END
	ELSE
		# get result var for process even if not running any more
		${result}= 	Get Process Result		${process_manager}
	END
	Log		${result.stdout}
	Log		${result.stderr}

	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	Process returned: ${result.rc}

# Stop Agent old
# 	${running}= 	Is Process Running 	${process_agent}
# 	IF 	${running}
# 		Sleep	3s
# 		IF  '${platform}' == 'windows'	# Send Signal To Process keyword does not work on Windows
# 			${result} = 	Terminate Process		${process_agent}
# 		ELSE
# 			Send Signal To Process 	SIGINT 	${process_agent}
# 			${result}= 	Wait For Process 	${process_agent}	timeout=30	on_timeout=kill
# 		END
# 	ELSE
# 		# get result var for process even if not running any more
# 		${result}= 	Get Process Result		${process_agent}
# 	END
# 	Log		${result.stdout}
# 	Log		${result.stderr}
# 	# Should Be Equal As Integers 	${result.rc} 	0

Test Agent Connectivity
	#[Setup] 	Start Server	127.0.0.1	8138

	# wait for GET poll to /
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method} 	GET
	Should Be Equal 	${url}		/

	# wait for POST to /Jobs
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	# Should Be Equal 	${method}	POST
	# Should Be Equal 	${url}		/Jobs

	#[Teardown]	Stop Server

Find Result DB
	[Arguments] 	${directory}=${RESULTS_DIR} 	${result_pattern}=*_*
	${fols}= 	List Directory 	${directory} 	${result_pattern} 	absolute=True
	Log 	${fols} 	console=${True}

	${file}= 	List Directory 	${fols[-1]} 	*.db 	absolute=True
	Log 	Result DB: ${file[-1]} 	console=${True}
	RETURN 	${file[-1]}

Get Modules From Program .py File That Are Not BuildIn
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	[Arguments]		${file_path}
	@{buildin}=		Create List	__future__	__main__	_thread	_tkinter	abc	aifc	argparse	array	pkg_resources
	...    ast	asyncio	atexit	audioop	base64	bdb	binascii	bisect	builtins	bz2	calendar	cgi	cgitb
	...    chunk	cmath	cmd	code	codecs	codeop	collections	colorsys	compileall	concurrent	configparser
	...    contextlib	contextvars	copy	copyreg	cProfile	crypt	csv	ctypes	curses	dataclasses	datetime
	...    dbm	decimal	difflib	dis	doctest	email	encodings	ensurepip	enum	errno	faulthandler	fcntl
	...    filecmp	fileinput	fnmatch	fractions	ftplib	functools	gc	getopt	getpass	gettext	glob	graphlib
	...    grp	gzip	hashlib	heapq	hmac	html	http	idlelib	imaplib	imghdr	importlib	inspect	io	ipaddress
	...    itertools	json	keyword	lib2to3	linecache	locale	logging	lzma	mailbox	mailcap	marshal	math	mimetypes
	...    mmap	modulefinder	msilib	msvcrt	multiprocessing	netrc	nis	nntplib	numbers	operator	optparse	os
	...    ossaudiodev	pathlib	pdb	pickle	pickletools	pipes	pkgutil	platform	plistlib	poplib	posix	pprint
	...    profile	pstats	pty	pwd	py_compile	pyclbr	pydoc	queue	quopri	random	re	readline	reprlib	resource
	...    rlcompleter	runpy	sched	secrets	select	selectors	shelve	shlex	shutil	signal	site	sitecustomize
	...    smtplib	sndhdr	socket	socketserver	spwd	sqlite3	ssl	stat	statistics	string	stringprep	struct
	...    subprocess	sunau	symtable	sys	sysconfig	syslog	tabnanny	tarfile	telnetlib	tempfile	termios	test
	...    textwrap	threading	time	timeit	tkinter	token	tokenize	tomllib	trace	traceback	tracemalloc	tty	turtle
	...    turtledemo	types	typing	unicodedata	unittest	urllib	usercustomize	uu	uuid	venv	warnings	wave
	...    weakref	webbrowser	winreg	winsound	wsgiref	xdrlib	xml	xmlrpc	zipapp	zipfile	zipimport	zlib	zoneinfo

	&{replace_names}	Create Dictionary	PIL=pillow 		yaml=pyyaml

	${manager_content}	Get File	${file_path}
	${all_imports_lines}	Split String	${manager_content}	separator=\n
	Log	${all_imports_lines}

	${custom_imports}	Create List
	${length}	Get Length	${all_imports_lines}
	FOR  ${i}  IN RANGE  0  ${length}
		@{import_line_elements}	Create List
		FOR  ${x}  IN  ${all_imports_lines}[${i}]
			@{items_form_line}	Split String	${x}
			Append To List	${import_line_elements}		@{items_form_line}
		END

		${length2}	Get Length	${import_line_elements}
		IF  ${length2} != 0
			IF  '${import_line_elements}[0]' == 'class'
				BREAK
			END
		END

		FOR  ${j}  IN RANGE  0  ${length2}
			Log		${import_line_elements}[${j}]
			IF  '${import_line_elements}[${j}]' == '#'
				BREAK
			END
			IF  '${import_line_elements}[${j}]' == 'import' or '${import_line_elements}[${j}]' == 'from'
				${module_name}	Split String	${import_line_elements}[${j + 1}]	separator=.
				IF  '${module_name}[0]' not in ${buildin}
					Append To List	${custom_imports}	${module_name}[0]
				END
				BREAK
			END
		END
	END

	${custom_imports}	Evaluate	list(set(${custom_imports}))
	${length}	Get Length	${custom_imports}
	FOR  ${i}  IN RANGE  0  ${length}
		IF  '${custom_imports}[${i}]' in &{replace_names}
			${custom_imports}[${i}]  Set Variable  ${replace_names}[${custom_imports}[${i}]]
		END
	END

	RETURN	${custom_imports}

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

Get Agent PIP Data
	Run Process		pip		show	rfswarm-agent		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Agent must be installed with pip
	Log		${pip_data.stdout}
	RETURN		${pip_data.stdout}

Get Agent Default Save Path
	${pip_data}=	Get Agent PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_agent${/}

Check Icon Install
	VAR 	${projname}= 		rfswarm-agent 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Agent 		scope=TEST
	Run Keyword 	Check Icon Install For ${platform}

Check Icon Install For Macos
	${Status}= 	Run Keyword And Return Status 	Directory Should Exist 	%{HOME}${/}Applications${/}${projname}.app
	IF 	${Status}
		${appfolder}= 		Set Variable    %{HOME}${/}Applications${/}${dispname}.app
	ELSE
		${appfolder}= 		Set Variable    ${/}Applications${/}${dispname}.app
	END
	Directory Should Exist 	${appfolder} 		.app Folder not found

	Directory Should Exist 	${appfolder}${/}Contents 		Contents Folder not found
	Directory Should Exist 	${appfolder}${/}Contents${/}MacOS 		MacOS Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources 		Resources Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset 		iconset Folder not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset${/}icon_*.png 		Icons Images not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.icns 		icns File not found

	File Should Exist 	${appfolder}${/}Contents${/}Info.plist 		plist File not found
	Show Log 	 					${appfolder}${/}Contents${/}Info.plist

	File Should Exist 	${appfolder}${/}Contents${/}PkgInfo 		PkgInfo File not found
	Show Log 	 					${appfolder}${/}Contents${/}PkgInfo

	File Should Exist 	${appfolder}${/}Contents${/}MacOS${/}${projname} 		Executable Symbolic Link File not found

Check Icon Install For Windows
	Log 	%{USERPROFILE}
	Log 	%{APPDATA}
	Directory Should Exist 	%{APPDATA} 		APPDATA Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft 		Microsoft Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows 		Windows Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu 		Start Menu Directory not found
	File Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu${/}${dispname}.lnk 		Shortcut File not found


Check Icon Install For Ubuntu
	Log 	%{HOME}
	# /home/dave/.local/share/applications/rfswarm-manager.desktop
	${Status}= 	Run Keyword And Return Status 	File Should Exist 	%{HOME}${/}.local${/}share${/}applications${/}${projname}.desktop
	IF 	${Status}
		${pathprefix}= 		Set Variable    %{HOME}${/}.local${/}share
	ELSE
		${pathprefix}= 		Set Variable    ${/}usr${/}share
	END
	File Should Exist 	${pathprefix}${/}applications${/}${projname}.desktop 		Desktop File not found
	File Should Exist 	${pathprefix}${/}icons${/}hicolor${/}128x128${/}apps${/}${projname}.png 		Icon File not found

### v1.6.0 ###

Run Agent
	[Arguments] 	@{appargs}
	Run Agent CLI 	@{appargs}

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
			TRY
				Empty Directory 	${AGENT_DIR}
			EXCEPT
				Log 	Failed to empty Agent dir: ${AGENT_DIR}
			END
		END
	END

	Log 	${\n}Starting ${component_name} ... 	console=${True}
	${args}= 	Evaluate 	" ".join(@{appargs})
	Log 	\t\${args}: ${args} 	console=${True}

	${tname} 		Convert To Save Path 	${TEST NAME}
	Create File 		${OUTPUT DIR}${/}stdout_${comp}.txt
	Create File 		${OUTPUT DIR}${/}stderr_${comp}.txt
	${process}= 	Start Process 	${CMD_${comp}}  @{appargs}  alias=${component_name}
	...    stdout=${OUTPUT DIR}${/}stdout_${comp}.txt  stderr=${OUTPUT DIR}${/}stderr_${comp}.txt
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

Stop Agent
	Stop Agent CLI

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
	${running}= 	Is Process Running 	${PROCESS_${comp}}
	Run Keyword If 	${running} 	Fail 	Failed to close ${component_name}

	[Teardown] 	Set Suite Variable 	${PROCESS_${comp}} 	${None}

Change Manager INI Option
	[Arguments]		${section} 		${option}		${new_value}
	${location}=	Get Manager INI Location
	Change INI Option 	${location} 	${section} 		${option}		${new_value}

Create Manager INI File If It Does Not Exist
	[Documentation] 	Pass the: Manager, Reporter or Agent
	VAR 	${component_name} 	Manager
	${location}= 	Get Manager INI Location
	${comp} 	Convert To Lower Case 	${component_name}

	TRY
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	EXCEPT
		Log 	INI file for ${component_name} does not exist or it's empty. Creating new one. 	console=True

		IF  '${component_name}' == 'Manager'
			${process}= 	Start Process  rfswarm-manager  -n
		ELSE IF  '${component_name}' == 'Agent'
			${process}= 	Start Process  rfswarm-agent
		ELSE IF  '${component_name}' == 'Reporter'
			${process}= 	Start Process  rfswarm-reporter  -n
		END
		Wait For File To Exist 	${location}
		Sleep 	5s
		${result}= 	Terminate Process 	${process}

		File Should Exist 	${location}
		File Should Not Be Empty 	${location}
	END

Get Manager Default Save Path
	${pip_data}=	Get Manager PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_manager${/}

Get Manager INI Location
	${location}=	Get Manager Default Save Path
	RETURN	${location}RFSwarmManager.ini

Get Manager PIP Data
	Run Process	pip	show	rfswarm-manager		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Manager must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Wait For File To Exist
	[Arguments]		${filepath} 	${timeout}=120
	TRY
		WHILE    True 	limit=${timeout} seconds
			TRY
				Sleep 	500 ms
				File Should Exist 		${filepath}
			EXCEPT
				CONTINUE
			END
			BREAK
		END
	EXCEPT
		Fail 		File '${filepath}' does not exist after ${timeout} seconds
	END

Query Result DB
	[Arguments]		${dbfile} 	${sql} 	${info}=${True}
	Log 	dbfile: ${dbfile} 	console=${info}
	${dbfile}= 	Replace String 	${dbfile} 	${/} 	/

	Connect To Database 	sqlite3 	database=${dbfile} 	isolation_level=${None}
	Log 	sql: ${sql} 	console=${info}
	${result}= 	Query 	${sql}
	Log 	sql result: ${result} 	console=${info}
	Disconnect From Database
	RETURN 	${result}

Find Log
	[Documentation] 	Returns path to the stdout and stderr log file for current test
	[Arguments] 	${component_name}=${COMPONENT}
	${comp} 	Convert To Lower Case 	${component_name}
	${tname} 		Convert To Save Path 	${TEST NAME}

	File Should Exist 	${OUTPUT DIR}${/}stdout_${comp}.txt
	File Should Exist 	${OUTPUT DIR}${/}stderr_${comp}.txt

	RETURN 		${OUTPUT DIR}${/}stdout_${comp}.txt 	${OUTPUT DIR}${/}stderr_${comp}.txt

Read Log
	[Arguments]		${filepath}
	Log 		${filepath}
	${filedata}= 	Get File 	${filepath} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata}
	RETURN 		${filedata}

Convert To Save Path
	[Arguments] 	${path}
	${safe_path} 		Evaluate 	re.sub(r'[<>:"/\\|?*]', '_', "${path}".replace(' ', '_')).replace(chr(0), '_').rstrip(' .')[:60] 	modules=re

	RETURN 	${safe_path}

Wait Until the Agent Connects to the Manager
	[Documentation] 	For this keyword to function correctly, logs from the agent must be available dynamically.
	VAR    ${timeout}    160
	TRY
		${stdout}  ${stderr}= 	Find Log 	Agent
	EXCEPT
		Sleep 	5s
		${stdout}  ${stderr}= 	Find Log 	Agent
	END

	Log 	Waiting for the Agent to connect with the Manager... 	console=${true}
	TRY
		WHILE    True 	limit=${timeout} seconds
			TRY
				Sleep 	10 s
				${stdout_content}= 	Read Log 	${stdout}
				Should Contain 		${stdout_content}  Manager Connected
			EXCEPT
				CONTINUE
			END
			BREAK
		END
	EXCEPT
		Fail 	Agent didn't connect to the Manager after ${timeout} seconds
	END

Wait Until the Query Is Not Empty
	[Arguments]		${dbfile}  ${sql}  ${timeout}=${300}

	VAR 	${iter} 	0
	TRY
		WHILE    True 	limit=${timeout} seconds
			${iter}= 	Evaluate  ${iter} + 1
			IF    ${iter} == 30
				Log 	Query '${sql}' is returning empty row after ${iter} seconds.  level=WARN
			END
			
			TRY
				Sleep 	1s
				${query_result}= 	Query Result DB 	${dbfile}  ${sql}  info=${False}
				${len}= 	Get Length 	${query_result}
				Should Be True 	${len} > 0
			EXCEPT
				CONTINUE
			END
			BREAK
		END
	EXCEPT
		Fail 		Query '${sql}' is returning empty row after ${timeout} seconds.
	END

	#
#
