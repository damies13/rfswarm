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

	VAR 	${COMPONENT} 	${component} 	scope=SUITE
	VAR 	${IMAGE_DIR} 	${CURDIR}${/}..${/}Regression${/}${COMPONENT}${/}Images${/}file_method 	scope=SUITE
	Set Confidence 		${CONFIDENCE}
	ImageHorizonLibrary.Set Reference Folder 	${IMAGE_DIR}
	ImageHorizonLibrary.Set Screenshot Folder 	${OUTPUT DIR}

	IF 	'${PLATFORM}' == 'macos'
		Take A Screenshot
		Run Keyword And Ignore Error 	Handle MacOS Pop-ups
	END

	Log 	\t[ === GUI suite configuration has been initiated for ${COMPONENT} === ] 	console=True
	Log 	image dir = ${IMAGE_DIR} 	console=True
	Log 	confidence level = ${CONFIDENCE} 	console=True
	Log 	default image timeout = ${DEFAULT_IMAGE_TIMEOUT} 	console=True
	Log 	------------------------------------------------------------------------------\n\n\n 	console=True

Handle MacOS Pop-ups
	[Tags]  macos-latest
	[Documentation]  The MacOS system sometimes displays pop-up windows related to permissions. This keyword is intended to accept/ignore these pop-up windows.
	[Setup] 	Sleep 	1s
	Take A Screenshot
	
	VAR 	${img} 	macos_dlgbtn_allow_grayed.png
	Run Keyword And Ignore Error
	...    Wait For 	${img} 	 timeout=2

	Run Keyword And Ignore Error
	...    Click Image 	${img}

	VAR 	${img} 	macos_dlgbtn_allow.png
	Run Keyword And Ignore Error
	...    Wait For 	${img} 	 timeout=2

	${result}= 	Run Keyword And Return Status
	...    Click Image 	${img}

	Sleep 	0.1

Press ${key} ${n} Times
	[Documentation] 	Provide full name. For example: Key.tab
	Sleep	1
	FOR  ${i}  IN RANGE  0  ${n}
		Press Combination 	${key}
	END

Wiggle Mouse
	Move To 	10 	10
	Move To 	20 	20

Get Image Size
	[Arguments] 	${imgfile}
	# ahrrrg windows paths, PIL.Image.open doesn't like them, need to escape / replace \\
	# ${imgfile}= 	Evaluate    "${imgfile}".replace('\\' '/')
	${img}= 	Evaluate    PIL.Image.open(r'${imgfile}') 	PIL.Image
	VAR 	${imgsize} 	${img.size}
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
	VAR 	${img} 	${comp}_${PLATFORM}_corner_resize.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate		${img}
	@{coordinates2}= 	Create List 	${{${coordinates[0]}+${x}}} 	${{${coordinates[1]}+${y}}}
	Move To 	@{coordinates}
	Mouse Down
	Move To 	@{coordinates2}
	# Take A Screenshot
	Mouse Up
