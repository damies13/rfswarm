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
${agent_dir} 				${OUTPUT DIR}${/}rfswarm-agent

*** Keywords ***
Set Platform
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
	Log 		${\n}--VVV--${filename}--VVV-- 		console=True
	${filedata}= 	Get File 	${filename} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata} 		console=True
	Log 		--ɅɅɅ--${filename}--ɅɅɅ--${\n} 		console=True
	RETURN 		${filedata}

Read Log
	[Arguments]		${filename}
	Log 		${filename}
	${filedata}= 	Get File 	${filename} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata}
	RETURN 		${filedata}

Show Dir Contents
	[Arguments]		${dir}
	${filesnfolders}= 	Evaluate    glob.glob("${dir}${/}*", recursive=True) 	modules=glob
	FOR 	${item} 	IN 	${filesnfolders}
		Log 	${item} 	console=True
	END

Run Agent
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
	END
	Append To List 	${options} 	-d 	${agent_dir}
	Create Directory 	${agent_dir}
	Empty Directory 	${agent_dir}

	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	${process}= 	Start Process 	${cmd_agent}  @{options}  alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Run Manager CLI
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
		Create Directory 	${results_dir}
		Append To List 	${options} 	-d 	${results_dir}
	END
	Log to console 	${\n}\${options}: ${options}
	# ${process}= 	Start Process 	python3 	${pyfile_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	${process}= 	Start Process 	${cmd_manager}  @{options}  alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}

Wait For Manager
	[Arguments]		${timeout}=30min
	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=terminate
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Check Agent Is Running
	[Documentation] 	This keyword checks if the agent is running and returns true or false
	${result}= 	Is Process Running		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log 	Is Agent Running: ${result} 	console=True
	Should Be True 	${result}

Stop Manager
	${result}= 	Terminate Process		${process_manager}
	# Should Be Equal As Integers 	${result.rc} 	0

	Copy File 	${result.stdout_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stdout_manager.txt
	Copy File 	${result.stderr_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stderr_manager.txt

	Log to console 	Terminate Manager Process returned: ${result.rc} 	console=True
	Log 	stdout_path: ${result.stdout_path} 	console=True
	Log 	stdout: ${result.stdout} 	console=True
	Log 	stderr_path: ${result.stderr_path} 	console=True
	Log 	stderr: ${result.stderr} 	console=True

Stop Agent
	${result}= 	Terminate Process		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0

	Copy File 	${result.stdout_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stdout_agent.txt
	Copy File 	${result.stderr_path} 	${OUTPUT DIR}${/}${TEST NAME}${/}stderr_agent.txt

	Log 	Terminate Agent Process returned: ${result.rc} 	console=True
	Log 	stdout_path: ${result.stdout_path} 	console=True
	Log 	stdout: ${result.stdout} 	console=True
	Log 	stderr_path: ${result.stderr_path} 	console=True
	Log 	stderr: ${result.stderr} 	console=True
	Show Dir Contents 	${agent_dir}

Set Global Filename And Default Save Path
	[Documentation]	Sets global default save path as Test Variable and file name for robot test.
	...    You can also provide optional save path.
	[Arguments]		${input_name}	${optional_path}=${None}

	Set Test Variable	${global_name}	${input_name}
	${location}=	Get Manager Default Save Path
	Set Test Variable	${global_path}	${location}

	Set Test Variable 	$file_name 	${global_name}
	IF  '${optional_path}' != '${None}'
		Set Test Variable	${global_path}	${optional_path}
		${location}=	Get Manager INI Location
		${ini_content}=		Get Manager INI Data
		${ini_content_list}=	Split String	${ini_content}
		${scriptdir}=	Get Index From List		${ini_content_list}		scriptdir

		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${scriptdir + 2}]	${optional_path}
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${scriptdir + 5}]	${optional_path}

		Remove File		${location}
		Log		${ini_content}
		Append To File	${location}		${ini_content}
	END

	Log		${global_name}
	Log		${global_path}

Get Manager Default Save Path
	${pip_data}=	Get Manager PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_manager${/}

Get Manager INI Location
	${location}=	Get Manager Default Save Path
	RETURN	${location}${/}RFSwarmManager.ini

Get Manager INI Data
	${location}=	Get Manager INI Location
	TRY
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	EXCEPT
		# --- temp fix:
		@{mngr_options}= 	Create List 	-g 	1
		Open Manager GUI 		${mngr_options}
		# ---
		Run Keyword		Close Manager GUI ${platform}
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	END
	${ini_content}=	Get File	${location}
	Log	${ini_content}
	Should Not Be Empty	${ini_content}
	RETURN	${ini_content}

#Read INI Data
#	[Arguments]		${inifile}

Set INI Window Size
	[Arguments]		${width}=${None}	${height}=${None}
	${location}=	Get Manager INI Location
	${ini_content}=		Get Manager INI Data
	${ini_content_list}=	Split String	${ini_content}
	${i}=	Get Index From List		${ini_content_list}		win_width
	${j}=	Get Index From List		${ini_content_list}		win_height
	IF	"${width}" != "${None}"
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${i + 2}]	${width}
	END
	IF	"${height}" != "${None}"
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${j + 2}]	${height}
	END
	Remove File		${location}
	Log		${ini_content}
	Append To File	${location}		${ini_content}

