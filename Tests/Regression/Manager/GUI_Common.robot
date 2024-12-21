*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library		Collections
Library		DateTime
Library		XML

Library		ImageHorizonLibrary	reference_folder=${IMAGE_DIR}

Library 	ini_file.py
Library 	get_ip_address.py

# Attempting to record video cause more trouble than help
# Library		ScreenRecorderLibrary.py


*** Variables ***
${default_image_timeout} 	${120}
${platform}		None
${platform}		ubuntu
${global_path}	None
${global_name}	None
@{mngr_options}		None
@{agent_options}	None
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm-manager
${IMAGE_DIR} 	${CURDIR}/Images/file_method
${pyfile_manager}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${pyfile_agent}			${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${process_manager}		None
${process_agent}		None
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

Open Agent
	[Arguments]		${options}=None
	IF  ${options} == None
		${options}= 	Create List
		Append To List 	${options} 	-d 	${agent_dir}
	END
	Log to console 	${\n}\${options}: ${options}
	${process}= 	Start Process 	${cmd_agent}  @{options}    alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Open Manager GUI
	[Arguments]		${options}=None
	# Press Escape and move mouse because on linux the screen save had kicked in
	Press Combination 	Key.esc
	Wiggle Mouse

	IF  ${options} == None
		${options}= 	Create List
		Create Directory 	${results_dir}
		Append To List 	${options} 	-d 	${results_dir}
	END
	Log to console 	${\n}\${options}: ${options}
	Set Confidence		0.9
	${process}= 	Start Process 	${cmd_manager}  @{options}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}
	# Sleep 	10
	Set Screenshot Folder 	${OUTPUT DIR}
	# Take A Screenshot
	${result}= 	Wait Until Keyword Succeeds 	${default_image_timeout} sec 	500ms 	Process Should Be Running 	${process_manager}
	Log		Process Is Running: ${result} 		console=True

	IF 	'-n' in ${options}
		Sleep 	10
	ELSE IF 	'-r' in ${options} or '--run' in ${options}
		Handle Donation Reminder
	ELSE
		Handle Donation Reminder

		${img}=	Set Variable		manager_${platform}_button_runschedule.png
		${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=${default_image_timeout / 2}
		IF 	not ${passed}
			${running}= 	Is Process Running 	${process_manager}
			IF 	not ${running}
				${result} = 	Get Process Result

				Log		rc: ${result.rc} 		console=True
				Log		stdout: ${result.stdout} 		console=True
				Log		stderr: ${result.stderr} 		console=True
				Log		stdout_path: ${result.stdout_path} 		console=True
				Log		stderr_path: ${result.stderr_path} 		console=True

				Show Log 	${result.stdout_path}
				Show Log 	${result.stderr_path}

				Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
				Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

				Fail 		Manager not running
			ELSE
				Wait For 	${img} 	 timeout=${default_image_timeout / 2}
			END
		END
	END

Wiggle Mouse
	Move To 	10 	10
	Move To 	20 	20

Handle Donation Reminder
	${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		${default_image_timeout / 2}
	VAR 	${DonationReminder} 	${found} 		scope=TEST

Close Manager GUI ubuntu
	Run Keyword And Ignore Error 	Click Dialog Button 	cancel 		0.01
	Run Keyword And Ignore Error 	Click Dialog Button 	no 		0.01
	Close Manager GUI

Close Manager GUI windows
	Run Keyword And Ignore Error 	Click Dialog Button 	cancel 		0.01
	Run Keyword And Ignore Error 	Click Dialog Button 	no 		0.01
	Close Manager GUI

Close Manager GUI
	[Tags]	windows-latest		ubuntu-latest
	# make sure the window is the active window first, Unlikely the about tab has been selected
	Run Keyword And Ignore Error 	Click Tab 	 About
	Run Keyword And Ignore Error 	Click Tab 	 Run
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	Sleep	5
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Press Combination 	Key.esc
		Press Combination 	x 	Key.ctrl
		Sleep	3
		Run Keyword And Ignore Error 	Click Dialog Button		no 		10
	END
	${result}= 		Wait For Process 	${process_manager} 	timeout=55
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Log		${result.stdout}
		Log		${result.stderr}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Log 	${result.stdout}
		Log 	${result.stderr}
		${running}= 	Is Process Running 	${process_manager}
		Take A Screenshot
		IF 	${running}
			Fail
		END
	END
	Kill Manager If Still Running
	# stdout=${OUTPUT DIR}${/}stdout_manager.txt    stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

Close Manager GUI macos
	[Tags]	macos-latest
	# Sleep	3
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Run Keyword And Ignore Error 	Click Dialog Button 	cancel 		0.01
		Run Keyword And Ignore Error 	Click Dialog Button 	no 		0.01
		# make sure the window is the active window first, Unlikely the about tab has been selected
		Run Keyword And Ignore Error 	Click Tab 	 About
		Run Keyword And Ignore Error 	Click Tab 	 Run
		# Click Image		manager_${platform}_titlebar_rfswarm.png
		Click Button	closewindow
		# Sleep	3
		Run Keyword And Ignore Error 	Click Dialog Button		no 		1
	END
	${result}= 		Wait For Process 	${process_manager} 	timeout=55
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Log 	${result.stdout}
		Log 	${result.stderr}
		Should Be Equal As Integers 	${result.rc} 	0
		Take A Screenshot
		Log		${result.stdout}
		Log		${result.stderr}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Log 	${result.stdout}
		Log 	${result.stderr}
		${running}= 	Is Process Running 	${process_manager}
		Take A Screenshot
		IF 	${running}
			Fail
		END
	END
	Kill Manager If Still Running
	Show Log 	${OUTPUT DIR}${/}stdout_manager.txt
	Show Log 	${OUTPUT DIR}${/}stderr_manager.txt

Kill Manager If Still Running
	Kill If Still Running 	${cmd_manager}

Stop Agent
	${running}= 	Is Process Running 	${process_agent}
	IF 	${running}
		Sleep	3s
		IF  '${platform}' == 'windows'	# Send Signal To Process keyword does not work on Windows
			${result} = 	Terminate Process		${process_agent}
		ELSE
			Send Signal To Process 	SIGINT 	${process_agent}
			${result}= 	Wait For Process 	${process_agent}	timeout=30	on_timeout=kill
		END
		Log		${result.stdout}
		Log		${result.stderr}
		# Should Be Equal As Integers 	${result.rc} 	0
	END

	Kill Agent If Still Running
	#	 stdout=${OUTPUT DIR}${/}stdout_agent.txt    stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Show Log 	${OUTPUT DIR}${/}stdout_agent.txt
	Show Log 	${OUTPUT DIR}${/}stderr_agent.txt

Kill Agent If Still Running
	Kill If Still Running 	${cmd_agent}

Kill If Still Running
	[Arguments]		${cmdname}
	${processes}= 	Evaluate    list(psutil.process_iter()) 	modules=psutil
	# Log		${processes}
	FOR 	${p} 	IN 	@{processes}
		# Log		${p}
		TRY
			IF 	$cmdname in $p.name()
				Evaluate    $p.kill()
			END
		EXCEPT               # Match any error.
			No Operation
    END
	END

Show Log
	[Arguments]		${filename}
	Log 		${\n}--VVV--${filename}--VVV-- 		console=True
	${filedata}= 	Get File 	${filename} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata} 		console=True
	Log 		--ɅɅɅ--${filename}--ɅɅɅ--${\n} 		console=True
	RETURN 		${filedata}


Stop Test Scenario Run Gradually
	[Arguments]	${rumup_time}	${robot_test_time}
	Set Confidence	0.95
	Wait For	manager_${platform}_robots_10.png 	timeout=${rumup_time + ${default_image_timeout}}
	Click Button	stoprun
	${START_TIME}=	Get Current Date
	Wait For	manager_${platform}_robots_0.png 	timeout=${robot_test_time + ${default_image_timeout}}
	Set Confidence	0.9
	# Take A Screenshot
	${END_TIME}=	Get Current Date
	${ELAPSED_TIME}=	Subtract Date From Date	${END_TIME}	${START_TIME}
	Should Be True	${ELAPSED_TIME} >= ${robot_test_time / 2} and ${ELAPSED_TIME} <= ${robot_test_time + 90}

	Press Key.tab 2 Times
	Move To	10	10
	# Take A Screenshot
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${robot_test_time + ${default_image_timeout}}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

Stop Test Scenario Run Quickly
	[Arguments]	${rumup_time}	${robot_test_time}
	Set Confidence	0.95
	Wait For	manager_${platform}_robots_10.png 	timeout=${rumup_time + ${default_image_timeout}}
	Click Button	stoprun
	Sleep	2
	Click
	Press Key.enter 1 Times
	${START_TIME}=	Get Current Date
	Wait For	manager_${platform}_robots_0.png 	timeout=${robot_test_time + 60}
	Set Confidence	0.9
	# Take A Screenshot
	${END_TIME}=	Get Current Date
	${ELAPSED_TIME}=	Subtract Date From Date	${END_TIME}	${START_TIME}
	Should Be True	${ELAPSED_TIME} <= ${robot_test_time / 2}

	Press Key.tab 2 Times
	Move To	10	10
	# Take A Screenshot
	${status}=	Run Keyword And Return Status
	...    Wait For	manager_${platform}_button_finished_run.png 	timeout=${robot_test_time + ${default_image_timeout}}
	Run Keyword If	not ${status}	Fail	msg=Test didn't finish as fast as expected. Check screenshots for more informations.

Utilisation Stats
	${cpupct}= 	Evaluate 	psutil.cpu_percent(interval=1, percpu=True) 				modules=psutil
	Log 	\n${cpupct} 	console=True
	${loadavg}= 	Evaluate 	psutil.getloadavg() 															modules=psutil
	Log 	${loadavg} 	console=True
	${mem}= 		Evaluate 	psutil.virtual_memory() 														modules=psutil
	Log 	${mem}
	${proc}= 		Evaluate 	list(psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username'])) 		modules=psutil
	Log 	${proc}

Check If The Agent Is Ready
	[Arguments] 	${timeout}=300
	# Sleep	1
	Click Tab	Agents
	Wait For 	manager_${platform}_agents_ready.png	timeout=${timeout}

Check If the Robot Failed
	[Arguments] 	${expected_time}
	Sleep	${expected_time}
	TRY
		Click Image 	manager_${platform}_button_abort
		Press Combination	Key.enter
	EXCEPT
		Wait For	manager_${platform}_button_finished_run.png	timeout=${default_image_timeout}
	END
	# Take A Screenshot
	${status}=	Run Keyword And Return Status	Locate	manager_${platform}_resource_file_provided.png
	Run Keyword If	not ${status}	Fail	msg=Test failed. Check screenshots for more informations.

Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		manager_${platform}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Select Option
	[Arguments]		${optname}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}=	Set Variable		manager_${platform}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Take A Screenshot

Selected Option Should Be
	[Arguments]		${optname}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}=	Set Variable		manager_${platform}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}


