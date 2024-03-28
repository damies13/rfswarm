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
	IF 	"${platform}" == "ubuntu"
		Sleep	1
		TRY
			Click Button	close_no
		EXCEPT
			No Operation 
		END
	ELSE
		Press Combination 	n 	Key.ctrl
	END
	Press Combination 	n 	Key.ctrl
	${result}= 	Wait For Process 	${process_manager} 	timeout=60
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
	Click Image		manager_${platform}_button_closewindow.png
	Take A Screenshot
	${result}= 	Wait For Process 	${process_manager} 	timeout=60
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
	${img}=	Set Variable		${platform}_dlgbtn_${btnname}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	1
	Take A Screenshot

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
	Mouse Up

Wait Agent Ready
	Click Tab 	 Agents
	${img}=	Set Variable		manager_${platform}_agents_ready.png
	Wait For 	${img} 	 timeout=300

Set Global Save Path And Filename
	#sets global default global save path and file_name for robot
	[Arguments]		${input_name}	${optional_path}=${None}
	Set Test Variable	${file_name}	${input_name}

	${pip_data}=	Get Manager PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]

	Set Test Variable	${save_path}	${location}${/}rfswarm_manager${/}

	Set Test Variable 	$file_name 	${file_name}
	Run Keyword If	'${optional_path}' != '${None}'	
	...	Set Test Variable	${save_path}	${optional_path}

	Log		${file_name}
	Log		${save_path}

Get Manager PIP Data
	Run Process	pip	show	rfswarm-manager	alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Manager must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Create Example Robot File
	${example_robot_content}=	Set Variable	***Test Case***\nExample Test Case\n
	Variable Should Exist	${save_path}	msg="Global save path does not exist."
	Variable Should Exist	${file_name}	msg="Global file name does not exist."
	Create File		${save_path}${/}${file_name}	content=${example_robot_content}
	File Should Exist	${save_path}${/}${file_name}

Delete Example Robot File
	Remove File		${save_path}${/}${file_name}
	Variable Should Exist	${save_path}	msg="Global save path does not exist."
	Variable Should Exist	${file_name}	msg="Global file name does not exist."
	File Should Not Exist	${save_path}${/}${file_name}

Select Robot File windows
	[Tags]	windows-latest
	[Arguments]		@{correct_data}
	${robot_file_name}=		Set Variable		${correct_data}[1]
	${robot_file_name}=		Get Substring	${robot_file_name}	0	-6
	Log		${robot_file_name}
	Sleep	3
	Take A Screenshot
	Click Dialog Button		${file_name}
	Sleep	1
	Click Dialog Button		open
	Sleep	1

Select Robot File ubuntu
	[Tags]	ubuntu-latest
	[Arguments]		@{correct_data}
	${robot_file_name}=		Set Variable		${correct_data}[1]
	${robot_file_name}=		Get Substring	${robot_file_name}	0	-6
	Log		${robot_file_name}
	Sleep	3
	Take A Screenshot
	Type	${correct_data}[1]
	Sleep	1
	Press Combination	Key.enter
	Sleep	1

Save Scenario File
	[Arguments]		${scenario_name}
	Sleep	1
	Type	${scenario_name}.rfs
	Click Dialog Button		save
	Sleep	1

Delete Scenario File
	[Arguments]		${scenario_name}
	Remove File		${save_path}${/}${scenario_name}.rfs
	File Should Not Exist	${save_path}${/}${scenario_name}.rfs

Verify Scenario File
	[Arguments]		${scenario_name}	@{correct_data}
	Log	${scenario_name}.rfs
	Log	${correct_data}
	${scenario_content}=	Get scenario file content	${scenario_name}
	Check scenario file content		${scenario_content}		@{correct_data}

Get Scenario File Content
	[Arguments]		${scenario_name}
	${scenario_content}=	Get File	${save_path}${/}${scenario_name}.rfs
	Should Not Be Empty	${scenario_content}
	${scenario_content}=	Split String	${scenario_content}

	RETURN	${scenario_content}

Check Scenario File Content
	[Arguments]		${scenario_content}		@{correct_data}
	Log		${scenario_content}

	${correct_robot_name}=	Split String		${correct_data}[0]
	Log		${correct_robot_name}
	${i}=	Get Index From List		${scenario_content}		test
	Should Be Equal		${correct_robot_name}	${scenario_content}[${i + 2}:${i + 5}]

	${i}=	Get Index From List		${scenario_content}		script
	Should Be Equal		${correct_data}[1]	${scenario_content}[${i + 2}]
