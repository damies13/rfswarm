*** Settings ***
Resource 	GUI_Common.resource

Resource 	RFS_Components.resource
Resource 	GUI_Click.resource

*** Keywords ***
# # # # # # # # # # # # # # #
# Open/Close component GUI  #
# # # # # # # # # # # # # # #

Handle Donation Reminder
	${comp}= 	Convert To Lower Case 	${COMPONENT}
	IF  '${COMPONENT}' == 'Manager'
		Run Keyword And Ignore Error 	Wait For 	manager_${PLATFORM}_button_runscriptrow.png 	timeout=8
		${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		2
		Run Keyword And Ignore Error 	Wait For 	manager_${PLATFORM}_button_runscriptrow.png 	timeout=8
	ELSE IF  '${COMPONENT}' == 'Reporter'
		Run Keyword And Ignore Error 	Wait For 	reporter_${PLATFORM}_button_generateexcel.png 	timeout=8
		${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		2
		Run Keyword And Ignore Error 	Wait For 	reporter_${PLATFORM}_button_generateexcel.png 	timeout=8
	END

	IF  not ${found}
		${found}= 	Run Keyword And Return Status 	Click Button 	MaybeLater 		4
	END
	VAR 	${DonationReminder} 	${found} 		scope=TEST

Open ${component_name} GUI
	[Documentation] 	Open one of the RFSwarm applications for GUI purposes. Pass the: Manager, Reporter or Agent
	[Arguments] 	@{appargs}  ${envargs}=${None}
	${comp} 	Convert To Lower Case 	${component_name}
	${var}= 	Get Variables
	Log 	${var}

	Press Combination 	Key.esc
	Wiggle Mouse

	VAR 	${noargs} 	${False}
	${len} 	Get Length 	${appargs}
	IF  ${len} == ${0}
		VAR 	${noargs} 	${True}
	END

	Run Keyword 	Run ${component_name} CLI 	@{appargs}  noargs=${noargs}  envargs=${envargs}

	IF 	'-n' in ${appargs} or '--nogui' in ${appargs}
		Sleep 	5
	ELSE
		Handle Donation Reminder
		${running}= 	Is Process Running 	${PROCESS_${comp}}
		IF 	not ${running}
			Take A Screenshot
			Fail 		${component_name} not running
		END
	END

Close ${component_name} GUI
	[Documentation] 	Closes one of the RFSwarm applications with GUI. Pass the: Manager or Reporter
	${comp} 	Convert To Lower Case 	${component_name}
	Run Keyword And Ignore Error 	Click Dialog Button 	cancel 	0.01
	Run Keyword And Ignore Error 	Click Dialog Button 	no 		0.01

	IF  '${comp}' == 'agent'
		Stop Agent CLI
		RETURN
	END

	IF 	${PROCESS_${comp}}
		${running}= 	Is Process Running 	${PROCESS_${comp}}
		IF 	${running}
			Log 	${\n}Closing ${component_name} GUI ... 	console=True

			# make sure the window is the active window first
			IF 	'${component_name}' == 'Manager'
				Run Keyword And Ignore Error 	Click Image 	manager_${PLATFORM}_tab_about.png
				Run Keyword And Ignore Error 	Click Image 	manager_${PLATFORM}_tab_run.png
			ELSE IF 	'${component_name}' == 'Reporter'
				IF  '${PLATFORM}' == 'macos'
					Run Keyword And Ignore Error 	Click Button With Vertical Offset 	OpenTemplate 	offset=-20 	timeout=1
				ELSE
					Run Keyword And Ignore Error 	Click Image 	reporter_${PLATFORM}_menu_results.png
				END
			END

			Sleep 	1
			Press Key.esc 3 Times
			Sleep 	1
			IF  '${PLATFORM}' == 'macos'  Press Combination  Key.command  q  ELSE  Press Combination  Key.ctrl  x
			Sleep	3

			${running}= 	Is Process Running 	${PROCESS_${comp}}
			IF 	${running}
				Press Combination 	Key.esc
				IF  '${PLATFORM}' == 'macos'  Press Combination  Key.command  q  ELSE  Press Combination  Key.ctrl  x
			END

		ELSE
			Log 	${component_name} is not running! 	console=True
			${result}= 	Wait For Process 	${PROCESS_${comp}} 	timeout=60
			Run Keyword And Ignore Error 	Check Logs 	${component_name} 	# TODO: remove ignore error and check if test cases fail. Log issues for failing test cases
			# Should Be Equal As Integers 	${result.rc} 	0

			RETURN
		END

		Sleep 	2s
		Run Keyword And Ignore Error 	Click Dialog Button 	no 		1

		${result}= 		Wait For Process 	${process_${comp}} 	timeout=15
		${running}= 	Is Process Running 	${PROCESS_${comp}}
		IF 	not ${running}
			Log 	*=== ${component_name} closed with GUI ===* 	console=True
			TRY
				Log 	${component_name} exited with: ${result.rc} 	console=${True}
				# Should Be Equal As Integers 	${result.rc} 	0

				Log		stdout_path: ${result.stdout_path} 		console=True
				Log		stderr_path: ${result.stderr_path} 		console=True

				Show Log 	${result.stdout_path}
				Show Log 	${result.stderr_path}

			EXCEPT 	AS 	${error}
				Log 	error: ${error} 		console=true
			END

		ELSE
			Log 	Closing GUI with CLI 	console=True
			Take A Screenshot
			Run Keyword 	Stop ${component_name} CLI 	# close with cli signal
			RETURN
		END

	END

	Sleep 	0.5
	Run Keyword And Ignore Error 	Check Logs 	${component_name} 	# TODO: remove ignore error and check if test cases fail. Log issues for failing test cases
	${running}= 	Is Process Running 	${PROCESS_${comp}}
	Run Keyword If 	${running} 	Fail 	Failed to close ${component_name}

	[Teardown] 	Run Keywords
	...    Set Suite Variable 	${PROCESS_${comp}} 	${None} 	AND 	Kill If Still Running 	${CMD_${comp}}

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
