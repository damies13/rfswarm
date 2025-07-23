*** Settings ***
Documentation 	This resource file contains keywords for Reporter GUI only.

Resource 	../../../Common/GUI_Common.resource
Resource 	../../../Common/GUI_Click.resource
Resource 	../../../Common/GUI_Text.resource

Library 	ArchiveLibrary
Library 	DocTest.VisualTest
Library 	XML 	use_lxml=True

Variables 	report_expected_data.yaml

*** Keywords ***
Create New Section
	[Arguments]		${sectname}

	Click Button 			AddSection
	Take A Screenshot
	${img}=	Set Variable		reporter_${PLATFORM}_label_sectionname.png
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
	${img}=	Set Variable		reporter_${PLATFORM}_section_${sectnamel}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	# Take A Screenshot

Select Field With Label
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}=	Set Variable		reporter_${PLATFORM}_label_${labell}.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
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
	Sleep 	0.1
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot

Wait For Status
	[Arguments]		${status}	${timeout}=${1800}
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		reporter_${PLATFORM}_status_${statusl}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wiggle Mouse
	# Take A Screenshot
	Wait For 	${img} 	 timeout=${timeout}
	Sleep 	0.1
	# Take A Screenshot

Save Template File OS DIALOG
	[Arguments]		${template_name}
	Sleep	5
	Type	${template_name}
	# Take A Screenshot
	Click Dialog Button		save
	Sleep	1

Open Template File OS DIALOG
	[Arguments]		${template_name}
	Sleep	5
	Type	${template_name}.template
	Take A Screenshot
	Click Dialog Button		open
	Sleep	1

Navigate to and check Desktop Icon
	VAR 	${projname}= 		rfswarm-reporter 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Reporter 		scope=TEST
	Run Keyword 	Navigate to and check Desktop Icon For ${PLATFORM}

Navigate to and check Desktop Icon For MacOS

	# Release Fn Key

	Take A Screenshot

	# open go menu
	${img}=	Set Variable		${PLATFORM}_finder_menu_go.png
	Click Image		${img}
	# Sleep 	0.3
	# Take A Screenshot

	# select Go to Folder from Go menu
	${img}=	Set Variable		${PLATFORM}_finder_menu_gotofolder.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	Click Image		${img}
	# Sleep 	0.3
	# Take A Screenshot


	# # open finder
	# ${img}=	Set Variable		${PLATFORM}_finder.png
	# Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# @{coordinates}= 	Locate		${img}
	# Click Image		${img}
	# ${img}=	Set Variable		${PLATFORM}_finder_toolbar.png
	# Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot
	#
	# # un-maximise finder if maximised
	# ${img}=	Set Variable		${PLATFORM}_finder.png
	# ${passed}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=1
	# IF 	not ${passed}
	# 	Take A Screenshot
	# 	Press Combination 	KEY.fn 	KEY.f
	# END
	# Sleep 	0.3
	# Take A Screenshot
	#
	# ${img}=	Set Variable		${PLATFORM}_finder_toolbar.png
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
	Sleep 	0.3
	Press Combination 	KEY.backspace
	Sleep 	0.3
	# VAR 	@{top_corner} 	${100} 	${100}
	# Click To The Below Of 	${top_corner} 	${20}

	Take A Screenshot
	${img}=	Set Variable		${PLATFORM}_finder_gotofolder.png
	${status}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=${20}
	IF  ${status}
		Run Keyword And Ignore Error 	Click Image		${img}
	END

	# Type 		/Applications
	Evaluate 		pynput.keyboard.Controller().type('/Applications') 		modules=pynput.keyboard

	# Sleep 	0.3
	# Take A Screenshot
	${img}=	Set Variable		${PLATFORM}_finder_gotoapplications.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot

	Press Combination 	KEY.enter
	# Sleep	0.5
	# Take A Screenshot
	${img}=	Set Variable		${PLATFORM}_finder_facetime.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot

	# Filter/Search /Applications?
	Type 	RFSwarm
	# Sleep 	0.3
	${img}=	Set Variable		${PLATFORM}_finder_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	Take A Screenshot

	# Open Launchpad (F4?)
	# Press Combination   key.f4
	${img}=	Set Variable		${PLATFORM}_launchpad.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Sleep 	1
	${img}=	Set Variable		${PLATFORM}_launchpad_search.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot

	# Search Launchpad
	Type 	RFSwarm
	# Sleep 	0.3
	Take A Screenshot

	# Check for Icon
	# macos_launchpad_rfswarm_reporter.png
	${img}=	Set Variable		${PLATFORM}_launchpad_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# Take A Screenshot

	Press Combination 	KEY.ESC
	# Take A Screenshot

Navigate to and check Desktop Icon For Windows

	Take A Screenshot
	# Open Start Menu
	Sleep 	0.5
	${img}=	Set Variable		${PLATFORM}_start_menu.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Take A Screenshot

	${img}=	Set Variable		${PLATFORM}_start_menu_rfswarm_reporter.png
	Run Keyword And Ignore Error 	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT} 	# temp. fix

	# Navigate Start Menu
	Type 	RFSwarm
	Sleep 	0.5
	Take A Screenshot

	# Check for Icon
	${img}=	Set Variable		${PLATFORM}_search_rfswarm_reporter.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}

	Press Combination 	KEY.ESC

Navigate to and check Desktop Icon For Ubuntu

	Take A Screenshot
	# Open Menu
	${img}=	Set Variable		${PLATFORM}_lxqt_menu.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	# Move To 	${coordinates}
	# Click 	button=right
	Sleep 	0.5
	Take A Screenshot

	# Navigate Menu
	# lxqt_programming_menu.png
	${img}=	Set Variable		${PLATFORM}_lxqt_programming_menu.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	Click Image		${img}
	Sleep 	0.5
	Take A Screenshot

	# Check for Icon
	# ubuntu_lxqt_rfswarm_reporter_menu.png
	${img}=	Set Variable		${PLATFORM}_lxqt_rfswarm_reporter_menu.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}

	Press Combination 	KEY.ESC

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
	Run Keyword 	Choose Colour With ${PLATFORM} Colour Picker 		${hex_colour}

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

	# Locate 	reporter_${PLATFORM}_dlg_aaa.png

Release Fn Key

	IF 	$platform == 'macos'
		# https://github.com/asweigart/pyautogui/issues/796
		${result}= 		Evaluate 	pyautogui.keyUp('fn') 	modules=pyautogui
		Log    ${result}

	END

#