Click Button
	[Arguments]		${btnname} 		${timeout}=${default_image_timeout}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		manager_${platform}_button_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Click Menu
	[Arguments]		${menuname}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	${img}=	Set Variable		manager_${platform}_menu_${menunamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=${default_image_timeout}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_dlgbtn_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Click CheckBox
	[Arguments]		${status} 		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		${platform}_checkbox_${statusl}_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Click RadioBtn
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_radiobtn_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	1
	Take A Screenshot

Press ${key} ${n} Times
	[Documentation]	Provide full name. For example: Key.tab
	Sleep	1
	FOR  ${i}  IN RANGE  0  ${n}
		Press Combination 	${key}
	END

Click Label With Vertical Offset
	[Arguments]		${labelname}	${offset}=0
	[Documentation]	Click the image with the offset
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	...	Give the image a full name, for example: button_runopen.
	${labelname}= 	Convert To Lower Case 	${labelname}
	${img}=	Set Variable		manager_${platform}_label_${labelname}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1
	# Take A Screenshot

Click Label With Horizontal Offset
	[Arguments]		${labelname}	${offset}=0
	[Documentation]	Click the image with the offset
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right].
	...	Give the image a full name, for example: button_runopen.
	${labelname}= 	Convert To Lower Case 	${labelname}
	${img}=	Set Variable		manager_${platform}_label_${labelname}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1
	# Take A Screenshot

#TODO: Chceck if it works
Resize Window
	[Arguments]		${x}=0		${y}=0
	# 											manager_macos_corner_resize
	${img}=	Set Variable		manager_${platform}_corner_resize.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	@{coordinates2}= 	Create List 	${{${coordinates[0]}+${x}}} 	${{${coordinates[1]}+${y}}}
	Move To 	@{coordinates}
	Mouse Down
	Move To 	@{coordinates2}
	# Take A Screenshot
	Mouse Up

Wait Agent Ready
	Click Tab 	 Agents
	${img}=	Set Variable		manager_${platform}_agents_ready.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

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

