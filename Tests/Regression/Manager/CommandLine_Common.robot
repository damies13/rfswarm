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

Show Log
	[Arguments]		${filename}
	Log to console 	${\n}-----${filename}-----
	${filedata}= 	Get File 	${filename}
	Log to console 	${filedata}
	Log to console 	-----${filename}-----${\n}

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

Wait For Manager
	[Arguments]		${timeout}=10min
	${result}= 	Wait For Process		${process_manager} 	timeout=${timeout} 	on_timeout=kill
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	${result.rc}

Check Agent Is Running
	${result}= 	Is Process Running		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log 	Is Agent Running: ${result} 	console=True
	Should Be True 	${result}

Stop Manager
	${result}= 	Terminate Process		${process_manager}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log to console 	Terminate Process returned: ${result.rc}

Stop Agent
	${result}= 	Terminate Process		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0
	Log 	Terminate Process returned: ${result.rc} 	console=True
	Log 	stdout_path: ${result.stdout_path} 	console=True
	Log 	stdout: ${result.stdout} 	console=True
	Log 	stderr_path: ${result.stderr_path} 	console=True
	Log 	stderr: ${result.stderr} 	console=True
	Show Dir Contents 	${agent_dir}

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
