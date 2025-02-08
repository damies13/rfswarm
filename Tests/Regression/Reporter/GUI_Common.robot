*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String
Library 	Collections
Library 	DocTest.VisualTest
Library 	XML 	use_lxml=True

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}
Library 	OCRLibrary

Library 	read_docx.py
Library 	read_xlsx.py
Library 	save_html_image.py
Library 	img_common.py

Variables 	report_expected_data.yaml

*** Variables ***
${default_image_timeout} 	${120}
${platform}		None
${cmd_reporter} 		rfswarm-reporter
${IMAGE_DIR} 	${CURDIR}${/}Images${/}file_method
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py
${process}		None
${sssleep}		0.5
${DonationReminter} 	${False}

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

Make Clipboard Not None
	Evaluate    clipboard.copy("You should never see this after copy") 	modules=clipboard

Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		reporter_${platform}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	# Take A Screenshot

Create New Section
	[Arguments]		${sectname}

	Click Button 			AddSection
	Take A Screenshot
	${img}=	Set Variable		reporter_${platform}_label_sectionname.png
	Wait For		${img} 	 timeout=300
	Take A Screenshot

	IF 	$platform == 'macos'
		# Type 		${sectname}
		# Sleep    2
		# Take A Screenshot
		Press Combination 	Key.Tab
		# Click Image		${img}
		# Sleep    2
		# Take A Screenshot
		Click To The Below Of Image 	${img} 	20
		# Sleep    2
		# Take A Screenshot
		Press Combination 	Key.End
		Sleep    2
		# Take A Screenshot
		# Type 		${sectname}
		# Evaluate 		pyautogui.write('${sectname}', interval=0.10)		modules=pyautogui
		# try pynput.keyboard.Controller
		Evaluate 		pynput.keyboard.Controller().type('${sectname}') 		modules=pynput.keyboard
		# Sleep    2
		# Take A Screenshot
		# Sleep    2
		Click Button 			OK
		# Take A Screenshot
	ELSE
		Click To The Below Of Image 	${img} 	20
		# Sleep    2
		# Take A Screenshot
		Type 		${sectname}
		Take A Screenshot
		# Sleep    2
		Click Button 			OK
		# Take A Screenshot
	END

Click Section
	[Arguments]		${sectname}
	${sectnamel}= 	Convert To Lower Case 	${sectname}
	${img}=	Set Variable		reporter_${platform}_section_${sectnamel}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	# Take A Screenshot

Select Option
	[Arguments]		${optname}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}=	Set Variable		reporter_${platform}_option_${optnamel}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	# Take A Screenshot

Select Field With Label
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}=	Set Variable		reporter_${platform}_label_${labell}.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	${imgsize}= 	Get Image Size 	${IMAGE_DIR}${/}${img}
	Log		${imgsize}
	${offsetx}= 	Evaluate 	int(${imgsize}[0]/2)+${offsetx}
	Log		${offsetx}
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	${x}= 	Evaluate 	${coordinates}[0]+${offsetx}
	${y}= 	Evaluate 	${coordinates}[1]+${offsety}
	@{coordinates}= 	Create List 	${x} 	${y}
	Move To 	${coordinates}
	Click
	Sleep 	${sssleep}
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

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
	# Take A Screenshot

Get Text Value To Right Of
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}= 	Set Variable		reporter_${platform}_label_${labell}.png

	Wait For 	${img} 	 timeout=${default_image_timeout}

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
	${labell}= 	Convert To Lower Case 	${label}
	${img}= 	Set Variable		reporter_${platform}_label_${labell}.png
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
	Take A Screenshot
	Double Click
	Take A Screenshot
	Type 	${value}
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
			Type 	${value}
			Take A Screenshot
			${value2}= 	Get Text Value To Right Of		${label} 		${offsetx}
		END
		Should Be Equal As Strings    ${value}    ${value2}
	END

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

