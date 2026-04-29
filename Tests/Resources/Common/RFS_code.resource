*** Settings ***
Resource 	Common.resource

*** Variables ***
@{CHECKED_PY_FILES} 	__init__.py
@{BUILTIN_PY_MODULES}	__future__	__main__	_thread	_tkinter	abc	aifc	argparse	array	pkg_resources
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

*** Keywords ***
# # # # # # # # # #
# Python modules: #
# # # # # # # # # #

Update BUILTIN_PY_MODULES
	[Arguments]		${module}
	@{buildin}=		Create List		@{BUILTIN_PY_MODULES}
	Append To List 	${buildin} 	${module}
	${buildin}	Evaluate	list(set(${buildin}))
	VAR    @{BUILTIN_PY_MODULES}      @{buildin}    scope=SUITE

Get Modules From Program .py File That Are Not BuildIn
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	[Arguments]		${file_path}
	@{buildin}=		Create List		@{BUILTIN_PY_MODULES}
	log 	${buildin}

	&{replace_names}	Create Dictionary	PIL=pillow 		yaml=pyyaml
	${custom_imports}	Create List

	# add local modules to buildin list and also check them for non builtin import modules
	${file_location} 	${file_name}= 	Split Path 	${file_path}
	@{checked_py_files}= 	Create List 	${file_name} 	@{CHECKED_PY_FILES}
	VAR    @{CHECKED_PY_FILES}      @{checked_py_files}    scope=SUITE
	Log		${CHECKED_PY_FILES}
	@{pyfiles}= 	List Files In Directory 	${file_location} 	*.py
	Remove Values From List 	${pyfiles}  	@{CHECKED_PY_FILES}
	Log		${pyfiles}
	FOR 	${pyfile} 	IN 	@{pyfiles}
		${module} 	${ext} = 	Split Extension 	${pyfile}
		Update BUILTIN_PY_MODULES 	${module}
		@{module_imports}	Get Modules From Program .py File That Are Not BuildIn 	${file_location}${/}${pyfile}
		Append To List 	${custom_imports} 	@{module_imports}
	END

	${parent_location} 	${file_dir_name}= 	Split Path 	${file_location}
	${common_location}= 	Join Path 	${parent_location}  	rfswarm_common
	Log		${CHECKED_PY_FILES}
	@{pyfiles}= 	List Files In Directory 	${common_location} 	*.py
	Remove Values From List 	${pyfiles}  	@{CHECKED_PY_FILES}
	Log		${pyfiles}
	FOR 	${pyfile} 	IN 	@{pyfiles}
		${module} 	${ext} = 	Split Extension 	${pyfile}
		Update BUILTIN_PY_MODULES 	${module}
		@{module_imports}	Get Modules From Program .py File That Are Not BuildIn 	${common_location}${/}${pyfile}
		Append To List 	${custom_imports} 	@{module_imports}
	END

	${manager_content}	Get File	${file_path}
	${all_imports_lines}	Split String	${manager_content}	separator=\n
	Log	${all_imports_lines}

	log 	${BUILTIN_PY_MODULES}

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
			IF  '${import_line_elements}[${j}]' == '='
				BREAK
			END
			IF  '${import_line_elements}[${j}]' == 'import' or '${import_line_elements}[${j}]' == 'from'
				${module_name}	Split String	${import_line_elements}[${j + 1}]	separator=.
				IF  '${module_name}[0]' not in ${BUILTIN_PY_MODULES}
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
			${custom_imports}[${i}] 	Set Variable 	${replace_names}[${custom_imports}[${i}]]
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
				VAR 	${install_requires} 	${setup_content_elements}[1][2:-3]
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
