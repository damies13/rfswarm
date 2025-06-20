*** Settings ***
Documentation 	This resource file contains the basic keywords for all components that are run in the command line.

Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library 	Collections
Library 	DateTime

Library 	ini_file.py
Library 	get_ip_address.py

*** Variables ***
${COMPONENT} 		${None} 	# currently used rfswarm component (app)
${platform} 		${None}
${results_dir} 		${OUTPUT DIR}${/}results

*** Keywords ***
Basic Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the suite for keywords. The component must be chosen between: Manager, Reporter, Agent
	Set Suite Variable 	${COMPONENT} 	${component}
	Set Platform

	${status}= 	Run Keyword And Return Status 	Directory Should Exist 	${results_dir}
	IF 	not ${status}
		Create Directory 	${results_dir}
	END

	Log To Console 	\t[ === Basic suite configuration has been initiated for ${COMPONENT} === ]
	Log To Console 	component = ${COMPONENT}
	Log To Console 	platform = ${platform}
	Log To Console 	results dir = ${results_dir}\n\n\n

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
	Log 	${OPTIONS}
	Log 	${OPTIONS}[include]
	${inclen}= 	Get Length 	${OPTIONS}[include]
	IF 	${inclen} > 0
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

Check Logs
	${comp} 	Convert To Lower Case 	${COMPONENT}
	${stdout_component}= 		Read Log 	${OUTPUT DIR}${/}stdout_${comp}.txt
	${stderr_component}= 		Read Log 	${OUTPUT DIR}${/}stderr_${comp}.txt

	Should Not Contain 	${stdout_component} 	RuntimeError
	Should Not Contain 	${stderr_component} 	RuntimeError
	Should Not Contain 	${stdout_component} 	Exception
	Should Not Contain 	${stderr_component} 	Exception
	Should Not Contain 	${stdout_component} 	OSError
	Should Not Contain 	${stderr_component} 	OSError
	Should Not Contain 	${stdout_component} 	KeyError
	Should Not Contain 	${stderr_component} 	KeyError

Utilisation Stats
	${cpupct}= 	Evaluate 	psutil.cpu_percent(interval=1, percpu=True) 				modules=psutil
	Log 	\n${cpupct} 	console=True
	${loadavg}= 	Evaluate 	psutil.getloadavg() 															modules=psutil
	Log 	${loadavg} 	console=True
	${mem}= 		Evaluate 	psutil.virtual_memory() 														modules=psutil
	Log 	${mem}
	${proc}= 		Evaluate 	list(psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username'])) 		modules=psutil
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

Clean Up Old Files
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# cleanup previous output
	Log To Console    ${OUTPUT DIR}
	Remove File    ${OUTPUT DIR}${/}*.txt
	Remove File    ${OUTPUT DIR}${/}*.png
	# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*

# # # # # #
# Paths:  #
# # # # # #

Show Dir Contents
	[Arguments]		${dir}
	${filesnfolders}= 	Evaluate    glob.glob("${dir}${/}*", recursive=True) 	modules=glob
	FOR 	${item} 	IN 	${filesnfolders}
		Log 	${item} 	console=True
	END

Find Absolute Paths And Names For Files In Directory
	[Documentation]	This algorithm analyses the specified path and returns all
	...    file names with their absolute paths even those that are in subdirectories
	[Arguments]		${given_path}	@{excluded_files}
	${curr_dir}	Set Variable	${given_path}
	@{absolute_paths}	Create List
	@{file_names}	Create List
	${new_dir}		List Directories In Directory	${curr_dir}	absolute=${True}

	#=== Collecting data section ===
	@{dir_files_path}=		List Files In Directory		${curr_dir}	absolute=${True}
	@{dir_file_names}=		List Files In Directory		${curr_dir}

	${length}	Get Length	${dir_files_path}
	FOR  ${i}  IN RANGE  0  ${length}
		IF  '${dir_file_names}[${i}]' not in ${excluded_files}
			Append To List	${absolute_paths}	${dir_files_path}[${i}]
			Append To List	${file_names}	${dir_file_names}[${i}]
		END
	END

	#=== Merging data section ===
	FOR  ${specific_dir}  IN  @{new_dir}
		${next_absolute_paths}	${next_file_names}
		...    Find Absolute Paths And Names For Files In Directory	${specific_dir}	@{excluded_files}

		${length}	Get Length	${next_absolute_paths}
		FOR  ${i}  IN RANGE  0  ${length}
			${bad_list}	Get Length	${next_absolute_paths}
			IF  ${bad_list} != ${0}
				Append To List	${absolute_paths}	${next_absolute_paths}[${i}]
				Append To List	${file_names}	${next_file_names}[${i}]
			END
		END
	END

	RETURN	${absolute_paths}	${file_names}

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

Get Relative Paths
	[Arguments] 	${base} 		${paths_in}

	${paths_out}= 	Create List
	FOR 	${item} 	IN 		@{paths_in}
		${relpath}= 	Evaluate 	os.path.relpath(r"${item}", start=r"${base}") 	modules=os.path
		Append To List 	${paths_out} 	${relpath}
	END
	RETURN 	${paths_out}

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

# # # # #
# CSV:  #
# # # # #

Convert CSV File Cells To a List
	[Arguments]		${csv_file_path}	${csv_separator}
	${csv_file_content}=	Get File		${csv_file_path}
	@{csv_rows_list}=	Split String	${csv_file_content}		separator=\n

	@{csv_rows_content_list}=	Create List
	FOR  ${row}  IN  @{csv_rows_list}
		@{csv_row_cells_list}=		Split String	${row}	separator=${csv_separator}
		Append To List	${csv_rows_content_list}	${csv_row_cells_list}
	END

	${status}=	Run Keyword And Return Status	Should Be Empty	@{csv_rows_content_list}[-1]
	IF  ${status} == ${True}
		@{csv_rows_content_list}	Set Variable	${csv_rows_content_list}[:-1]
	END

	RETURN	${csv_rows_content_list}

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

Wait For File To Exist
	[Arguments] 	${filepath} 	${timeout}=${120}
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
	Connect To Database 	sqlite3 	database=${dbfile} 	isolation_level=${None}
	# Log 	conn: ${conn} 	console=true
	Log 	sql: ${sql} 	console=true
	Check If Exists In Database 	${sql}
	${result}= 	Query 	${sql}
	Log 	sql result: ${result} 	console=true
	Disconnect From Database
	RETURN 	${result}

Resync Date With Time Server
	[Arguments] 	${old_date}
	IF 	"${platform}" == "macos"
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
	IF 	"${platform}" == "windows"
		${result}= 	Run Process 	powershell.exe  w32tm  /resync 	shell=${True}
		Log 	${result.stdout}
		Log 	${result.stderr}

		${result}= 	Run Process 	powershell.exe  Get-Date  -Format  'yyyy-MM-dd' 	shell=${True}
		Should Not Be Equal As Strings 	${result.stdout} 	${old_date}
		Log 	Back to original date: ${result.stdout} 	console=${True}
		Log 	${result.stderr}
	END
	IF 	"${platform}" == "ubuntu"
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

	${python_file_content}	Get File	${file_path}
	${all_imports_lines}	Split String	${python_file_content}	separator=\n
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