Click Button
	[Arguments]		${bttnname} 		${timeout}=300
	${bttnnamel}= 	Convert To Lower Case 	${bttnname}
	${img}=	Set Variable		reporter_${platform}_button_${bttnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	# Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=300
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${platform}_dlgbtn_${btnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	1
	# Take A Screenshot

Wait For Status
	[Arguments]		${status}	${timeout}=1800
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		reporter_${platform}_status_${statusl}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wiggle Mouse
	# Take A Screenshot
	Wait For 	${img} 	 timeout=${timeout}
	Sleep 	${sssleep}
	# Take A Screenshot

Open GUI
	[Arguments]		@{appargs}
	${var}= 	Get Variables
	Log 	${var}
	Get Platform

	# Press Escape and move mouse because on linux the screen save had kicked in
	Press Combination 	Key.esc
	Wiggle Mouse

	${keyword}= 	Set Variable 	Open GUI ${platform}
	Run Keyword 	${keyword} 	@{appargs}
	Handle Donation Reminder

Wiggle Mouse
	Move To 	10 	10
	Move To 	20 	20

Get Platform
	&{platforms}= 	Create Dictionary 	Linux=ubuntu 	Darwin=macos 	Java=notsupported 	Windows=windows
	${os}= 	Evaluate 	platform.system() 	platform
	Set Suite Variable    ${platform}    ${platforms}[${os}]

Open GUI windows
	[Arguments]		@{appargs}
	# Set Suite Variable    ${platform}    windows
	${args}= 	Evaluate 	" \t".join(@{appargs})
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	# ${process}= 	Start Process 	python 	${pyfile} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt

	Set Suite Variable 	$process 	${process}
	# reporter_windows_status_previewloaded
	# Wait For Status 	PreviewLoaded
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	# Take A Screenshot

Open GUI ubuntu
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	# Take A Screenshot

Open GUI macos
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile} 	-g 	5 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	# Take A Screenshot

Handle Donation Reminder
	${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		${default_image_timeout / 2}
	VAR 	${DonationReminder} 	${found} 		scope=TEST

Close GUI
	${keyword}= 	Set Variable 	Close GUI ${platform}
	IF 	${process}
		${running}= 	Is Process Running 	${process}
		IF 	${running}
			Run Keyword 	${keyword}
		ELSE
			# ${result}= 	Get Process Result 	${process}
			${result}= 	Wait For Process 	${process} 	timeout=60
			Check Result 	${result}
		END
	END
	Set Suite Variable 	$process 	None
	Sleep 	0.5

Check Result
	[Arguments]		${result}
	Log 	${result.stdout}
	Should Not Contain 	${result.stdout} 	Traceback
	Log 	${result.stderr}
	Should Not Contain 	${result.stderr} 	Traceback
	Should Be Equal As Integers 	${result.rc} 	0

Close GUI windows
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	# Press Combination 	Key.f4 	Key.alt
	# Run Keyword And Ignore Error 	Wait For Status 	PreviewLoaded 	10
	# Run Keyword And Ignore Error 	Click Image		reporter_${platform}_status_previewloaded.png
	Click Image		reporter_${platform}_button_closewindow.png
	Run Keyword And Ignore Error 	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI ubuntu
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	# Run Keyword And Ignore Error 	Wait For Status 	PreviewLoaded 	10
	# Run Keyword And Ignore Error 	Click Image		reporter_${platform}_status_previewloaded.png
	Click Image		reporter_${platform}_button_closewindow.png
	Run Keyword And Ignore Error 	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI macos
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		reporter_${platform}_menu_python3.png
	# Run Keyword And Ignore Error 	Wait For Status 	PreviewLoaded 	10
	# Run Keyword And Ignore Error 	Click Image		reporter_${platform}_status_previewloaded.png
	Click Image		reporter_${platform}_button_closewindow.png
	Run Keyword And Ignore Error 	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

End Process If Still Running
	${result}= 	Wait For Process 	${process} 	timeout=60
	${running}= 	Is Process Running 	${process}
	IF 	not ${running}
		Check Result 	${result}
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Check Result 	${result}
		Fail 	Had to Terminate Process
	END

Get Python Version Info
	${vinfo}= 	Evaluate    sys.version_info 	modules=sys
	RETURN		${vinfo}

Get Image Size
	[Arguments] 	${imgfile}
	# ahrrrg windows paths, PIL.Image.open doesn't like them, need to escape / replace \\
	# ${imgfile}= 	Evaluate    "${imgfile}".replace('\\' '/')
	${img}= 	Evaluate    PIL.Image.open(r'${imgfile}') 	PIL.Image
	${imgsize}= 	Set Variable    ${img.size}
	# Evaluate    ${img.close()}
	RETURN 	${imgsize}

Get Reporter PIP Data
	Run Process	pip	show	rfswarm-reporter		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Reporter must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Get Reporter Default Save Path
	${pip_data}=	Get Reporter PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_reporter${/}

Get Reporter INI Location
	${location}=	Get Reporter Default Save Path
	RETURN	${location}RFSwarmReporter.ini

Get Reporter INI Data
	${location}=	Get Reporter INI Location
	TRY
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	EXCEPT
		Open GUI
		Close GUI
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	END
	${ini_content}=	Get File	${location}
	Log	${ini_content}
	Should Not Be Empty	${ini_content}
	RETURN	${ini_content}

Change Reporter INI File Settings
	[Arguments]		${option}	${new_value}
	${location}=	Get Reporter INI Location
	${ini_content}=		Get Reporter INI Data
	${ini_content_list}=	Split String	${ini_content}
	${option_index}=	Get Index From List		${ini_content_list}		${option}
	Log To Console	${ini_content_list}

	${len}	Get Length	${ini_content_list}
	IF  ${len} > ${option_index + 2}
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${option_index + 2}]	${new_value}
	ELSE
		${ini_content}=		Replace String	${ini_content}	${ini_content_list}[${option_index}] =	${option} = ${new_value}
	END
	Log To Console	${ini_content}

	Remove File		${location}
	Log		${ini_content}
	Append To File	${location}		${ini_content}

Save Template File OS DIALOG
	[Arguments]		${template_name}
	Sleep	5
	Type	${template_name}
	# Take A Screenshot
	Click Dialog Button		save
	Sleep	1

Get Manager Default Save Path
	${pip_data}=	Get Manager PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_manager${/}

Get Manager PIP Data
	Run Process	pip	show	rfswarm-manager		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Manager must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Navigate to and check Desktop Icon
	VAR 	${projname}= 		rfswarm-manager 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Manager 		scope=TEST
	Run Keyword 	Navigate to and check Desktop Icon For ${platform}

Navigate to and check Desktop Icon For MacOS

	# Release Fn Key

	Take A Screenshot

	# open go menu
	${img}=	Set Variable		${platform}_finder_menu_go.png
	Click Image		${img}
	# Sleep 	0.3
	# Take A Screenshot

	# select Go to Folder from Go menu
	${img}=	Set Variable		${platform}_finder_menu_gotofolder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}
	# Sleep 	0.3
	# Take A Screenshot


	# # open finder
	# ${img}=	Set Variable		${platform}_finder.png
	# Wait For 	${img} 	 timeout=${default_image_timeout}
	# @{coordinates}= 	Locate		${img}
	# Click Image		${img}
	# ${img}=	Set Variable		${platform}_finder_toolbar.png
	# Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot
	#
	# # un-maximise finder if maximised
	# ${img}=	Set Variable		${platform}_finder.png
	# ${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=1
	# IF 	not ${passed}
	# 	Take A Screenshot
	# 	Press Combination 	KEY.fn 	KEY.f
	# END
	# Sleep 	0.3
	# Take A Screenshot
	#
	# ${img}=	Set Variable		${platform}_finder_toolbar.png
	# Click Image 	${img}
	# Sleep 	0.3
	# Take A Screenshot
	#
	# # nav to /Applications
	# Press Combination 	KEY.command 	KEY.shift 	KEY.g
	# Sleep 	0.3
	# Take A Screenshot
	# Press Combination 	KEY.backspace		#clear text filed
	# Sleep 	0.3
	# Take A Screenshot
	# Sleep 	0.3
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_gotofolder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}
	# Take A Screenshot

	# Type 		/Applications
	Evaluate 		pynput.keyboard.Controller().type('/Applications') 		modules=pynput.keyboard

	# Sleep 	0.3
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_gotoapplications.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

	Press Combination 	KEY.enter
	# Sleep	0.5
	# Take A Screenshot
	${img}=	Set Variable		${platform}_finder_facetime.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

	# Filter/Search /Applications?
	Type 	RFSwarm
	# Sleep 	0.3
	${img}=	Set Variable		${platform}_finder_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Take A Screenshot

	# Open Launchpad (F4?)
	# Press Combination   key.f4
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
	# Sleep 	0.3
	Take A Screenshot

	# Check for Icon
	# macos_launchpad_rfswarm_reporter.png
	${img}=	Set Variable		${platform}_launchpad_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

	Press Combination 	KEY.ESC
	# Take A Screenshot

