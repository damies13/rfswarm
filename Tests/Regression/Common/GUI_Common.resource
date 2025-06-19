*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library 	Collections
Library 	DateTime
Library 	XML
Library 	OCRLibrary

Library 	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

Library 	ini_file.py
Library 	get_ip_address.py
Library 	img_common.py

*** Variables ***
${COMPONENT} 		${None} 	# currently used rfswarm component (app)
${platform}			${None}
${global_path}		${None}
${IMAGE_DIR} 		${CURDIR}${/}Images${/}file_method

${debug_screenshots} 		${False}
${default_image_timeout} 	${120}

*** Keywords ***
Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the suite. The component must be chosen between: Manager, Reporter
	Set Suite Variable 	${COMPONENT} 	${component}
	Set Suite Variable 	${IMAGE_DIR} 	${CURDIR}${/}..${/}${COMPONENT}${/}Images${/}file_method
	ImageHorizonLibrary.Set Reference Folder 	${IMAGE_DIR}

	Set Platform

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
	${stdout_manager}= 		Read Log 	${OUTPUT DIR}${/}stdout_${comp}.txt
	${stderr_manager}= 		Read Log 	${OUTPUT DIR}${/}stderr_${comp}.txt

	Should Not Contain 	${stdout_manager} 	RuntimeError
	Should Not Contain 	${stderr_manager} 	RuntimeError
	Should Not Contain 	${stdout_manager} 	Exception
	Should Not Contain 	${stderr_manager} 	Exception
	Should Not Contain 	${stdout_manager}	OSError
	Should Not Contain 	${stderr_manager} 	OSError
	Should Not Contain 	${stdout_manager}	KeyError
	Should Not Contain 	${stderr_manager} 	KeyError

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

Press ${key} ${n} Times
	[Documentation]	Provide full name. For example: Key.tab
	Sleep	1
	FOR  ${i}  IN RANGE  0  ${n}
		Press Combination 	${key}
	END

Wiggle Mouse
	Move To 	10 	10
	Move To 	20 	20

Handle Donation Reminder
	${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		30
	VAR 	${DonationReminder} 	${found} 		scope=TEST


Get Image Size
	[Arguments] 	${imgfile}
	# ahrrrg windows paths, PIL.Image.open doesn't like them, need to escape / replace \\
	# ${imgfile}= 	Evaluate    "${imgfile}".replace('\\' '/')
	${img}= 	Evaluate    PIL.Image.open(r'${imgfile}') 	PIL.Image
	${imgsize}= 	Set Variable    ${img.size}
	# Evaluate    ${img.close()}
	RETURN 	${imgsize}

Get Last Screenshot
	Log 	${OUTPUT FILE}
	${path} 	${file}= 	Split Path 	${OUTPUT FILE}
	@{files}= 	List Files In Directory 	${path} 	*.png 	absolute
	Sort List 	${files}
	${fc}= 	Get Length 	${files}
	IF 	${fc} > 9
		${len0}= 	Get Length 	${files}[0]
		WHILE    True    limit=10
			${lenlast}= 	Get Length 	${files}[-1]
			IF 	${lenlast} > ${len0}
				RETURN 	${files}[-1]
			ELSE
				Remove From List 	${files} 	-1
			END
		END
	ELSE
		RETURN 	${files}[-1]
	END

Get Python Version Info
	${vinfo}= 	Evaluate 	sys.version_info 	modules=sys
	RETURN		${vinfo}

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

Wait For File To Exist
	[Arguments]		${filepath} 	${timeout}=${default_image_timeout}
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

# # # # # # #
# CLICK ... #
# # # # # # #

Click Button
	[Arguments]		${btnname} 		${timeout}=${default_image_timeout}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}= 	Set Variable 	${comp}_${platform}_button_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	IF  "${platform}" == "windows"
		Set Confidence	0.85
	END
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	IF  "${platform}" == "windows"
		Set Confidence 	0.9
	END

Wait For Dialog Button
	[Arguments]		${btnname} 		${timeout}=${default_image_timeout}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable 	${platform}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=${default_image_timeout}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click Tab
	[Arguments]		${tabname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		${comp}_${platform}_tab_${tabnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Select Option
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}= 	Set Variable		${comp}_${platform}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Selected Option Should Be
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}= 	Set Variable		${comp}_${platform}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}

