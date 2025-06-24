*** Settings ***
Documentation 	
...    This resource file contains keywords related to the basic GUI functions in the rfswarm components (Manager and Reporter)
...    Run "GUI Suite Initialization ${component}" keyword to set the GUI and basic suite configuration.

Resource 	Common.resource 	# basic keywords

Library 	OCRLibrary
Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}

*** Variables ***
${CONFIDENCE} 		${0.9}
${IMAGE_DIR} 		${None}

${DEBUG_SCREENSHOTS} 		${False}
${DEFAULT_IMAGE_TIMEOUT} 	${120}

*** Keywords ***
GUI Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the suite for GUI keywords. The component must be chosen between: Manager, Reporter

	Basic Suite Initialization ${component} 	# basic suite configuration

	Set Suite Variable 	${COMPONENT} 	${component}
	Set Suite Variable 	${IMAGE_DIR} 	${CURDIR}${/}..${/}Regression${/}${COMPONENT}${/}Images${/}file_method
	Set Confidence 		${CONFIDENCE}
	ImageHorizonLibrary.Set Reference Folder 	${IMAGE_DIR}

	Log 	\t[ === GUI suite configuration has been initiated for ${COMPONENT} === ] 	console=True
	Log 	image dir = ${IMAGE_DIR} 	console=True
	Log 	confidence level = ${CONFIDENCE} 	console=True
	Log 	default image timeout = ${DEFAULT_IMAGE_TIMEOUT} 	console=True
	Log 	------------------------------------------------------------------------------\n\n\n 	console=True

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

#TODO: Chceck if it works
Resize Window
	[Arguments]		${x}=0		${y}=0
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${img}=	Set Variable		${comp}_${PLATFORM}_corner_resize.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate		${img}
	@{coordinates2}= 	Create List 	${{${coordinates[0]}+${x}}} 	${{${coordinates[1]}+${y}}}
	Move To 	@{coordinates}
	Mouse Down
	Move To 	@{coordinates2}
	# Take A Screenshot
	Mouse Up

# # # # #
# INI:  #
# # # # #

Set ${component_name} INI Window Size
	[Documentation] 	Pass the: Manager, Reporter or Agent
	[Arguments]		${width}=${None}	${height}=${None}
	Log 	${width}
	Log 	${height}
	IF	"${width}" != "${None}"
		Change ${component_name} INI Option 	GUI 		win_width 	${width}
	END
	IF	"${height}" != "${None}"
		Change ${component_name} INI Option 	GUI 		win_height 	${height}
	END

# # # # # # #
# CLICK ... #
# # # # # # #

Click Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}= 	Set Variable 	${comp}_${PLATFORM}_button_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	# IF  "${PLATFORM}" == "windows"
	# 	Set Confidence	0.85
	# END
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
	# IF  "${PLATFORM}" == "windows"
	# 	Set Confidence 	0.9
	# END

Wait For Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable 	${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click Tab
	[Arguments]		${tabname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		${comp}_${PLATFORM}_tab_${tabnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Select Option
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}= 	Set Variable		${comp}_${PLATFORM}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Selected Option Should Be
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}= 	Set Variable		${comp}_${PLATFORM}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}

Click Menu
	[Arguments]		${menuname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	${img}=	Set Variable		${comp}_${PLATFORM}_menu_${menunamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click CheckBox
	[Arguments]		${status} 		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		${PLATFORM}_checkbox_${statusl}_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click RadioBtn
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${img}=	Set Variable		${PLATFORM}_radiobtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click ${item} With Vertical Offset
	[Arguments]		${image_name}	${offset}=0
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	${img}=	Set Variable		${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click ${item} With Horizontal Offset
	[Arguments]		${image_name}	${offset}=0
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	${img}=	Set Variable		${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

File Open Dialogue Select File
	[Arguments]		${filepath}
	Run Keyword		File Open Dialogue ${PLATFORM} Select File 			${filepath}
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

File Open Dialogue ubuntu Select File
	[Arguments]		${filepath}
	Sleep	2
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath} 	Key.ENTER
	Sleep	0.5
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
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
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
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
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
	Press Combination 	KEY.down	#choose paste option(should be first)
	Press key.enter 1 Times		#execute paste option
	Sleep	0.5
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
	Press key.enter 1 Times
	Sleep	0.5
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot
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
	IF 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Get Text Value To Right Of
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${comp}= 	Convert To Lower Case 	${COMPONENT}
	${img}= 	Set Variable		${comp}_${PLATFORM}_label_${labell}.png

	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}

	Make Clipboard Not None 	# reset clipboard
	${b4value}= 	Get Clipboard Content
	Click To The Right Of Image 	${img} 	${offsetx}
	Sleep    10 ms
	Click To The Right Of Image 	${img} 	${offsetx}
	Sleep    10 ms
	${value}= 	Copy From The Right Of 	${img} 	${offsetx}
	Take A Screenshot

	WHILE 	$b4value == $value 		limit=15
		Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
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
	${img}= 	Set Variable		${comp}_${PLATFORM}_label_${labell}.png
	${imgsize}= 	Get Image Size 	${IMAGE_DIR}${/}${img}
	Log		${imgsize}
	${offsetx2}= 	Evaluate 	int(${imgsize}[0]/2)+${offsetx}
	Log		${offsetx}
	Log		${CURDIR}
 	Log		${IMAGE_DIR}

	@{coordinates}= 	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	${x}= 	Evaluate 	${coordinates}[0]+${offsetx2}
	${y}= 	Evaluate 	${coordinates}[1]+${offsety}
	@{coordinates}= 	Create List 	${x} 	${y}
	Move To 	${coordinates}
	Click
	Sleep 	0.5
	Click
	Sleep 	0.3
	IF  "${PLATFORM}" == "macos"
		Press Combination	KEY.command		KEY.a
	ELSE
		Press Combination	KEY.ctrl		KEY.a
	END
	Take A Screenshot
	Sleep 	0.3

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
	IF  "${PLATFORM}" == "macos"
		Press Combination	KEY.command		KEY.v
	ELSE
		Press Combination	KEY.ctrl		KEY.v
	END
	Take A Screenshot

	IF 	$platform == 'macos'
		Press Combination 	Key.Shift 	Key.End

		Press Combination 	Key.Delete
		Take A Screenshot

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

			IF  "${PLATFORM}" == "macos"
				Press Combination	KEY.command		KEY.v
			ELSE
				Press Combination	KEY.ctrl		KEY.v
			END

			Take A Screenshot
			${value2}= 	Get Text Value To Right Of		${label} 		${offsetx}

		END
		Should Be Equal As Strings 	${value} 	${value2}

	END