Change Manager INI File Settings
	[Arguments]		${option}	${new_value}
	${location}=	Get Manager INI Location
	${ini_content}=		Get Manager INI Data
	${ini_content_list}=	Split String	${ini_content}
	${option_index}=	Get Index From List		${ini_content_list}		${option}

	${len}	Get Length	${ini_content_list}
	IF  ${len} > ${option_index + 2}
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${option_index + 2}]	${new_value}
	ELSE
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${option_index}] =	${option} = ${new_value}
	END

	Remove File		${location}
	Log		${ini_content}
	Append To File	${location}		${ini_content}

Get Manager PIP Data
	Run Process	pip	show	rfswarm-manager		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Manager must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

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
	# Disconnect From All Databases
	Log 	dbfile: ${dbfile} 	console=true
	${dbfile}= 	Replace String 	${dbfile} 	${/} 	/
	# Log to console 	\${dbfile}: ${dbfile}
	Connect To Database Using Custom Params 	sqlite3 	database="${dbfile}", isolation_level=None
	# Log 	conn: ${conn} 	console=true
	Log 	sql: ${sql} 	console=true
	Check If Exists In Database 	${sql}
	${result}= 	Query 	${sql}
	Log 	sql result: ${result} 	console=true
	Disconnect From Database
	RETURN 	${result}

CSV to List
	[Arguments] 	${filepath}
	File Should Exist 	${filepath}
	${f}= 	Evaluate    open($filepath)
	${csvdata}= 	Evaluate    csv.reader($f, delimiter=',') 	modules=csv
	${data}= 			Evaluate    list($csvdata)
	Evaluate    str($f.close())
	${headings}= 			Evaluate    str($data.pop(0))
	RETURN 	${data}

CSV to Dict
	[Arguments] 	${filepath}
	File Should Exist 	${filepath}
	${f}= 	Evaluate    open($filepath)
	${csvdata}= 	Evaluate    csv.DictReader($f, delimiter=',') 	modules=csv
	${data}= 			Evaluate    list($csvdata)
	Evaluate    str($f.close())
	RETURN 	${data}

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
	&{replace_names}	Create Dictionary	PIL=pillow

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
#

Create Testdata Agent INI
	[Arguments] 	${inifile}
	Create File 	${inifile} 	[Agent]\n
	Append To File 	${inifile} 	agentname = E-5CG2026KN2\n
	Append To File 	${inifile} 	agentdir = ${testdata}${/}agent-dir\n
	Append To File 	${inifile} 	xmlmode = False\n
	Append To File 	${inifile} 	excludelibraries = BuiltIn,String,OperatingSystem,perftest\n
	Append To File 	${inifile} 	properties =\n
	Append To File 	${inifile} 	swarmmanager = http://localhost:8138/\n
	Append To File 	${inifile} 	robotcmd = robot\n

Create Testdata Manager INI
	[Arguments] 	${inifile}

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

List Files In Directory And Sub Directories
	[Arguments] 	${path} 	${pattern}=None 	${absolute}=False
	@{files}= 	List Files In Directory 	${path} 	${pattern} 	${absolute}
	FOR 	${file} 	IN 	@{files}
		${fpath} 	${ext} = 	Split Extension 	${file}
		IF 		'${ext}' == 'pyc'
			Remove Values From List 		${files} 	${file}
		END
	END
	@{dirs}= 	List Directories In Directory 	${path}
	FOR 	${dir} 	IN 	@{dirs}
		@{sd_files}= 	List Files In Directory And Sub Directories 	${path}${/}${dir} 	${pattern} 	${absolute}
		FOR 	${file} 	IN 	@{sd_files}
			IF 	${absolute}
				Append To List 	${files} 	${file}
			ELSE
				Append To List 	${files} 	${dir}${/}${file}
			END
		END
	END
	RETURN 	${files}

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

Check Icon Install
	VAR 	${projname}= 		rfswarm-manager 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Manager 		scope=TEST
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