Navigate to and check Desktop Icon For Windows

	Take A Screenshot
	# Open Start Menu
	${img}=	Set Variable		${platform}_start_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	1
	Take A Screenshot

	${img}=	Set Variable		${platform}_start_menu_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	# Navigate Start Menu
	Type 	RFSwarm
	Sleep 	0.5
	Take A Screenshot

	# Check for Icon
	${img}=	Set Variable		${platform}_search_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.ESC

Navigate to and check Desktop Icon For Ubuntu

	Take A Screenshot
	# Open Menu
	${img}=	Set Variable		${platform}_lxqt_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Move To 	${coordinates}
	# Click 	button=right
	Sleep 	0.5
	Take A Screenshot

	# Navigate Menu
	# lxqt_programming_menu.png
	${img}=	Set Variable		${platform}_lxqt_programming_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	Click Image		${img}
	Sleep 	0.5
	Take A Screenshot

	# Check for Icon
	# ubuntu_lxqt_rfswarm_reporter_menu.png
	${img}=	Set Variable		${platform}_lxqt_rfswarm_reporter_menu.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.ESC

Parse HTML File
	[Documentation] 	Parse HTML file to the etree object using lxml module.
	[Arguments] 	${html_file}
	File Should Exist 	${html_file}
	${html}= 	Evaluate 	lxml.etree.parse(r'${html_file}', lxml.etree.HTMLParser()) 	modules=lxml.etree

	RETURN 	${html}