Create Robot File
	[Arguments]		${path}=${global_path}	${name}=${global_name}
	...    ${file_content}=***Test Case***\nExample Test Case\n

	${example_robot_content}=	Set Variable	${file_content}
	Variable Should Exist	${path}	msg="Global save path does not exist or path is not provided."
	Variable Should Exist	${name}	msg="Global file name does not exist or file name is not provided."
	Create File		${path}${/}${name}	content=${example_robot_content}
	File Should Exist	${path}${/}${name}

Clear Manager Result Directory
	[Arguments]		${results_dir}=${results_dir}
	@{run_result_dirs}=		List Directories In Directory	${results_dir}	absolute=${True}
	FOR  ${dir}  IN  @{run_result_dirs}
		Remove Directory	${dir}	recursive=${True}
	END

Change Test Group Settings
	[Arguments]		${row_settings_data}
	Sleep	2
	#Click Dialog Button		row_settings_frame_name
	IF  'exclude_libraries' in ${row_settings_data}
		Click Label With Vertical Offset	exclude_libraries	20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${row_settings_data['exclude_libraries']}
	END
	IF  'robot_options' in ${row_settings_data}
		Click Label With Vertical Offset	robot_options		20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${row_settings_data['robot_options']}
	END
	IF  'inject_sleep_min' in ${row_settings_data}
		Click Label With Vertical Offset	inject_sleep_min	20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${row_settings_data['inject_sleep_min']}
	END
	IF  'inject_sleep_max' in ${row_settings_data}
		Click Label With Vertical Offset	inject_sleep_max	20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${row_settings_data['inject_sleep_max']}
	END
	IF  'test_repeater' in ${row_settings_data}
		IF  '${row_settings_data['test_repeater']}' == 'True'
			Click CheckBox	unchecked	default
		ELSE IF  '${row_settings_data['test_repeater']}' == 'False'
			Click CheckBox	checked	default
		END
	END
	IF  'inject_sleep' in ${row_settings_data}
		IF  '${row_settings_data['inject_sleep']}' == 'True'
			Click CheckBox	unchecked	injectsleep
		ELSE IF  '${row_settings_data['inject_sleep']}' == 'False'
			Click CheckBox	checked		injectsleep
		END
	END
	# TODO: disableloglog, disablelogreport, disablelogoutput

	Test Group Save Settings

Change Scenario Wide Settings
	[Arguments]		${wide_settings_data}
	Sleep	2
	#Click Label With Vertical Offset	scenario_settings_scenario
	IF  'exclude_libraries' in ${wide_settings_data}
		Click Label With Horizontal Offset	exclude_libraries	100
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['exclude_libraries']}
	END
	IF  'robot_options' in ${wide_settings_data}
		Click Label With Horizontal Offset	robot_options		100
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['robot_options']}
	END
	IF  'inject_sleep_min' in ${wide_settings_data}
		Click Label With Vertical Offset	inject_sleep_min	20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['inject_sleep_min']}
	END
	IF  'inject_sleep_max' in ${wide_settings_data}
		Click Label With Vertical Offset	inject_sleep_max	20
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['inject_sleep_max']}
	END
	IF  'bind_ip_address' in ${wide_settings_data}
		Click Label With Horizontal Offset	bind_ip_address		100
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['bind_ip_address']}
	END
	IF  'bind_port_number' in ${wide_settings_data}
		Click Label With Horizontal Offset	bind_port_number	100
		IF  "${platform}" == "macos"
			Press Combination	KEY.command		KEY.a
		ELSE
			Double Click
		END
		Type	${wide_settings_data['bind_port_number']}
	END
	IF  'upload_logs' in ${wide_settings_data}
		Click Button	on_error_only
		IF  '${wide_settings_data['upload_logs']}' == 'on_error_only'
			Press Key.down 2 Times
			Press Combination	Key.enter
		ELSE IF  '${wide_settings_data['upload_logs']}' == 'immediately'
			Press Key.down 1 Times
			Press Combination	Key.enter
		ELSE IF  '${wide_settings_data['upload_logs']}' == 'all_deferred'
			Press Key.down 3 Times
			Press Combination	Key.enter
		END
	END
	IF  'test_repeater' in ${wide_settings_data}
		IF  '${wide_settings_data['test_repeater']}' == 'True'
			Click CheckBox	unchecked	default
		ELSE IF  '${wide_settings_data['test_repeater']}' == 'False'
			Click CheckBox	checked	default
		END
	END
	IF  'inject_sleep' in ${wide_settings_data}
		IF  '${wide_settings_data['inject_sleep']}' == 'True'
			Click CheckBox	unchecked	injectsleep
		ELSE IF  '${wide_settings_data['inject_sleep']}' == 'False'
			Click CheckBox	checked		injectsleep
		END
	END
	# TODO: disableloglog, disablelogreport, disablelogoutput

	Click Button	ok

Test Group Save Settings
	IF 	"${platform}" == "macos"
		Click Dialog Button		save_2
	ELSE
		Click Dialog Button		save
	END

Change ${str1} With ${str2} In ${file}
	${file_content}	Get File	${file}
	Remove File		${file}
	${file_content}	Replace String	${file_content}	${str1}	${str2}
	Create File		${file}	${file_content}

Select ${n} Robot Test Case
	Click Button	select_test_case
	Press Key.down ${n} Times
	Press Combination	Key.enter

Select Robot File OS DIALOG
	[Arguments]		${robot_file_name}
	Sleep	5
	Type	${robot_file_name}
	# Take A Screenshot
	Click Dialog Button		open
	Sleep	1

Save Scenario File OS DIALOG
	[Arguments]		${scenario_name}
	Sleep	5
	Type	${scenario_name}
	# Take A Screenshot
	Click Dialog Button		save
	Sleep	1

Open Scenario File OS DIALOG
	[Arguments]		${scenario_name}
	Sleep	5
	Type	${scenario_name}.rfs
	# Take A Screenshot
	Click Dialog Button		open
	Sleep	1

Get Scenario File Content
	[Arguments]		${path}		${scenario_name}
	${scenario_content}=	Get File	${path}${/}${scenario_name}.rfs
	Should Not Be Empty	${scenario_content}

	RETURN	${scenario_content}

Delete Scenario File
	[Arguments]		${scenario_name}
	Remove File		${global_path}${/}${scenario_name}.rfs
	File Should Not Exist	${global_path}${/}${scenario_name}.rfs

