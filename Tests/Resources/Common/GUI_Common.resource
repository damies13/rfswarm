*** Settings ***
Documentation 	
...    This resource file contains keywords related to the basic GUI functions in the rfswarm components (Manager and Reporter)
...    Run "GUI Suite Initialization ${component}" keyword to set the GUI and basic suite configuration.

Resource 	Common.resource 	# basic keywords

Library 	OCRLibrary
Library 	ImageHorizonLibrary

*** Variables ***
${CONFIDENCE} 		${0.9}
${IMAGE_DIR} 		${None}

${DEBUG_SCREENSHOTS} 		${False}
${DEFAULT_IMAGE_TIMEOUT} 	${30}

&{POPUPS} 		&{EMPTY}

*** Keywords ***
GUI Suite Initialization ${component}
	[Documentation] 	This keyword must be run to set up the suite for GUI keywords. The component must be chosen between: Manager, Reporter

	Basic Suite Initialization ${component} 	# basic suite configuration

	VAR 	${COMPONENT} 	${component} 	scope=SUITE
	VAR 	${IMAGE_DIR} 	${CURDIR}${/}..${/}..${/}Regression${/}${COMPONENT}${/}Images${/}file_method 	scope=SUITE
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
	[Setup] 	Sleep 	2s
	Take A Screenshot

	GROUP    Bash is requesting to bypass the system private window picker and directly access your screen
		IF    "Bash" not in ${POPUPS}
			Set To Dictionary 	${POPUPS} 	Bash=${False}

			${result}= 	Run Keyword And Return Status
			...    Click OS Button 		allow

			IF 	${result}
				Set To Dictionary 	${POPUPS} 	Bash=${True}
				Take A Screenshot
			END
		END
	END
		
	GROUP    Click Ignore on python quit unexpectedly
		# this needs to run all the time just in case
		Sleep 	2s
		${result}= 	Run Keyword And Return Status
		...    Click OS Button 		ignore

		Sleep 	0.1
		IF 	${result}
			Take A Screenshot
		END
	END

	GROUP    Analytics screen
		IF    "Analytics" not in ${POPUPS}
			Set To Dictionary 	${POPUPS} 	Analytics=${True}
			# https://derflounder.wordpress.com/2025/08/12/suppressing-the-analytics-screen-with-a-configuration-profile-on-macos-sequoia/
			# https://apple.stackexchange.com/questions/117753/how-to-stop-setup-assistant-from-showing-up-on-every-restart-on-mac-mini-with-os
			# https://www.google.com/search?q=kill+com.apple.SetupAssistant.managed+from+command+line&oq=kill+com.apple.SetupAssistant.managed+from+command+line&gs_lcrp=EgZjaHJvbWUyCwgAEEUYChg5GKABMgkIARAhGAoYoAEyCQgCECEYChigAdIBCDU5MTFqMGo3qAIAsAIA&client=ubuntu-chr&sourceid=chrome&ie=UTF-8&source=chrome.ob
			# killall "Setup Assistant"
			# killall -9 "Setup Assistant"
			${result}= 	Kill If Still Running 	Setup Assistant
			# - determine way to know if it was closed and only take screenshot if it was
			Log 	result: ${result} 
			IF 	${result}
				Take A Screenshot
			END
		END
	END


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

Wait For Expected
	[Arguments]		${expected} 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${expectedl}= 	Convert To Lower Case 	${expected}
	# VAR 	${glob}= 	${IMAGE_DIR}/reporter_${PLATFORM}_expected_${statusl}*.png
	@{files}= 	List Files In Directory 	${IMAGE_DIR} 	${comp}_${PLATFORM}_expected_${expectedl}*.png
	# VAR 	${img}=		reporter_${PLATFORM}_expected_${expectedl}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wiggle Mouse
	# Take A Screenshot
	# Wait For 	${img} 	 timeout=${timeout}

	FOR 	${img} 	IN 	@{files}
		${status}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=${timeout}
		IF 	${status}
			BREAK
		END
	END

	IF 	${status} is False
		Fail 	${expected} not found
	END

	Sleep 	0.1
	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click OS Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	# VAR 	${img} 	${comp}_${PLATFORM}_button_${btnnamel}.png
	@{files}= 	List Files In Directory 	${IMAGE_DIR} 	${PLATFORM}_dlgbtn_${btnnamel}*.png
	Log 	Click Button ${btnname} 	console=True
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	FOR 	${img} 	IN 	@{files}
		Wait For 	${img} 	 timeout=${timeout}
		@{coordinates}= 	Locate 	${img}
		${status}= 	Run Keyword And Return Status 	Click Image 	${img}
		IF 	${status}
			Sleep 	0.1
			BREAK
		END
	END

	IF 	${status} is False
		Fail 	${btnname} not found
	END

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