Click Menu
	[Arguments]		${menuname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	${img}=	Set Variable		${comp}_${platform}_menu_${menunamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click CheckBox
	[Arguments]		${status} 		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		${platform}_checkbox_${statusl}_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click RadioBtn
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_radiobtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click ${item} With Vertical Offset
	[Arguments]		${image_name}	${offset}=0
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	${img}=	Set Variable		${comp}_${platform}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Click ${item} With Horizontal Offset
	[Arguments]		${image_name}	${offset}=0
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	${img}=	Set Variable		${comp}_${platform}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

File Open Dialogue Select File
	[Arguments]		${filepath}
	Run Keyword		File Open Dialogue ${platform} Select File 			${filepath}
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

File Open Dialogue ubuntu Select File
	[Arguments]		${filepath}
	Sleep	2
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath} 	Key.ENTER
	Sleep	0.5
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	# Click Dialog Button 	open

File Open Dialogue windows Select File
	[Arguments]		${filepath}
	Sleep	3
	${filepath}= 	Normalize Path 	${filepath}
	${path} 	${file} = 	Split Path 	${filepath}
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${path} 	Key.ENTER
	Sleep	0.5
	Take A Screenshot
	Type 		${file}
	Sleep	0.5
	Take A Screenshot
	Press key.enter 1 Times
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	# Click Dialog Button 	open
	Sleep	0.5

File Open Dialogue macos Select File
	[Arguments]		${filepath}
	Sleep	3
	${filepath}=	Convert To Lower Case	${filepath}
	Evaluate	clipboard.copy(r"${filepath}")	modules=clipboard		#copy path to clipboard
	Press Combination 	KEY.command 	KEY.shift 	KEY.g
	Press Combination 	KEY.backspace		#clear text filed
	Click Label With Horizontal Offset 	file_name 	-10
	Click	button=right	#show context menu
	Sleep	2
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	Press Combination 	KEY.down	#choose paste option(should be first)
	Press key.enter 1 Times		#execute paste option
	Sleep	0.5
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	Press key.enter 1 Times
	Sleep	0.5
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot
	Click Dialog Button 	open
	# Type 		Key.BACKSPACE 	Key.DELETE
	# Click Dialog Button 	open

# # # # # # #
# ... Text  #
# # # # # # #

Find Text
	[Arguments]		${mytext}
	Take A Screenshot
	${img}=		Get Last Screenshot
	Log 	${img}
	${processed_img}= 	Read Image 	${img}
	${bounds}= 	Locate Text Bounds 	${processed_img} 	${mytext}
	Log 	${bounds}
	IF 	${bounds}
		RETURN 	${bounds}
	ELSE
		Fail		${mytext} Not Found
	END

Click Text
	[Arguments]		${mytext} 	${offsetx}=0 	${offsety}=0
	${bounds}= 	Find Text		${mytext}
	${x}= 	Evaluate 	${bounds}[0]+int(${bounds}[2]/2)+${offsetx}
	${y}= 	Evaluate 	${bounds}[1]+int(${bounds}[3]/2)+${offsety}
	@{coordinates}= 	Create List 	${x} 	${y}
	Move To 	${coordinates}
	Click
	Run Keyword IF 	${debug_screenshots} 	Take A Screenshot

Get Text Value To Right Of
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}= 	Set Variable		reporter_${platform}_label_${labell}.png

	Wait For 	${img} 	 timeout=${default_image_timeout}

	Make Clipboard Not None 	# reset clipboard
	${b4value}= 	Get Clipboard Content
	Click To The Right Of Image 	${img} 	${offsetx}
	Sleep    10 ms
	Click To The Right Of Image 	${img} 	${offsetx}
	Sleep    10 ms
	${value}= 	Copy From The Right Of 	${img} 	${offsetx}
	Take A Screenshot
	WHILE 	$b4value == $value 		limit=15
		Wait For 	${img} 	 timeout=${default_image_timeout}
		${offsetx}= 	Evaluate 	${offsetx}+10
		Click To The Right Of Image 	${img} 	${offsetx}
		${value}= 	Copy From The Right Of 	${img} 	${offsetx}
		# Take A Screenshot
		${valuec}= 	Copy
		IF  $valuec != $value
			${value}= 	Set Variable 		${valuec}
		END
		${valueg}= 	Get Clipboard Content
		IF  $valueg != $value
			${value}= 	Set Variable 		${valueg}
		END
		IF 	$platform == 'macos' and $b4value == $value
			# Click To The Right Of Image 	${img} 	${offsetx}
			# Sleep    10 ms
			# Click To The Right Of Image 	${img} 	${offsetx}
			# Sleep    10 ms
			# Take A Screenshot
			Click To The Right Of Image 	${img} 	${offsetx} 	clicks=3
			# Take A Screenshot
			Press Combination 	KEY.command 	KEY.c
			# Press Combination 	KEY.command 	KEY.v
			Sleep    10 ms
			# Take A Screenshot
			# Press Combination 	KEY.command 	KEY.v
			# Sleep    10 ms
			# Take A Screenshot
			${valueg}= 	Get Clipboard Content
			IF  $valueg != $value
				${value}= 	Set Variable 		${valueg}
			END

			# ${valueclp}= 	Evaluate 		pyperclip.paste() 		modules=pyperclip
			# IF  $valueclp != $value
			# 	${value}= 	Set Variable 		${valueclp}
			# END

		END
	END
	RETURN 	${value}

