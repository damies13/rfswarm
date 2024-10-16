*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String
Library 	Collections

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}
Library 	OCRLibrary


*** Variables ***
${cmd_reporter} 		rfswarm-reporter
${IMAGE_DIR} 	${CURDIR}${/}Images${/}file_method
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py
${process}		None
${sssleep}		0.5

*** Keywords ***
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
	Take A Screenshot

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
	Take A Screenshot

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
	Take A Screenshot

Select Field With Label
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}=	Set Variable		reporter_${platform}_label_${labell}.png
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
	Take A Screenshot

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
	Take A Screenshot

Get Text Value To Right Of
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}= 	Set Variable		reporter_${platform}_label_${labell}.png

	${b4value}= 	Get Clipboard Content
	${value}= 	Copy From The Right Of 	${img} 	${offsetx}
	Take A Screenshot
	WHILE 	$b4value == $value 		limit=10
		Sleep    10 ms
		${offsetx}= 	Evaluate 	${offsetx}+10
		${value}= 	Copy From The Right Of 	${img} 	${offsetx}
		Take A Screenshot
		${valuec}= 	Copy
		IF  $valuec != $value
			${value}= 	Set Variable 		${valuec}
		END
		${valueg}= 	Get Clipboard Content
		IF  $valueg != $value
			${value}= 	Set Variable 		${valueg}
		END
		IF 	$platform == 'macos'
			Sleep    10 ms
			Press Combination 	KEY.command 	c
			Sleep    10 ms
			${valueg}= 	Get Clipboard Content
			IF  $valueg != $value
				${value}= 	Set Variable 		${valueg}
			END
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
	Take A Screenshot
	${value2}= 	Get Text Value To Right Of		${label}
	WHILE 	$value2 != $value 		limit=10
		${x}= 	Evaluate 	${x}+10
		${offsetx}= 	Evaluate 	${offsetx}+10
		@{coordinates}= 	Create List 	${x} 	${y}
		Move To 	${coordinates}
		Click
		Double Click
		Type 	${value}
		Take A Screenshot
		${value2}= 	Get Text Value To Right Of		${label}
	END
	Should Be Equal As Strings    ${value}    ${value2}

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
	[Arguments]		${bttnname}
	${bttnnamel}= 	Convert To Lower Case 	${bttnname}
	${img}=	Set Variable		reporter_${platform}_button_${bttnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	Take A Screenshot

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
	Take A Screenshot

Wait For Status
	[Arguments]		${status}	${timeout}=300
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		reporter_${platform}_status_${statusl}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	Sleep 	${sssleep}
	Take A Screenshot

Open GUI
	[Arguments]		@{appargs}
	${var}= 	Get Variables
	Log 	${var}
	Get Platform
	${keyword}= 	Set Variable 	Open GUI ${platform}
	Run Keyword 	${keyword} 	@{appargs}

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
	${process}= 	Start Process 	${cmd_reporter} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt

	Set Suite Variable 	$process 	${process}
	# reporter_windows_status_previewloaded
	# Wait For Status 	PreviewLoaded
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI ubuntu
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_reporter} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI macos
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile} 	-g 	5 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	${cmd_reporter} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


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
	Log 	${result.stderr}
	Should Not Contain 	${result.stderr} 	Traceback
	Should Be Equal As Integers 	${result.rc} 	0

Close GUI windows
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	# Press Combination 	Key.f4 	Key.alt
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI ubuntu
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI macos
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		reporter_${platform}_menu_python3.png
	Click Image		reporter_${platform}_button_closewindow.png
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
	RETURN	${location}${/}RFSwarmReporter.ini

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
	Take A Screenshot
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
