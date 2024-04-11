*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String
Library		Collections

Library	ImageHorizonLibrary	reference_folder=${IMAGE_DIR}


*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm
${IMAGE_DIR} 	${CURDIR}/Images/file_method
${pyfile_manager}			${EXECDIR}${/}rfswarm_manager${/}rfswarm.py
${pyfile_agent}			${EXECDIR}${/}rfswarm_agent${/}rfswarm_agent.py
${process_manager}		None
${process_agent}		None

*** Keywords ***
Set Platform
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
	# [Arguments]		${options}
	# ${process}= 	Start Process 	python3 	${pyfile_agent}    alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	${process}= 	Start Process 	${cmd_agent}    alias=Agent 	stdout=${OUTPUT DIR}${/}stdout_agent.txt 	stderr=${OUTPUT DIR}${/}stderr_agent.txt
	Set Test Variable 	$process_agent 	${process}

Open Manager GUI
	# [Arguments]		${options}
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	${process}= 	Start Process 	${cmd_manager}    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout_manager.txt 	stderr=${OUTPUT DIR}${/}stderr_manager.txt
	Set Test Variable 	$process_manager 	${process}
	Sleep 	10
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Close Manager GUI ubuntu
	Close Manager GUI

Close Manager GUI windows
	Close Manager GUI

Close Manager GUI
	[Tags]	windows-latest		ubuntu-latest
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	Sleep	5
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Click Dialog Button		no
	END
	${result}= 	Wait For Process 	${process_manager} 	timeout=55
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Fail
	END

Close Manager GUI macos
	[Tags]	macos-latest
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		manager_${platform}_menu_python3.png
	Click Menu		rfswarm
	Click Button	closewindow
	Sleep	5
	${running}= 	Is Process Running 	${process_manager}
	IF 	${running}
		Click Dialog Button		no
	END
	${result}= 	Wait For Process 	${process_manager} 	timeout=55
	${running}= 	Is Process Running 	${process_manager}
	IF 	not ${running}
		Should Be Equal As Integers 	${result.rc} 	0
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process_manager}
		Fail
	END

Stop Agent
	${result} = 	Terminate Process		${process_agent}
	# Should Be Equal As Integers 	${result.rc} 	0

Check If The Agent Has Connected To The Manager
	Click Tab	Agents
	Wait For 	manager_${platform}_agents_ready.png	timeout=300

Check If the Robot Failed
	[Arguments] 	${expected_time}
	Sleep	${expected_time}
	Take A Screenshot	#del later
	TRY
		Click Image 	manager_${platform}_button_abort
		Press Combination	Key.enter
	EXCEPT
		Wait For	manager_${platform}_button_finished_run.png	timeout=300
	END
	Take A Screenshot
	${status}=	Run Keyword And Return Status	Locate	manager_${platform}_testfailed.png
	Run Keyword If	${status}	Fail	msg=Test failed. Check screenshots.

Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		manager_${platform}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot

Click Button
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		manager_${platform}_button_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot

Click Menu
	[Arguments]		${menuname}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	${img}=	Set Variable		manager_${platform}_menu_${menunamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_dlgbtn_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	1
	Take A Screenshot

Press ${key} ${n} Times
	[Documentation]	Provide full name. For example: Key.tab
	Sleep	0.5
	FOR  ${i}  IN RANGE  0  ${n}
		Press Combination 	${key}
	END

Click Label With Vertical Offset
	[Arguments]		${labelname}	${offset}
	[Documentation]	Click the image with the offset 
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down]. 
	...	Give the image a full name, for example: button_runopen.
	${labelname}= 	Convert To Lower Case 	${labelname}
	${img}=	Set Variable		manager_${platform}_${labelname}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1
	Take A Screenshot

Click Label With Horizontal Offset
	[Arguments]		${labelname}	${offset}
	[Documentation]	Click the image with the offset 
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right]. 
	...	Give the image a full name, for example: button_runopen.
	${labelname}= 	Convert To Lower Case 	${labelname}
	${img}=	Set Variable		manager_${platform}_${labelname}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1
	Take A Screenshot

#TODO: Chceck if it works
Resize Window
	[Arguments]		${x}=0		${y}=0
	# 											manager_macos_corner_resize
	${img}=	Set Variable		manager_${platform}_corner_resize.png
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	@{coordinates2}= 	Create List 	${{${coordinates[0]}+${x}}} 	${{${coordinates[1]}+${y}}}
	Move To 	@{coordinates}
	Mouse Down
	Move To 	@{coordinates2}
	Take A Screenshot
	Mouse Up

Wait Agent Ready
	Click Tab 	 Agents
	${img}=	Set Variable		manager_${platform}_agents_ready.png
	Wait For 	${img} 	 timeout=300

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
	EXCEPT
		Open Manager GUI
		Run Keyword		Close Manager GUI ${platform}
		File Should Exist	${location}
	END
	${ini_content}=	Get File	${location}
	Log	${ini_content}
	Should Not Be Empty	${ini_content}
	RETURN	${ini_content}

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

Get Manager PIP Data
	Run Process	pip	show	rfswarm-manager		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Manager must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Create Robot File
	[Arguments]		${path}=${global_path}	${name}=${global_name}	
	...    ${file_content}=***Test Case***\nExample Test Case\n
	
	${example_robot_content}=	Set Variable	${file_content}
	Variable Should Exist	${path}	msg="Global save path does not exist or path is not provided."
	Variable Should Exist	${name}	msg="Global file name does not exist or file name is not provided."
	Create File		${path}${/}${name}	content=${example_robot_content}
	File Should Exist	${path}${/}${name}

Change Test Group Settings
	[Arguments]		&{row_settings_data}
	Sleep	2
	Click Dialog Button		row_settings_frame_name
	Press Key.tab 1 Times
	IF  'excludelibraries' in ${row_settings_data}
		Type	${row_settings_data['excludelibraries']}
	END
	Press Key.tab 1 Times
	IF  'robot_options' in ${row_settings_data}
		Type	${row_settings_data['robot_options']}
	END
	IF  'test_repeater' in ${row_settings_data}
		IF  '${row_settings_data['test_repeater']}' == 'True'
			Click Button	checkbox_unch
		END
	END
	
	IF 	"${platform}" == "macos"
		Click Dialog Button		save_2
	ELSE
		Click Dialog Button		save
	END
	

Select Robot File
	[Arguments]		@{robot_data}
	Sleep	2
	${robot_file_name}=		Set Variable		${robot_data}[1]
	${robot_file_name}=		Get Substring	${robot_file_name}	0	-6
	Log		${robot_file_name}
	Take A Screenshot
	Click Dialog Button		${robot_file_name}_robot
	Sleep	1
	Take A Screenshot
	Click Dialog Button		open
	Sleep	1

Select ${n} Robot Test Case
	Click Button	select_test_case
	Press Key.down ${n} Times	
	Press Combination	Key.enter

Save Scenario File
	[Arguments]		${scenario_name}
	Sleep	5
	Type	${scenario_name}.rfs
	Take A Screenshot
	Click Dialog Button		save
	Sleep	1

Open Scenario File
	[Arguments]		${scenario_name}
	Sleep	5
	Type	${scenario_name}.rfs
	Take A Screenshot
	Click Dialog Button		open
	Sleep	1

Get Scenario File Content
	[Arguments]		${scenario_name}
	${scenario_content}=	Get File	${global_path}${/}${scenario_name}.rfs
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

Delete Directory In Default Path
	[Arguments]	${dir_name}
	Remove Directory	${global_path}${/}${dir_name}	recursive=${True}