Set Text Value To Right Of
	[Arguments]		${label} 	${value} 	${offsetx}=50 	${offsety}=0
	Log		${offsetx}
	${value}= 	Convert To String 	${value}
	${comp}= 	Convert To Lower Case 	${COMPONENT}
	${labell}= 	Convert To Lower Case 	${label}
	${img}= 	Set Variable		${comp}_${platform}_label_${labell}.png
	${imgsize}= 	Get Image Size 	${IMAGE_DIR}${/}${img}
	Log		${imgsize}
	${offsetx2}= 	Evaluate 	int(${imgsize}[0]/2)+${offsetx}
	Log		${offsetx}
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	${x}= 	Evaluate 	${coordinates}[0]+${offsetx2}
	${y}= 	Evaluate 	${coordinates}[1]+${offsety}
	@{coordinates}= 	Create List 	${x} 	${y}
	Move To 	${coordinates}
	# Triple Click is broken on MacOS: TypeError: not enough arguments for format string
	# Triple Click 		button=left 	interval=0.0
	Click
	Sleep 	0.3
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Press Combination	KEY.ctrl		KEY.a
	END
	Take A Screenshot
	Sleep 	0.3
	# Double Click
	# Take A Screenshot

	# @{characters}= 	Split String 	${value} 	separator=${SPACE}
	# ${len} 	Get Length 	${characters}
	# FOR  ${i}  IN RANGE  0  ${len}
	# 	Type 	${characters}[${i}]
	# 	Sleep 	0.1s
	# 	IF  not ${i+1} == ${len}
	# 		Type 	${SPACE}
	# 	END
	# 	Sleep 	0.1s
	# END

	Evaluate 	clipboard.copy("${value}") 	modules=clipboard
	IF  "${platform}" == "macos"
		Press Combination	KEY.command		KEY.v
	ELSE
		Press Combination	KEY.ctrl		KEY.v
	END
	# Type 	${value}
	Take A Screenshot
	IF 	$platform == 'macos'
		# Take A Screenshot

		# Press Combination 	Key.Home
		Press Combination 	Key.Shift 	Key.End

		# Take A Screenshot
		# Type 	${value}
		Press Combination 	Key.Delete
		# Take A Screenshot

	ELSE
		${value2}= 	Get Text Value To Right Of		${label} 		${offsetx}
		WHILE 	$value2 != $value 		limit=10
			Log 	${value2} != ${value}
			${x}= 	Evaluate 	${x}+10
			${offsetx}= 	Evaluate 	${offsetx}+10
			@{coordinates}= 	Create List 	${x} 	${y}
			Move To 	${coordinates}
			Click
			Take A Screenshot
			Double Click
			Take A Screenshot
			Evaluate 	clipboard.copy("${value}") 	modules=clipboard
			IF  "${platform}" == "macos"
				Press Combination	KEY.command		KEY.v
			ELSE
				Press Combination	KEY.ctrl		KEY.v
			END
			Take A Screenshot
			${value2}= 	Get Text Value To Right Of		${label} 		${offsetx}
		END
		Should Be Equal As Strings    ${value}    ${value2}
	END