Delete Robot File
	[Arguments]		${path}=${global_path}	${name}=${global_name}
	Variable Should Exist	${path}	msg="Global save path does not exist or path is not provided."
	Variable Should Exist	${name}	msg="Global file name does not exist or file name is not provided"
	Remove File		${path}${/}${name}
	File Should Not Exist	${path}${/}${name}

Find Absolute Paths And Names For Files In Directory
	[Documentation]	This algorithm analyses the specified path and returns all
	...    file names with their absolute paths even those that are in subdirectories
	[Arguments]		${given_path}	@{excluded_files}
	${example_dir}	Set Variable	${given_path}
	@{absolute_paths}	Create List
	@{file_names}	Create List

	${new_dir}		List Directories In Directory	${example_dir}	absolute=${True}
	#=== Collecting data section

	@{dir_files_path}=		List Files In Directory		${example_dir}	absolute=${True}
	@{dir_file_names}=		List Files In Directory		${example_dir}

	${length}	Get Length	${dir_files_path}
	FOR  ${i}  IN RANGE  0  ${length}
		IF  '${dir_file_names}[${i}]' not in ${excluded_files}
			Append To List	${absolute_paths}	${dir_files_path}[${i}]
			Append To List	${file_names}	${dir_file_names}[${i}]
		END
	END
	#=== Merging data section
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

Compare Manager and Agent Files
	[Arguments]	${M_file_names}	${A_file_names}
	Log To Console	\n${M_file_names}
	Log To Console	${A_file_names}\n
	Lists Should Be Equal	${M_file_names}	${A_file_names}
	...    msg="Files are not transferred correctly! Check report for more information."

Compare Manager and Agent Files Content
	[Arguments]	${M_absolute_paths}	${A_absolute_paths}
	${length}	Get Length	${M_absolute_paths}
	@{excluded_files_format}	Create List	png		jpg		xlsx	pdf
	FOR  ${i}  IN RANGE  0  ${length}
		${file_extension}	Split String From Right	${M_absolute_paths}[${i}]	separator=.
		IF  '${file_extension}[-1]' not in @{excluded_files_format}
			${M_file_content}	Get File	${M_absolute_paths}[${i}]
			${A_file_content}	Run Keyword And Continue On Failure
			...    Get File	${A_absolute_paths}[${i}]

			Run Keyword And Continue On Failure
			...    Should Be Equal	${M_file_content}	${A_file_content}
		END
	END

Get Relative Paths
	[Arguments] 	${base} 		${paths_in}

	${paths_out}= 	Create List
	FOR 	${item} 	IN 		@{paths_in}
		${relpath}= 	Evaluate     os.path.relpath(r"${item}", start=r"${base}") 	modules=os.path
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

Verify Scenario File Robots
	[Arguments]		${scenario_content_list}	${run_robots}	${start_group}	${end_group}
	FOR  ${rows}  IN RANGE  ${start_group}	${end_group + 1}
		${row}	Set Variable	[${rows}]	#[1], [2], [3]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		IF  '${i}' == '-1'
			Fail	msg=Cant find index ${row} in scenario file!
		END
		Log		${row}

		${robots_offset}	Get Index From List 	${scenario_content_list}	robots	start=${i}
		Should Be Equal		robots	${scenario_content_list}[${robots_offset}]	msg=Robots is missing!
		Should Be Equal		${run_robots}[${rows - 1}]	${scenario_content_list}[${robots_offset + 2}]
		...    msg=Robots value did not save correctly [settings != scenario]!
	END

Verify Scenario File Times
	[Arguments]		${scenario_content_list}	${run_times_in_s}	${start_group}	${end_group}
	FOR  ${rows}  IN RANGE  ${start_group}	${end_group + 1}
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		IF  '${i}' == '-1'
			Fail	msg=Cant find index ${row} in scenario file!
		END
		Log		${row}
		${time_indx}=	Evaluate	${rows - 1}*3

		${delay_offset}		Get Index From List 	${scenario_content_list}	delay	start=${i}
		Should Be Equal		delay	${scenario_content_list}[${delay_offset}]	msg=Delay is missing!
		Should Be Equal		${run_times_in_s}[${time_indx}]		${scenario_content_list}[${delay_offset + 2}]
		...    msg=Delay time value did not save correctly [settings != scenario]!

		${rampup_offset}	Get Index From List 	${scenario_content_list}	rampup	start=${i}
		Should Be Equal		rampup	${scenario_content_list}[${rampup_offset}]	msg=Rampup is missing!
		Should Be Equal		${run_times_in_s}[${time_indx + 1}]		${scenario_content_list}[${rampup_offset + 2}]
		...    msg=Rump-up time value did not save correctly [settings != scenario]!

		${run_offset}		Get Index From List 	${scenario_content_list}	run	start=${i}
		Should Be Equal		run		${scenario_content_list}[${run_offset}]		msg=Run is missing!
		Should Be Equal		${run_times_in_s}[${time_indx + 2}]		${scenario_content_list}[${run_offset + 2}]
		...    msg=Run time value did not save correctly [settings != scenario]!
	END

Verify Scenario File Robot Data
	[Arguments]		${scenario_content_list}	${robot_data}	${start_group}	${end_group}
	FOR  ${rows}  IN RANGE  ${start_group}	${end_group + 1}
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		IF  '${i}' == '-1'
			Fail	msg=Cant find index ${row} in scenario file!
		END
		Log		${row}

		${test_offset}		Get Index From List 	${scenario_content_list}	test	start=${i}
		Should Be Equal		test	${scenario_content_list}[${test_offset}]	msg=Test is missing!

		${next_equal_offset}		Get Index From List
		...    ${scenario_content_list}	=	start=${test_offset + 2}
		@{test_name}	Create List
		FOR  ${j}  IN RANGE  0  ${next_equal_offset - 1} - ${test_offset} - ${2}
			Append To List	${test_name}	${scenario_content_list[${test_offset + 2 + ${j}}]}
		END
		${test_name}=	Catenate	@{test_name}

		Should Be Equal		${robot_data}[1]	${test_name}
		...    msg=Robot test file name did not save correctly [settings != scenario]!

		${script_offset}		Get Index From List 	${scenario_content_list}	script	start=${i}
		Should Be Equal		script	${scenario_content_list}[${script_offset}]	msg=Script is missing!
		Should Be Equal		${robot_data}[0]	${scenario_content_list}[${script_offset + 2}]
		...    msg=Robot script name did not save correctly [settings != scenario]!
	END

