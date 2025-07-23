*** Settings ***
Resource 	GUI_Common.resource

*** Keywords ***
# # # # # # #
# CLICK ... #
# # # # # # #
Click Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${comp}_${PLATFORM}_button_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Wait For Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click Dialog Button
	[Arguments]		${btnname} 		${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_dlgbtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click Tab
	[Arguments]		${tabname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	VAR 	${img} 	${comp}_${PLATFORM}_tab_${tabnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Select Option
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	VAR 	${img} 	${comp}_${PLATFORM}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Selected Option Should Be
	[Arguments]		${optname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${optnamel}= 	Convert To Lower Case 	${optname}
	VAR 	${img} 	${comp}_${PLATFORM}_option_${optnamel}.png
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click Menu
	[Arguments]		${menuname}
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${menunamel}= 	Convert To Lower Case 	${menuname}
	VAR 	${img} 	${comp}_${PLATFORM}_menu_${menunamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click CheckBox
	[Arguments]		${status} 		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	${statusl}= 	Convert To Lower Case 	${status}
	VAR 	${img} 	${PLATFORM}_checkbox_${statusl}_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click RadioBtn
	[Arguments]		${btnname}
	${btnnamel}= 	Convert To Lower Case 	${btnname}
	VAR 	${img} 	${PLATFORM}_radiobtn_${btnnamel}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	@{coordinates}= 	Locate 	${img}
	Click Image 	${img}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click ${item} With Vertical Offset
	[Arguments]		${image_name}	${offset}=0 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move down].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	VAR 	${img} 	${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Below Of	${coordinates}	${offset}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

Click ${item} With Horizontal Offset
	[Arguments]		${image_name}	${offset}=0 	${timeout}=${DEFAULT_IMAGE_TIMEOUT}
	[Documentation]	Click the item with the offset. An item can be: Label, Button, ...
	...	[the point (0.0) is in the top left corner of the screen, so give positive values when you want to move right].
	${comp}= 		Convert To Lower Case 	${COMPONENT}
	${image_name}= 	Convert To Lower Case 	${image_name}
	${item}= 	Convert To Lower Case 	${item}
	VAR 	${img} 	${comp}_${PLATFORM}_${item}_${image_name}.png
	Log 	${CURDIR}
	Log 	${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate 	${img}
	Log	${coordinates}
	Click To The Right Of	${coordinates}	${offset}
	Sleep 	0.1

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

File Open Dialogue Select File
	[Arguments]		${filepath}
	Run Keyword		File Open Dialogue ${PLATFORM} Select File 			${filepath}

	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

File Open Dialogue ubuntu Select File
	[Arguments]		${filepath}
	Sleep	2
	Click Label With Horizontal Offset 	file_name 	50
	Sleep	0.5
	Type 		${filepath} 	Key.ENTER
	Sleep	0.5

	# Click Dialog Button 	open
	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

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

	# Click Dialog Button 	open
	Sleep	0.5
	[Teardown] 	Run Keyword If 	${DEBUG_SCREENSHOTS} 	Take A Screenshot

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
