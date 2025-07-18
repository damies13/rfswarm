*** Settings ***
Resource 	GUI_Common.resource

*** Keywords ***
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
	VAR 	${img} 	${comp}_${PLATFORM}_label_${labell}.png

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
			VAR 	${value} 	${valuec}
		END
		${valueg}= 	Get Clipboard Content
		IF  $valueg != $value
			VAR 	${value} 	${valueg}
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
				VAR 	${value} 	${valueg}
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
	VAR 	${img} 	${comp}_${PLATFORM}_label_${labell}.png
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