Verify Scenario Test Row Settings
	[Arguments]		${scenario_content_list}	${row_settings_data}	${start_group}	${end_group}
	FOR  ${rows}  IN RANGE  ${start_group}	${end_group + 1}
		${row}	Set Variable	[${rows}]
		${i}=	Get Index From List		${scenario_content_list}		${row}
		IF  '${i}' == '-1'
			Fail	msg=Cant find index ${row} in scenario file!
		END
		Log		${row}

		IF  'exclude_libraries' in ${row_settings_data}
			${exlibraries_offset}	Get Index From List 	${scenario_content_list}	excludelibraries	start=${i}
			Should Be Equal		excludelibraries	${scenario_content_list}[${exlibraries_offset}]
			...    msg=Exclude Libraries are missing!

			${next_equal_offset}		Get Index From List
			...    ${scenario_content_list}	=	start=${exlibraries_offset + 2}
			@{exlibraries}	Create List
			FOR  ${j}  IN RANGE  0  ${next_equal_offset - 1} - ${exlibraries_offset} - ${2}
				Append To List	${exlibraries}	${scenario_content_list[${exlibraries_offset + 2 + ${j}}]}
			END
			${exlibraries}=	Catenate	@{exlibraries}

			Should Be Equal		${row_settings_data['exclude_libraries']}	${exlibraries}
			...    msg=Exclude Libraries did not save correctly [settings != scenario]!
		END

		IF  'robot_options' in ${row_settings_data}
			${robot_options_offset}		Get Index From List		${scenario_content_list}	robotoptions	start=${i}
			Should Be Equal		robotoptions	${scenario_content_list}[${robot_options_offset}]
			...    msg=Robot Options are missing!

			${next_equal_offset}		Get Index From List
			...    ${scenario_content_list}	=	start=${robot_options_offset + 2}
			@{robot_options}	Create List
			FOR  ${j}  IN RANGE  0  ${next_equal_offset - 1} - ${robot_options_offset} - ${2}
				Append To List	${robot_options}	${scenario_content_list[${robot_options_offset + 2 + ${j}}]}
			END
			${robot_options}=	Catenate	@{robot_options}

			Should Be Equal		${row_settings_data['robot_options']}	${robot_options}
			...    msg=Robot options did not save correctly [settings != scenario]!
		END

		IF  'test_repeater' in ${row_settings_data}
			${repeater_offset}		Get Index From List		${scenario_content_list}	testrepeater	start=${i}
			Should Be Equal		testrepeater	${scenario_content_list}[${repeater_offset}]
			...    msg=Test Repeater is missing!
			Should Be Equal		${row_settings_data['test_repeater']}	${scenario_content_list}[${repeater_offset + 2}]
			...    msg=Test repeater did not save correctly [settings != scenario]!
		END

		IF  'inject_sleep' in ${row_settings_data}
			${injectsleep_offset}		Get Index From List		${scenario_content_list}	injectsleepenabled	start=${i}
			Should Be Equal		injectsleepenabled	${scenario_content_list}[${injectsleep_offset}]
			...    msg=Inject Sleep Enabled is missing!
			Should Be Equal		${row_settings_data['inject_sleep']}	${scenario_content_list}[${injectsleep_offset + 2}]
			...    msg=Inject sleep enabled did not save correctly [settings != scenario]!
		END

		IF  'inject_sleep_min' in ${row_settings_data}
			${injectsleep_min_offset}		Get Index From List		${scenario_content_list}	injectsleepminimum 	start=${i}
			Should Be Equal		injectsleepminimum 	${scenario_content_list}[${injectsleep_min_offset}]
			...    msg=Inject Sleep Minimum is missing!
			Should Be Equal		${row_settings_data['inject_sleep_min']}	${scenario_content_list}[${injectsleep_min_offset + 2}]
			...    msg=Inject sleep minimum did not save correctly [settings != scenario]!
		END

		IF  'inject_sleep_max' in ${row_settings_data}
			${injectsleep_max_offset}		Get Index From List		${scenario_content_list}	injectsleepmaximum 	start=${i}
			Should Be Equal		injectsleepmaximum 	${scenario_content_list}[${injectsleep_max_offset}]
			...    msg=Inject Sleep Maximum is missing!
			Should Be Equal		${row_settings_data['inject_sleep_max']}	${scenario_content_list}[${injectsleep_max_offset + 2}]
			...    msg=Inject sleep maximum did not save correctly [settings != scenario]!
		END

		IF  'disablelog_log' in ${row_settings_data}
			${disablelog_log_offset}		Get Index From List		${scenario_content_list}	disableloglog	start=${i}
			Should Be Equal		disableloglog	${scenario_content_list}[${disablelog_log_offset}]
			...    msg=Disablelog log.html is missing!
			Should Be Equal		${row_settings_data['disablelog_log']}		${scenario_content_list}[${disablelog_log_offset + 2}]
			...    msg=Disablelog Robot Logs: log.html did not save correctly [settings != scenario]!
		END

		IF  'disablelog_report' in ${row_settings_data}
			${disablelog_report_offset}		Get Index From List		${scenario_content_list}	disablelogreport	start=${i}
			Should Be Equal		disablelogreport	${scenario_content_list}[${disablelog_report_offset}]
			...    msg=Disablelog report.html is missing!
			Should Be Equal		${row_settings_data['disablelog_report']}		${scenario_content_list}[${disablelog_report_offset + 2}]
			...    msg=Disablelog Robot Logs: report.html did not save correctly [settings != scenario]!
		END

		IF  'disablelog_output' in ${row_settings_data}
			${disablelog_output_offset}		Get Index From List		${scenario_content_list}	disablelogoutput	start=${i}
			Should Be Equal		disablelogoutput	${scenario_content_list}[${disablelog_output_offset}]
			...    msg=Disablelog output.xml is missing!
			Should Be Equal		${row_settings_data['disablelog_output']}		${scenario_content_list}[${disablelog_output_offset + 2}]
			...    msg=Disablelog Robot Logs: output.xml did not save correctly [settings != scenario]!
		END
	END
	# TODO: Agent filter