Extract All HTML Report Headings
	[Documentation] 	Search for all HTML report section headings. You can change searchable html element from h1 to: h2, h3 ...
	[Arguments] 	${grand_selector} 	${child}=//div 	${heading}=h1
	Log 	${grand_selector}

	VAR 	@{headings}
	TRY
		@{headings} 	Get Elements Texts 	${grand_selector} 	${heading}
	EXCEPT
		No Operation
	END

	@{selectors} 	Get Elements 	${grand_selector} 	${child}
	FOR  ${selector}  IN  @{selectors}
		@{selector_headings} 	Extract All HTML Report Headings 	${selector} 	div
		${headings} 	Combine Lists 	${headings} 	${selector_headings}
	END

	RETURN 	${headings}

Verify HTML Cover Page
	[Arguments] 	${html}
	${cover_section}= 	Get Element 	${html} 	//div[@id="TitlePage"]
	${title} 	Get Element Text 	${cover_section} 	div[@class="title center"]
	${data} 	Get Element Text 	${cover_section} 	div[@class="subtitle center"]
	VAR 	@{cover_txtdata} 	${title} 	${data}

	@{cover_expected} 	Convert To List 	${Cover.text}
	Lists Should Be Equal 	${cover_expected} 		${cover_txtdata}	msg=[ Expected != Converted ]

Get HTML Report Heading Section Object
	[Documentation]
	...    Searches for provided heading name and return whole section object in the given selector such as html.
	...    If not return 0.
	...    You can change searchable html element from h1 to: h2, h3 ...
	[Arguments] 	${grand_selector} 	${heading_name} 	${heading}=h1 	${child}=//div
	Log 	${grand_selector}
	Log 	${child}

	TRY
		@{texts} 	Get Elements Texts 	${grand_selector} 	${heading}
	EXCEPT
		No Operation
	END
	FOR  ${text}  IN  @{texts}
		${status}= 	Run Keyword And Return Status 	Should Contain 	${text} 	${heading_name}
		IF  ${status}
			Log 	${text}
			Log 	${heading_name}
			RETURN 	${grand_selector}
		END

	END

	@{selectors} 	Get Elements 	${grand_selector} 	${child}
	FOR  ${selector}  IN  @{selectors}
		${found_selector} 	Get HTML Report Heading Section Object 	${selector} 	${heading_name} 	${heading} 	child=div
		Log 	${found_selector}
		IF  '${found_selector}' != '${0}'
			RETURN 	${found_selector}
		END

	END

	Log 	Didn't find any matching headings.
	RETURN 	${0}

Read HTML Report Section Text Data
	[Documentation]
	...    Return all available text data in a given container from a given section and it's childs.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section_obj} 	 ${break_at}=${None} 	${container}=p
	Log 	${section_obj}

	TRY
		@{texts} 	Get Elements Texts 	${section_obj} 	${container}
	EXCEPT
		No Operation
	END

	@{childs} 	Get Child Elements 	${section_obj}
	FOR  ${child}  IN  @{childs}
		Log 	${child.tag}
		IF  '${child.tag}' != '${break_at}'
			@{selector_text} 	Read HTML Report Section Text Data 	${child} 	${break_at} 	${container}
			${texts} 	Combine Lists 	${texts} 	${selector_text}
		ELSE
			BREAK
		END

	END

	RETURN 	${texts}

Read HTML Report Section Data Table
	[Documentation] 	Return table data that is in the provided section as nested list: Table = [[header_row], [row1], [row2], ...]
	[Arguments] 	${section_obj}
	${table} 	Get Element 	${section_obj} 	div/table
	@{table_rows} 	Get Elements 	${table} 	tr

	VAR 	@{table_data}

	FOR  ${row}  IN  @{table_rows}
		VAR 	@{row_data}

		@{table_row_cells} 	Get Child Elements 	 ${row}
		FOR  ${cell}  IN  @{table_row_cells}
			${cell_data} 	Get Element Text 	${cell}
			Append To List 	${row_data} 	${cell_data}

		END
		${len} 	Get Length 	${row_data}
		IF  ${len} > 0
			Append To List 	${table_data} 	${row_data}
		END

	END

	RETURN 	${table_data}

