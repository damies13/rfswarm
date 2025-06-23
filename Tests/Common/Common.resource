*** Settings ***
Documentation 	
...    This resource file contains the basic keywords for all components that are run in the command line. 
...    Run "Basic Suite Initialization ${component}" keyword to set the basic suite configuration.

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
${PLATFORM} 		${None}
${RESULTS_DIR} 		${None}

*** Keywords ***
Basic Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the basic configuration for suite. The component must be chosen between: Manager, Reporter, Agent
	Set Suite Variable 	${COMPONENT} 	${component}
	Set Platform

	Set Suite Variable 	${RESULTS_DIR} 		${OUTPUT DIR}${/}results
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
		Set Suite Variable    ${PLATFORM}    macos
	END
	IF 	"${system}" == "Windows"
		Set Suite Variable    ${PLATFORM}    windows
	END
	IF 	"${system}" == "Linux"
		Set Suite Variable    ${PLATFORM}    ubuntu
	END

Set Platform By Tag
	Log 	${OPTIONS}
	Log 	${OPTIONS}[include]
	${inclen}= 	Get Length 	${OPTIONS}[include]
	IF 	${inclen} > 0
		Log 	${OPTIONS}[include][0]
		${ostag}= 	Set Variable 	${OPTIONS}[include][0]

		IF 	"${ostag}" == "macos-latest"
			Set Suite Variable    ${PLATFORM}    macos
		END
		IF 	"${ostag}" == "windows-latest"
			Set Suite Variable    ${PLATFORM}    windows
		END
		IF 	"${ostag}" == "ubuntu-latest"
			Set Suite Variable    ${PLATFORM}    ubuntu
		END
	END

Show Log
	[Arguments]		${filename}
	Log 		${\n}--VVV--${filename}--VVV-- 		console=True
	${filedata}= 	Get File 	${filename} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata} 		console=True
	Log 		--ɅɅɅ--${filename}--ɅɅɅ--${\n}${\n} 		console=True
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

# # # # # # #
# Pip Data: #
# # # # # # #

Get ${component_name} PIP Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${comp} 	Convert To Lower Case 	${component_name}

	Run Process 	pip  show  rfswarm-${comp} 		alias=pip-show
	${pip_data} 	Get Process Result 	pip-show
	Should Not Be Empty 	${pip_data.stdout} 		msg=${comp} must be installed with pip
	Log 	${pip_data.stdout}

	RETURN 	${pip_data.stdout}

Get ${component_name} Default Save Path
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${comp} 	Convert To Lower Case 	${component_name}

	${pip_data} 	Get ${component_name} PIP Data
	${pip_data_list} 	Split String 	${pip_data}
	${i} 	Get Index From List 	${pip_data_list} 	Location:
	${location}= 	Set Variable 	${pip_data_list}[${i + 1}]

	RETURN 	${location}${/}rfswarm_${comp}${/}

# # # # #
# INI:  #
# # # # #

Get ${component_name} INI Location
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location} 	Get ${component_name} Default Save Path

	RETURN 	${location}${/}RFSwarm${component_name}.ini

Create ${component_name} INI File If It Does Not Exist
	${location}= 	Get ${component_name} INI Location
	${comp} 	Convert To Lower Case 	${component_name}

	TRY
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	EXCEPT
		${process}= 	Start Process  rfswarm-${comp}  stdout=${OUTPUT DIR}${/}stdout_${comp}.txt  stderr=${OUTPUT DIR}${/}stderr_${comp}.txt
		Sleep 	6s
		${result}= 	Terminate Process 	${process}

		File Should Exist 	${location}
		File Should Not Be Empty 	${location}
	END

Get ${component_name} INI Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location}= 	Get ${component_name} INI Location
	Create ${component_name} INI File If It Does Not Exist
	${cfg}= 	Evaluate 		configparser.ConfigParser()		modules=configparser
	Evaluate 		$cfg.read('${location}')
	${ini_content}= 	Convert To Dictionary 	${cfg}
	Log 	${ini_content}
	RETURN 	${ini_content}

Show ${component_name} INI Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location}= 	Get ${component_name} INI Location
	Show Log 	${location}

Change ${component_name} INI Option
	[Documentation] 	Pass the: Manager, Reporter or Agent
	[Arguments] 	${section}  ${option}  ${new_value}
	${location}= 	Get ${component_name} INI Location

	Create ${component_name} INI File If It Does Not Exist
	Change INI Option 	${location}  ${section}  ${option}  ${new_value}

# # # # # # # # # # # # # # # # #
# Paths, directories and files: #
# # # # # # # # # # # # # # # # #

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

Clean Up Old Files
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# cleanup previous output
	Log To Console    ${OUTPUT DIR}
	Remove File    ${OUTPUT DIR}${/}*.txt
	Remove File    ${OUTPUT DIR}${/}*.png
	# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*

Clear Result Directory
	[Documentation] 	Clears all files and directories in "$RESULTS_DIR" directory. Use with caution.
	[Arguments] 	${RES_DIR}=${RESULTS_DIR}
	@{run_result_dirs}= 	List Directories In Directory 	${RES_DIR} 	absolute=${True}
	FOR  ${dir}  IN  @{run_result_dirs}
		Remove Directory 	${dir} 	recursive=${True}
	END

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

# # # # # # #
# Database: #
# # # # # # #

Find Result DB
	[Arguments] 	${directory}=${RESULTS_DIR} 	${result_pattern}=*_*
	# ${fols}= 	List Directory 	${RESULTS_DIR}
	# Log to console 	${fols}
	${fols}= 	List Directory 	${directory} 	${result_pattern} 	absolute=True
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
	Connect To Database 	sqlite3 	database=${dbfile} 	isolation_level=${None}
	Log to console 	sql: ${sql}
	${result}= 	Query 	${sql}
	Log to console 	sql result: ${result}
	Disconnect From Database
	RETURN 	${result}

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

# # # # # # # # # #
# Python modules: #
# # # # # # # # # #

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

# # # # # # # # # #
# Icon Installs:  #
# # # # # # # # # #

Check Icon Install
	${comp} 	Convert To Lower Case 	${COMPONENT}
	VAR 	${projname}= 		rfswarm-${comp} 		scope=TEST
	VAR 	${dispname}= 		RFSwarm ${COMPONENT} 	scope=TEST
	Run Keyword 	Check Icon Install For ${PLATFORM}

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