Verify Scenario Wide Settings Data
	[Arguments]		${scenario_content_list}	${wide_settings_data}
	${i}=	Get Index From List		${scenario_content_list}	Defaults]
	${first_group}=	Get Index From List		${scenario_content_list}		[1]

	IF  'exclude_libraries' in ${wide_settings_data}
		${exlibraries_offset}	Get Index From List 	${scenario_content_list}	excludelibraries	start=${i}	end=${first_group}
		Should Be Equal		excludelibraries	${scenario_content_list}[${exlibraries_offset}]
		...    msg=Exclude Libraries are missing!

		${next_equal_offset}		Get Index From List
		...    ${scenario_content_list}	=	start=${exlibraries_offset + 2}
		@{exlibraries}	Create List
		FOR  ${j}  IN RANGE  0  ${next_equal_offset - 1} - ${exlibraries_offset} - ${2}
			Append To List	${exlibraries}	${scenario_content_list[${exlibraries_offset + 2 + ${j}}]}
		END
		${exlibraries}=	Catenate	@{exlibraries}

		Should Be Equal		${wide_settings_data['exclude_libraries']}	${exlibraries}
		...    msg=Exclude Libraries did not save correctly [settings != scenario]!
	END

	IF  'robot_options' in ${wide_settings_data}
		${robot_options_offset}		Get Index From List		${scenario_content_list}	robotoptions	start=${i}	end=${first_group}
		Should Be Equal		robotoptions	${scenario_content_list}[${robot_options_offset}]
		...    msg=Robot options are missing!

		${next_equal_offset}		Get Index From List
		...    ${scenario_content_list}	=	start=${robot_options_offset + 2}
		@{robot_options}	Create List
		FOR  ${j}  IN RANGE  0  ${next_equal_offset - 1} - ${robot_options_offset} - ${2}
			Append To List	${robot_options}	${scenario_content_list[${robot_options_offset + 2 + ${j}}]}
		END
		${robot_options}=	Catenate	@{robot_options}

		Should Be Equal		${wide_settings_data['robot_options']}	${robot_options}
		...    msg=Robot options did not save correctly [settings != scenario]!
	END

	IF  'test_repeater' in ${wide_settings_data}
		${repeater_offset}		Get Index From List		${scenario_content_list}	testrepeater	start=${i}	end=${first_group}
		Should Be Equal		testrepeater	${scenario_content_list}[${repeater_offset}]
		...    msg=Test repeater is missing!
		Should Be Equal		${wide_settings_data['test_repeater']}	${scenario_content_list}[${repeater_offset + 2}]
		...    msg=Test repeater did not save correctly [settings != scenario]!
	END

	IF  'inject_sleep' in ${wide_settings_data}
		${injectsleep_offset}		Get Index From List		${scenario_content_list}	injectsleepenabled	start=${i}	end=${first_group}
		Should Be Equal		injectsleepenabled	${scenario_content_list}[${injectsleep_offset}]
		...    msg=Inject Sleep Enabled is missing!
		Should Be Equal		${wide_settings_data['inject_sleep']}	${scenario_content_list}[${injectsleep_offset + 2}]
		...    msg=Inject sleep enabled did not save correctly [settings != scenario]!
	END

	IF  'inject_sleep_min' in ${wide_settings_data}
		${injectsleep_min_offset}		Get Index From List		${scenario_content_list}	injectsleepminimum 	start=${i}	end=${first_group}
		Should Be Equal		injectsleepminimum 	${scenario_content_list}[${injectsleep_min_offset}]
		...    msg=Inject Sleep Minimum is missing!
		Should Be Equal		${wide_settings_data['inject_sleep_min']}	${scenario_content_list}[${injectsleep_min_offset + 2}]
		...    msg=Inject sleep minimum did not save correctly [settings != scenario]!
	END

	IF  'inject_sleep_max' in ${wide_settings_data}
		${injectsleep_max_offset}		Get Index From List		${scenario_content_list}	injectsleepmaximum 	start=${i}	end=${first_group}
		Should Be Equal		injectsleepmaximum 	${scenario_content_list}[${injectsleep_max_offset}]
		...    msg=Inject Sleep Maximum is missing!
		Should Be Equal		${wide_settings_data['inject_sleep_max']}	${scenario_content_list}[${injectsleep_max_offset + 2}]
		...    msg=Inject sleep maximum did not save correctly [settings != scenario]!
	END

	IF  'disablelog_log' in ${wide_settings_data}
		${disablelog_log_offset}		Get Index From List		${scenario_content_list}	disableloglog	start=${i}	end=${first_group}
		Should Be Equal		disableloglog	${scenario_content_list}[${disablelog_log_offset}]
		...    msg=Disablelog log.html is missing!
		Should Be Equal		${wide_settings_data['disablelog_log']}		${scenario_content_list}[${disablelog_log_offset + 2}]
		...    msg=Disablelog Robot Logs: log.html did not save correctly [settings != scenario]!
	END

	IF  'disablelog_report' in ${wide_settings_data}
		${disablelog_report_offset}		Get Index From List		${scenario_content_list}	disablelogreport	start=${i}	end=${first_group}
		Should Be Equal		disablelogreport	${scenario_content_list}[${disablelog_report_offset}]
		...    msg=Disablelog report.html is missing!
		Should Be Equal		${wide_settings_data['disablelog_report']}		${scenario_content_list}[${disablelog_report_offset + 2}]
		...    msg=Disablelog Robot Logs: report.html did not save correctly [settings != scenario]!
	END

	IF  'disablelog_output' in ${wide_settings_data}
		${disablelog_output_offset}		Get Index From List		${scenario_content_list}	disablelogoutput	start=${i}	end=${first_group}
		Should Be Equal		disablelogoutput	${scenario_content_list}[${disablelog_output_offset}]
		...    msg=Disablelog output.xml is missing!
		Should Be Equal		${wide_settings_data['disablelog_output']}		${scenario_content_list}[${disablelog_output_offset + 2}]
		...    msg=Disablelog Robot Logs: output.xml did not save correctly [settings != scenario]!
	END

Check That The Scenario File Opens Correctly
	[Arguments]		${scenario_name}	${scenario_content}
	Click Button	runsave
	${scenario_content_reopened}=	Get scenario file content	${global_path}	${scenario_name}
	Log		${scenario_content}
	Log		${scenario_content_reopened}
	Should Be Equal		${scenario_content}		${scenario_content_reopened}	msg=Scenario files are not equal!


Start New Scenario
	Click Button	runnew