Extract All Images From HTML Report Section
	[Documentation]
	...    Extract all images from the given section and save them in the given path.
	...    Provide ${base_name} to specify base for image name.
	...    The ${img_num} argument is only used for naming purposes and its logical count is related to the implementation of the regression.
	[Arguments] 	${section} 	${output_folder} 	${base_name} 	${img_num}=${1}
	Log 	${section}

	TRY
		@{img_containers} 	Get Elements 	${section} 	img
	EXCEPT
		No Operation
	END
	FOR  ${img}  IN  @{img_containers}
		${image_data}= 	Get Element Attribute 	${img} 	src
		Log 	${image_data}
		Log 	${img_num}
		@{splitted_img_data} 	Split String 	${image_data} 	, 	max_split=1 	# Need to separate img data from informations.
		Log 	${splitted_img_data}[1]
		${base64_string} 	Convert To String 	${splitted_img_data}[1]
		Save Html Embeded Image 	${base64_string} 	${base_name}_${img_num} 	${output_folder}

		VAR 	${img_num} 	${img_num + 1}

	END

	@{childs} 	Get Child Elements 	${section}
	FOR  ${child}  IN  @{childs}
		${child_img_num} 	Extract All Images From HTML Report Section 	${child} 	${output_folder} 	${base_name} 	${img_num}
		VAR 	${img_num} 	${child_img_num}
	END

	RETURN 	${img_num} 	# *Only for image count

Verify HTML Report Contents
	[Documentation]
	...    Verify the section for the given section name and section object for the expected text.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${break_at}=${None}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata}= 	Read HTML Report Section Text Data 	${section_obj} 	${break_at}
	@{expected_contents} 	Convert To List 	${${section}.text}
	${len} 	Get Length 	${section_txtdata}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Contain 	${section_txtdata}[${i}] 	${expected_contents}[${i}] 	msg=Can't find ${section_txtdata}[${i}] in the ${section} section.
	END

Verify HTML Report Notes
	[Documentation]
	...    Verify the section for the given section name and section object for the expected text.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${break_at}=${None}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata}= 	Read HTML Report Section Text Data 	${section_obj} 	${break_at}
	@{expected_notes} 	Convert To List 	${${section}.text}
	${len} 	Get Length 	${expected_notes}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${expected_notes}[${i}] 	${section_txtdata}[${i}]
		...    msg=[ Expected != Converted ] Can't find ${section_txtdata}[${i}] in the ${section} section.
	END

