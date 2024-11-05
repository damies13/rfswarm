*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String
Library 	Collections
Library 	DocTest.VisualTest

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}
Library 	OCRLibrary

Library 	read_docx.py
Library 	read_xlsx.py

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
	Double Click
	Type 	${value}
	IF 	$platform == 'macos'
		Take A Screenshot
	ELSE
		${value2}= 	Get Text Value To Right Of		${label}
		WHILE 	$value2 != $value 		limit=10
			${x}= 	Evaluate 	${x}+10
			${offsetx}= 	Evaluate 	${offsetx}+10
			@{coordinates}= 	Create List 	${x} 	${y}
			Move To 	${coordinates}
			Click
			Double Click
			Type 	${value}
			# Take A Screenshot
			${value2}= 	Get Text Value To Right Of		${label}
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

	Take A Screenshot

	# open finder
	${img}=	Set Variable		${platform}_finder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Sleep 	0.3
	${img}=	Set Variable		${platform}_finder_toolbar.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

	# un-maximise finder if maximised
	${img}=	Set Variable		${platform}_finder.png
	${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=1
	IF 	not ${passed}
		Take A Screenshot
		Press Combination 	KEY.fn 	KEY.f
		Sleep 	0.3
		Take A Screenshot
	END

	# nav to /Applications
	Press Combination 	KEY.command 	KEY.shift 	KEY.g
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
	# Sleep 	0.3
	${img}=	Set Variable		${platform}_finder_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	# Take A Screenshot

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
	# Take A Screenshot

	# Check for Icon
	# macos_launchpad_rfswarm_reporter.png
	${img}=	Set Variable		${platform}_launchpad_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${default_image_timeout}

	Press Combination 	KEY.ESC

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



#