Create ${lang} Language Scenario
	# [Arguments] 	${langcode}
	# Log 	${lang} 	console=True
	${scenariofile}= 		Set Variable    ${CURDIR}${/}testdata${/}Issue-#238${/}language${/}lang_${lang}.rfs
	${robotfile}= 		Set Variable    ${CURDIR}${/}testdata${/}Issue-#238${/}language${/}lang_${lang}.robot
	${robotfilename}= 		Set Variable    lang_${lang}.robot
	Create File 	${scenariofile} 	[Scenario]\n
	Append To File 	${scenariofile} 	uploadmode = err\n
	Append To File 	${scenariofile} 	scriptcount = 1\n
	Append To File 	${scenariofile} 	graphlist =\n
	Append To File 	${scenariofile} 	\n
	Append To File 	${scenariofile} 	[1]\n
	Append To File 	${scenariofile} 	robots = 2\n
	Append To File 	${scenariofile} 	delay = 300\n
	Append To File 	${scenariofile} 	rampup = 10\n
	Append To File 	${scenariofile} 	run = 60\n
	Append To File 	${scenariofile} 	test = First Test\n
	Append To File 	${scenariofile} 	script = ${robotfilename}\n
	RETURN 	${scenariofile}

Click Script Button On Row
		[Arguments]		${row}
		${rowheight}= 	Set Variable		30
		${rowoffset}= 	Evaluate		${rowheight} * ${row}

		${labelname}= 	Set Variable    script
		${labelname}= 	Convert To Lower Case 	${labelname}
		${img}=	Set Variable		manager_${platform}_label_${labelname}.png

		# Log		${CURDIR}
		# Log		${IMAGE_DIR}
		Wait For 	${img} 	 timeout=${default_image_timeout}
		# @{coordinates}= 	Locate		${img}
		# Log	${coordinates}
		Click To The Below Of Image 	${img} 	 offset=${rowoffset}

		# Take A Screenshot
		Press Key.tab 1 Times
		# Take A Screenshot
		# manager_macos_button_selected_runscriptrow.png
		${img}=	Set Variable		manager_${platform}_button_selected_runscriptrow.png
		Click Image 	${img}
		Sleep    0.1
		# Take A Screenshot
		# 	macos_dlgbtn_open
		${img}=	Set Variable		${platform}_dlgbtn_cancel.png
		Wait For 	${img} 	 timeout=${default_image_timeout}
		# Take A Screenshot

		# Fail 		Not Implimented

File Open Dialogue Select File
	[Arguments]		${filepath}
	Run Keyword		File Open Dialogue ${platform} Select File 			${filepath}
	# Take A Screenshot

File Open Dialogue ubuntu Select File
	[Arguments]		${filepath}
	Sleep	2
	# Take A Screenshot
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath} 	Key.ENTER
	Sleep	0.5
	# Take A Screenshot
	# Click Dialog Button 	open

File Open Dialogue windows Select File
	[Arguments]		${filepath}
	Sleep	3
	# Take A Screenshot
	${filepath}= 	Normalize Path 	${filepath}
	#${path} 	${file} = 	Split Path 	${filepath}
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath}
	Sleep	0.5
	Press key.enter 1 Times
	# Take A Screenshot
	# Click Dialog Button 	open

File Open Dialogue macos Select File
	[Arguments]		${filepath}
	Sleep	3
	# Take A Screenshot
	${filepath}=	Convert To Lower Case	${filepath}
	Evaluate	clipboard.copy("${filepath}")	modules=clipboard		#copy path to clipboard
	Press Combination 	KEY.command 	KEY.shift 	KEY.g
	Press Combination 	KEY.backspace		#clear text filed
	Click Label With Horizontal Offset 	file_name 	-10
	Click	button=right	#show context menu
	Sleep	2
	# Take A Screenshot
	Press Combination 	KEY.down	#choose paste option(should be first)
	Press key.enter 1 Times		#execute paste option
	Sleep	0.5
	# Take A Screenshot
	Press key.enter 1 Times
	Sleep	0.5
	# Take A Screenshot
	Click Dialog Button 	open
	# Type 		Key.BACKSPACE 	Key.DELETE
	# Click Dialog Button 	open

Select Test Script
	[Arguments]		${row}	${filepath}

	Click Script Button On Row 	${row}

	# Click Button	runscriptrow
	# Take A Screenshot
	# Press Key.escape 1 Times

	File Open Dialogue Select File		${filepath}
	# Take A Screenshot
	# Click Dialog Button 	cancel

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

Check Agent Downloaded ${lang} Language Test Files
	${robotfile}= 	Set Variable    ${agent_dir}${/}scripts${/}lang_${lang}.robot
	Wait For File To Exist 		${robotfile}

	# Tests/Regression/Manager/testdata/Issue-#238/language/resource/lang_bg.resource
	${resourcefile}= 	Set Variable    ${agent_dir}${/}scripts${/}resource${/}lang_${lang}.resource
	Wait For File To Exist 		${resourcefile} 	30
	# Tests/Regression/Manager/testdata/Issue-#238/language/resource/lang_bg.json
	${jsonfile}= 	Set Variable    ${agent_dir}${/}scripts${/}resource${/}lang_${lang}.json
	Wait For File To Exist 		${jsonfile} 	30
	# Tests/Regression/Manager/testdata/Issue-#238/language/images/lang_bg.png
	${imgfile}= 	Set Variable    ${agent_dir}${/}scripts${/}images${/}lang_${lang}.png
	Wait For File To Exist 		${imgfile} 	30
	# Tests/Regression/Manager/testdata/Issue-#238/language/images/lang_bg.svg
	${imgfile}= 	Set Variable    ${agent_dir}${/}scripts${/}images${/}lang_${lang}.svg
	Wait For File To Exist 		${imgfile} 	30




#
Verify Test Result Directory Name
	[Arguments]		${result_dir_name}	${scenario_name}	${current_date}
	@{run_dir_name_fragmented}=	Split String	${result_dir_name}	separator=_		max_split=2
	Length Should Be	${run_dir_name_fragmented}	3	msg=The test run result dir was not created correctly!

	${current_date}=	Convert Date	${current_date}		result_format=%Y%m%d_%H%M%S
	${expected_time_to_substract}=	Convert Date	${current_date}		date_format=%Y%m%d_%H%M%S
	${test_run_time_to_substract}=	Convert Date	${run_dir_name_fragmented}[0]_${run_dir_name_fragmented}[1]		date_format=%Y%m%d_%H%M%S
	${time_diff}		Subtract Date From Date	${current_date} 	${test_run_time_to_substract}
	Log To Console	Time diff: ${time_diff}
	Should Be True	${time_diff} >= 0 and ${time_diff} <= 3
	...    msg=Result directory name has incorrect date: expected "${current_date}_${scenario_name}", actual: "${result_dir_name}". There should be little or no difference.

	#${current_date}=	Convert Date	${current_date}		date_format=%Y%m%d_%H%M%S
	${expected_time}=	Subtract Time From Date		${current_date}		${time_diff}	result_format=%Y%m%d_%H%M%S		date_format=%Y%m%d_%H%M%S
	${expected_name}=	Set Variable	${expected_time}_${run_dir_name_fragmented}[2]
	Should Be Equal As Strings		${result_dir_name}		${expected_name}
	...    msg=Result directory name from scenario is incorrect: expected "${expected_name}", actual: "${result_dir_name}".