Verify HTML Report Graph
	[Documentation]
	...    Verify the section for the given section name and section object for the expected image.
	...    Also provide the paths to the expected html images directory and the directory where the image will be saved.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	${img_count} 	Extract All Images From HTML Report Section 	${section_obj} 	${html_img_path} 	${section}
	${normalized_section} 	Replace String 	${section} 	${SPACE} 	_
	VAR 	${img_name} 	${normalized_section}_${img_count - 1}_image.png
	Convert Image To Black And White 	${html_img_path}${/}${img_name}
	Compare Images 	${html_expected_img_path}${/}${img_name} 	${html_img_path}${/}${img_name}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify HTML Report Table Content
	[Documentation]
	...    Verify the section for the given section name and section object for the expected table content.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj}
	Log 	\t- ${section} 	console=${True}

	${section_table} 	Read HTML Report Section Data Table 	${section_obj}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_expected} 	Convert To List 	${${section}.header}
	@{st_header_row} 	Convert To List 	${section_table}[0]
	Length Should Be 	${section_table} 	${st_length_expected}
	Lists Should Be Equal 	${st_header_expected} 	${st_header_row} 	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify HTML Report Error Details Content
	[Documentation]
	...    Verify the section for the given section name and section object for the expected table content and screenshots.
	...    Also provide the paths to the expected html images directory and the directory where the image will be saved.
	...    The recursion of this function can be break at given html element.
	[Arguments] 	${section} 	${section_obj} 	${html_expected_img_path} 	${html_img_path}
	Log 	\t- ${section} 	console=${True}

	${section_table} 	Read HTML Report Section Data Table 	${section_obj}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_col_expected} 	Convert To List 	${${section}.header_col}
	Length Should Be 	${section_table} 	${st_length_expected}
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
		IF  '${row}[0]' not in @{st_header_col_expected}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${st_header_col_expected}.
		END

	END

	${last_img_num} 	Extract All Images From HTML Report Section 	${section_obj} 	${html_img_path} 	${section}
	${normalized_section} 	Replace String 	${section} 	${SPACE} 	_
	FOR  ${img_num}  IN RANGE  1  ${last_img_num}
		VAR 	${img_name} 	${normalized_section}_${img_num}_image.png
		Compare Images 	${html_expected_img_path}${/}${img_name} 	${html_img_path}${/}${img_name}

	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify XLSX Cover Page
	[Arguments] 	${xlsx_file}
	@{xlsx_sheets}= 	Read All Xlsx Sheets 	${xlsx_file}
	List Should Contain Value 	${xlsx_sheets} 	Cover
	@{cover_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	Cover
	@{cover_expected} 	Convert To List 	${Cover.text}

	${len} 	Get Length 	${cover_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${cover_expected}[${i}] 	${cover_txtdata}[${i}][0] 	msg=[ Expected != Converted ]
	END

Verify XLSX Report Contents
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} XLSX
	END

	@{section_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section_txtdata}

Verify XLSX Report Notes
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_txtdata}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section_txtdata}
	@{notes_expected} 	Convert To List 	${${section}.text}

	${len} 	Get Length 	${notes_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${notes_expected}[${i}] 	${section_txtdata}[${i}][0] 	msg=[ Expected != Converted ]
	END

Verify XLSX Report Graph
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected image. Provide full xlsx file path.
	...    It is required to specify in which cell the image is stored.
	...    Also provide the paths to the expected xlsx images directory and the directory where the image will be saved.
	[Arguments] 	${xlsx_file} 	${section} 	${cell_id} 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	${img}= 	Extract Image From Xlsx Sheet 	${xlsx_file} 	${xlsx_sheet} 	${cell_id} 	${xlsx_img_path}
	Convert Image To Black And White 	${xlsx_img_path}${/}${img}
	Compare Images 	${xlsx_expected_img_path}${/}${img} 	${xlsx_img_path}${/}${img}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify XLSX Report Table Content
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected table text. Provide full xlsx file path.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet} 	${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_table}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_expected} 	Convert To List 	${${section}.header}
	@{st_header_row} 	Convert To List 	${section_table}[0]
	Length Should Be 	${section_table} 	${st_length_expected}
	Lists Should Be Equal 	${st_header_expected} 	${st_header_row} 	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify XLSX Report Error Details Content
	[Documentation]
	...    Verify the section for the given section name and full xlsx sheet name for the expected table text and images. Provide full xlsx file path.
	...    Also provide the paths to the expected xlsx images directory and the directory where the image will be saved.
	...    ${start_at} and ${stop_at} are used to manipulate the returned text data. See the Python function doc. for more information.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${xlsx_file} 	${section} 	${xlsx_sheet}
	...    ${xlsx_expected_img_path} 	${xlsx_img_path}
	...    ${start_at}=${None} 	${stop_at}=${None} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} XLSX
	END

	@{section_table}= 	Read Xlsx Text Data From Sheet 	${xlsx_file} 	${xlsx_sheet} 	${start_at} 	${stop_at}
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_col_expected} 	Convert To List 	${${section}.header_col}
	Length Should Be 	${section_table} 	${st_length_expected}
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
		IF  '${row}[0]' not in @{st_header_col_expected}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${st_header_col_expected}.
		END

		${img}= 	Extract Image From Xlsx Sheet 	${xlsx_file} 	${xlsx_sheet} 	B${i + 3} 	${xlsx_img_path}
		IF  '${img}' != '${0}'
			Log 	Image was found in B${i} cell.
			Compare Images 	${xlsx_expected_img_path}${/}${img} 	${xlsx_img_path}${/}${img}
		END

	END

	# !need to convert empty expected list value to the ${space} where screenshot should be!
	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	${empty_i} 	Get Index From List 	${first_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${first_row_expected} 	${empty_i}
		Insert Into List 	${first_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	${empty_i} 	Get Index From List 	${last_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${last_row_expected} 	${empty_i}
		Insert Into List 	${last_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	${empty_i} 	Get Index From List 	${quater_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${quater_row_expected} 	${empty_i}
		Insert Into List 	${quater_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	${empty_i} 	Get Index From List 	${mid_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${mid_row_expected} 	${empty_i}
		Insert Into List 	${mid_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	${empty_i} 	Get Index From List 	${upper_mid_row_expected} 	${EMPTY}
	IF  '${empty_i}' != '-1'
		Remove From List 	${upper_mid_row_expected} 	${empty_i}
		Insert Into List 	${upper_mid_row_expected} 	${empty_i} 	${SPACE}
	END
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify DOCX Cover Page
	[Arguments] 	${docx_data}
	Dictionary Should Contain Key 	${docx_data} 	Cover
	@{cover_txtdata} 	Convert To List 	${docx_data}[Cover][text]
	@{cover_expected} 	Convert To List 	${Cover.text}
	Lists Should Be Equal 	${cover_expected} 		${cover_txtdata}	msg=[ Expected != Converted ]

Verify DOCX Report Contents
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata} 	Convert To List 	${docx_data}[${section}][text]
	Log 	${section_txtdata}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} DOCX
	END

Verify DOCX Report Notes
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_txtdata} 	Convert To List 	${docx_data}[${section}][text]
	Log 	${section_txtdata}

	IF  ${custom} == ${True}
		VAR 	${section} 		${section} DOCX
	END

	@{notes_expected} 	Convert To List 	${${section}.text}

	${len} 	Get Length 	${notes_expected}
	FOR  ${i}  IN RANGE  0  ${len}
		Should Be Equal 	${notes_expected}[${i}] 	${section_txtdata}[${i}] 	msg=[ Expected != Converted ]
	END

Verify DOCX Report Graph
	[Documentation]
	...    Verify the section for the given section name for the expected image. Provide full docx file path.
	...    Also provide the paths to the expected docx images directory and the directory where the image will be saved.
	[Arguments] 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${img_comp_threshold} 	${move_tolerance}
	Log 	\t- ${section} 	console=${True}

	@{img_names}= 	Extract DOCX Images Under Heading 	${section} 	${docx_file} 	${docx_img_path}
	VAR 	${img_name} 	${img_names}[0]
	Convert Image To Black And White 	${docx_img_path}${/}${img_name}
	Compare Images 	${docx_expected_img_path}${/}${img_name} 	${docx_img_path}${/}${img_name}
	...    threshold=${img_comp_threshold} 	move_tolerance=${move_tolerance} 	blur=${True}

Verify DOCX Report Table Content
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected table text.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	@{section_table} 	Convert To List 	${docx_data}[${section}][table]
	Log 	${section_table}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} DOCX
	END

	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_expected} 	Convert To List 	${${section}.header}
	@{st_header_row} 	Convert To List 	${section_table}[0]
	Length Should Be 	${section_table} 	${st_length_expected}
	Lists Should Be Equal 	${st_header_expected} 	${st_header_row} 	msg=[ Expected != Converted ]
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Verify DOCX Report Error Details Content
	[Documentation]
	...    Verify the section for the given docx data dict and section name for the expected table text and images.
	...    Provide full docx file path for image comparison.
	...    Also provide the paths to the expected docx images directory and the directory where the image will be saved.
	...    Custom variable is to select the expected data only for this type of report. If they exist in yaml file.
	[Arguments] 	${docx_data} 	${section} 	${docx_file} 	${docx_expected_img_path} 	${docx_img_path} 	${custom}=${False}
	Log 	\t- ${section} 	console=${True}

	IF  ${custom} == ${True}
		VAR 	${section} 	${section} DOCX
	END

	@{section_table}= 	Convert To List 	${docx_data}[${section}][table]
	Log 	${section} table content: ${section_table}
	VAR 	${st_length_expected} 	${${section}.length}
	@{st_header_col_expected} 	Convert To List 	${${section}.header_col}
	Length Should Be 	${section_table} 	${st_length_expected}
	FOR  ${i}  IN RANGE  0  ${st_length_expected}
		VAR 	${row} 		${section_table}[${i}]
		Should Not Be Empty 	${row} 		msg=Row ${i} is empty in the ${section}!
		IF  '${row}[0]' not in @{st_header_col_expected}
			Fail	msg=First column in the ${i} row does not save correctly because "${row}[0]" is not in expected values: ${st_header_col_expected}.
		END

	END

	@{img_names}= 	Extract DOCX Images Under Heading 	${section} 	${docx_file} 	${docx_img_path}
	FOR  ${img_name}  IN  @{img_names}
		Compare Images 	${docx_expected_img_path}${/}${img_name} 	${docx_img_path}${/}${img_name}
	END

	@{rows_numbers} 	Convert To List 	${${section}.rows_numbers}

	@{first_data_row} 		Convert To List 	${section_table}[${rows_numbers}[0]]
	@{first_row_expected} 	Convert To List 	${${section}.first_row}
	Lists Should Be Equal 	${first_row_expected} 	${first_data_row}	msg=[ Expected != Converted ]

	@{last_row} 			Convert To List 	${section_table}[${rows_numbers}[1]]
	@{last_row_expected} 	Convert To List 	${${section}.last_row}
	Lists Should Be Equal 	${last_row_expected} 	${last_row}	msg=[ Expected != Converted ]

	@{quater_row} 			Convert To List 	${section_table}[${rows_numbers}[2]]
	@{quater_row_expected} 	Convert To List 	${${section}.quater_row}
	Lists Should Be Equal 	${quater_row_expected} 	${quater_row}	msg=[ Expected != Converted ]

	@{mid_row} 				Convert To List 	${section_table}[${rows_numbers}[3]]
	@{mid_row_expected} 	Convert To List 	${${section}.mid_row}
	Lists Should Be Equal 	${mid_row_expected} 	${mid_row}	msg=[ Expected != Converted ]

	@{upper_mid_row} 			Convert To List 	${section_table}[${rows_numbers}[4]]
	@{upper_mid_row_expected} 	Convert To List 	${${section}.upper_mid_row}
	Lists Should Be Equal 	${upper_mid_row_expected} 	${upper_mid_row}	msg=[ Expected != Converted ]

Hex to DEC RGB
	[Arguments] 	${hex_colour}
	${HexR} = 	Get Substring 	${hex_colour} 	0 	2
	${HexG} = 	Get Substring 	${hex_colour} 	2 	4
	${HexB} = 	Get Substring 	${hex_colour} 	-2

	${DecR}= 	Convert To Integer 	${HexR} 	16
	${DecG}= 	Convert To Integer 	${HexG} 	16
	${DecB}= 	Convert To Integer 	${HexB} 	16

	${dec_rgb}= 	Create List 	${DecR} 	${DecG} 	${DecB}

	RETURN 		${dec_rgb}

Choose Colour With OS Colour Picker
	[Documentation]
	...    Select a colour using the OS's colour picker.
	...    Colour should be in rrbbgg hex values
	[Arguments] 	${hex_colour}
	Log    Hex Colour: ${hex_colour}
	Run Keyword 	Choose Colour With ${platform} Colour Picker 		${hex_colour}

Choose Colour With macos Colour Picker
	[Arguments] 	${hex_colour}
	# @{RGB}= 	Hex to DEC RGB 	${hex_colour}

	Click Button 	Sliders

	# Click Grayscale Slider option menu, then select RGB Slider
	Select Option 	GrayscaleSlider
	Select Option 	RGBSlider

	Set Text Value To Right Of 		HexColor 		${hex_colour} 	10

	# Sleep 	1
	# Take A Screenshot

	# Press Combination 	Key.ENTER
	# Press Combination 	Key.TAB
	Press Combination 	Key.Shift 	Key.TAB

	# Sleep 	1
	# Take A Screenshot

	Click Button 	OK2
	#
	# Sleep 	1
	# Take A Screenshot

Choose Colour With windows Colour Picker
	[Arguments] 	${hex_colour}
	@{RGB}= 	Hex to DEC RGB 	${hex_colour}

	${CRed}= 	Convert To String 	${RGB[0]}
	${CGreen}= 	Convert To String 	${RGB[1]}
	${CBlue}= 	Convert To String 	${RGB[2]}

	# Red
	Press Combination 	Key.Alt 	Key.r
	Type 		${CRed}

	# Green
	Press Combination 	Key.Alt 	Key.g
	Type 		${CGreen}

	# Blue
	Press Combination 	Key.Alt 	Key.u
	Type 		${CBlue}

	# Set Text Value To Right Of 		Red 		${RGB[0]} 	10
	# Set Text Value To Right Of 		Green 	${RGB[2]} 	10
	# Set Text Value To Right Of 		Blue 		${RGB[1]} 	10

	# Sleep 	1
	# Take A Screenshot

	Press Combination 	Key.ENTER
	# Click Button 	OK

	# Sleep 	1
	# Take A Screenshot

Choose Colour With ubuntu Colour Picker
	[Arguments] 	${hex_colour}
	# @{RGB}= 	Hex to DEC RGB 	${hex_colour}

	# Click To The Below Of Image

	# Press Alt+s
	Press Combination 	Key.Alt 	Key.s

	# Press Home, then press Shift + End
	Press Combination 	Key.Home
	Press Combination 	Key.Shift 	Key.End

	# Sleep 	1
	# Take A Screenshot

	Press Combination 	Key.Delete

	# Sleep 	1
	# Take A Screenshot
	# Type #value
	Log 		\#${hex_colour}
	Type 		\#${hex_colour}

	# Sleep 	1
	# Take A Screenshot

	Press Combination 	Key.ENTER

	# Sleep 	1
	# Take A Screenshot
	# Press Alt+O
	Press Combination 	Key.Alt 	Key.o

	# Sleep 	1
	# Take A Screenshot

	# Locate 	reporter_${platform}_dlg_aaa.png

Release Fn Key

	IF 	$platform == 'macos'
		# https://github.com/asweigart/pyautogui/issues/796
		${result}= 		Evaluate 	pyautogui.keyUp('fn') 	modules=pyautogui
		Log    ${result}

	END






#
