*** Settings ***
Resource 	GUI_Common.resource

*** Keywords ***
# # # # # # #
# CLICK ... #
# # # # # # #
Click Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	# VAR 	${img} 	${comp}_${PLATFORM}_button_${btnnamel}.png
	@{files}= 	List Files In Directory 	${IMAGE_DIR} 	${comp}_${PLATFORM}_button_${btnnamel}*.png
	Log 	Click Button ${btnname} 	console=True
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	TRY
		VAR    ${img} 	${files[0]}
		Wait For 	${img} 	 timeout=${timeout}
	EXCEPT
		Log 	${img} not found
	END

	VAR    ${status} 	${False}
	FOR 	${img} 	IN 	@{files}
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

Wait For Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click Tab
	[Arguments]		${tabname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	VAR 	${img} 	${comp}_${PLATFORM}_tab_${tabnamel}.png
	Log 	Click Tab ${tabname} 	console=True
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Select Option
	[Arguments]		${optname}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	VAR 	${img} 	${comp}_${PLATFORM}_option_${optnamel}.png

	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	IF  not ${status} and '${comp}' == 'reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Selected Option Should Be
	[Arguments]		${optname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	VAR 	${img} 	${comp}_${PLATFORM}_option_${optnamel}.png

	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click Menu
	[Arguments]		${menuname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	VAR 	${img} 	${comp}_${PLATFORM}_menu_${menunamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click CheckBox
	[Arguments]		${status} 		${btnname}
	[Tags] 	Manager 	Reporter
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${statusl}= 	Convert To Lower Case 	${status}
	VAR 	${img} 	${PLATFORM}_checkbox_${statusl}_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	Set Confidence 		${0.85}	#temporarily lower Confidence
	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	IF  not ${status} and '${COMPONENT}' == 'Reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1
	Set Confidence 		${CONFIDENCE}	#return Confidence to default

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click RadioBtn
	[Arguments]		${btnname}
	[Tags] 	Manager 	Reporter
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_radiobtn_${btnnamel}.png
	Log 	Click Radio Button ${btnname} 	console=True
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	IF  not ${status} and '${COMPONENT}' == 'reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click ${item} With Vertical Offset
	[Arguments]		${image_name}	${offset}=0 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	VAR 	${img} 	${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${timeout}
	IF  not ${status} and '${comp}' == 'reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

DoubleClick ${item} With Vertical Offset
	[Arguments]		${image_name}	${offset}=0 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	VAR 	${img} 	${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${timeout}
	IF  not ${status} and '${comp}' == 'reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	${newy} 	Evaluate 	${coordinates}[1] + ${offset}
	VAR 	@{newcoordinates} 	${coordinates}[0] 	${newy}
	# Move To 	${newcoordinates}
	Double Click
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

Click ${item} With Horizontal Offset
	[Arguments]		${image_name}	${offset}=0 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Tags] 	Manager 	Reporter
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	VAR 	${img} 	${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}

	${status}= 	Run Keyword And Return Status
	...    Wait For 	${img} 	 timeout=${timeout}
	IF  not ${status} and '${comp}' == 'reporter' and '${PLATFORM}' == 'macos'
		Handle Reporter Missing Settings
		Wait For 	${img} 	 timeout=5
	END
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

File Open Dialogue Select File
	[Arguments]		${filepath}
	[Tags] 	Manager 	Reporter
	Run Keyword		File Open Dialogue ${PLATFORM} Select File 			${filepath}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

File Open Dialogue ubuntu Select File
	[Arguments]		${filepath}
	[Tags] 	Manager 	Reporter
	Sleep	2
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath} 	Key.ENTER
	Sleep	0.5

	# Click Dialog Button 	open
	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

File Open Dialogue windows Select File
	[Arguments]		${filepath}
	[Tags] 	Manager 	Reporter
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

	# Click Dialog Button 	open
	Sleep	0.5
	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} or "${KEYWORD STATUS}" == "FAIL"     Take A Screenshot

File Open Dialogue macos Select File
	[Arguments]		${filepath}
	[Tags] 	Manager 	Reporter
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
	# Click Dialog Button 	open
	Click OS Button 		open
	# Type 		Key.BACKSPACE 	Key.DELETE
	# Click Dialog Button 	open

Handle Reporter Missing Settings
	[Documentation]
	...    Reporter section settings tab in MacOS environment is sometimes not being fully rendered.
	...    To cover that, it's possible to regenerate the settings by clicking preview tab and then settings once again.
	...    This keyword is simply doing these steps but only once.
	[Tags] 	Reporter 	Issue #382
	[Setup] 	Should Be Equal 	${COMPONENT} 	Reporter 	msg=This keyword is designed for Reporter only.
	[Timeout] 	10s
	Take A Screenshot
	Run Keyword And Ignore Error 	Click Tab 	Preview 	timeout=2
	Sleep 	3s
	Run Keyword And Ignore Error 	Click Tab 	Settings 	timeout=2
	Take A Screenshot