Verify Generated Run Result Files
	[Arguments]		${result_dir_name}		${scenario_name}
	@{run_dir_name_fragmented}=	Split String	${result_dir_name}	separator=_		max_split=2
	${result_dir_time}=	Set Variable	${run_dir_name_fragmented}[0]_${run_dir_name_fragmented}[1]

	${result_files}=		List Files In Directory		${results_dir}${/}${result_dir_name}
	Log To Console	${\n}All test run result files: ${result_files}{\n}
	${len}=		Get Length	${result_files}
	Should Be True	${len} > 0	msg=The db file was not created.
	Should Be True	${len} < 2	msg=Unexpected files have been created in the results folder. There should only be ${result_dir_time}_${scenario_name}.db file.
	${db_file}=		Set Variable	${result_files}[0]
	Should Be Equal As Strings		${db_file}		${result_dir_time}_${scenario_name}.db
	...    msg=Result directory name from scenario is incorrect: expected "${scenario_name}", actual: "${run_dir_name_fragmented}[2]".

	${logs}=	List Directories In Directory	${results_dir}${/}${result_dir_name}
	Log To Console	${\n}All test run result directories: ${logs}{\n}
	${len}=		Get Length	${logs}
	Should Be True	${len} > 0	msg=The logs directory was not created.
	Should Be True	${len} < 2	msg=Unexpected directories have been created in the results folder. There should only be 'logs' directory.
	Should Be Equal As Strings		${logs}[0]		logs
	...    msg=Logs directory name is incorrect: expected "logs", actual: "${logs}[0]".
	${logs_absolute_paths}	${logs_file_names}
	...    Find Absolute Paths And Names For Files In Directory		${results_dir}${/}${result_dir_name}${/}${logs}[0]
	${len}=		Get Length	${logs_file_names}
	Log To Console	Number of files in the Logs directory: ${len}
	Should Be True	${len} >= 20	msg=Number of files in the Logs directory is incorrect: should be at least 20, actual: "${len}".

Find Result DB
	[Arguments] 	${result_pattern}=*_*
	# ${fols}= 	List Directory 	${results_dir}
	# Log to console 	${fols}
	${fols}= 	List Directory 	${results_dir} 	${result_pattern} 	absolute=True
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

Navigate to and check Desktop Icon
	VAR 	${projname}= 		rfswarm-manager 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Manager 		scope=TEST
	Run Keyword 	Navigate to and check Desktop Icon For ${platform}

Navigate to and check Desktop Icon For MacOS
	Take A Screenshot

	# open finder
	${img}=	Set Variable		${platform}_finder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Sleep 	0.3
	${img}=	Set Variable		${platform}_finder_recents.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}
	# Take A Screenshot

	# un-maximise finder if maximised
	${img}=	Set Variable		${platform}_dock_trash.png
	${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=3
	IF 	not ${passed}
		Take A Screenshot
		Press Combination 	KEY.fn 	KEY.f
		Sleep 	0.3
		Take A Screenshot
	END

	${img}=	Set Variable		${platform}_finder_recents.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}
	Sleep 	0.3

	# macos_finder_menu_go.png
	${img}=	Set Variable		${platform}_finder_menu_go.png
	Click Image		${img}
	# Sleep 	0.3
	# Take A Screenshot

	# _finder_menu_gotofolder.png
	${img}=	Set Variable		${platform}_finder_menu_gotofolder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}

	# nav to /Applications
	# Press Combination 	KEY.command 	KEY.shift 	KEY.g
	${img}=	Set Variable		${platform}_finder_gotoprompt.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Sleep 	0.3

	Press Combination 	KEY.backspace		#clear text filed
	# Sleep 	0.3
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_gotofolder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Type 		/Applications
	# Sleep 	0.3
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_gotoapplications.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.enter
	# Sleep	0.5
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_facetime.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	# Filter/Search /Applications?
	Type 	RFSwarm
	Sleep 	3
	${img}=	Set Variable		${platform}_finder_rfswarm_manager.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

	${img}=	Set Variable		${platform}_dock_trash.png
	${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=3
	IF 	not ${passed}
		Take A Screenshot
		Press Combination 	KEY.fn 	KEY.f
		Sleep 	0.3
		Take A Screenshot
	END

	# Close finder window
	Press Combination 	KEY.command 	KEY.w
	Sleep 	0.3


	# Open Launchpad (F4?)
	# Press Combination   key.f4
	# ${img}=	Set Variable		${platform}_dock_launchpad.png
	${img}=	Set Variable		${platform}_launchpad.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Sleep 	1
	${img}=	Set Variable		${platform}_launchpad_search.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

	# Search Launchpad
	Type 	RFSwarm
	# Sleep 	0.5
	# Take A Screenshot

	# Check for Icon
	# macos_launchpad_rfswarm_reporter.png
	${img}=	Set Variable		${platform}_launchpad_rfswarm_manager.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.ESC

Navigate to and check Desktop Icon For Windows
	Take A Screenshot
	# Open Start Menu
	${img}=	Set Variable		${platform}_start_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Move To 		${coordinates}
	Click Image		${img}
	# Sleep 	1
	# Take A Screenshot

	${img}=	Set Variable		${platform}_start_menu_rfswarm_manager.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	# Navigate Start Menu
	Type 	RFSwarm
	# Sleep 	0.5
	# Take A Screenshot

	# Check for Icon
	${img}=	Set Variable		${platform}_search_rfswarm_manager.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.ESC

Navigate to and check Desktop Icon For Ubuntu

	# Open Menu
	${img}=	Set Variable		${platform}_lxqt_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Move To 		${coordinates}
	Click Image		${img}
	# Sleep 	0.5
	# Take A Screenshot

	# Navigate Menu
	# lxqt_programming_menu.png
	${img}=	Set Variable		${platform}_lxqt_programming_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Move To 		${coordinates}
	Sleep 	0.5
	Take A Screenshot
	Click Image		${img}
	Sleep 	1
	Take A Screenshot

	# Check for Icon
	# ubuntu_lxqt_rfswarm_manager_menu.png
	${img}=	Set Variable		${platform}_lxqt_rfswarm_manager_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

	Press Combination 	KEY.ESC






#
