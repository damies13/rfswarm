*** Settings ***
Resource 	GUI_Common.robot

Test Teardown 	Close GUI

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest		windows-latest		ubuntu-latest
	Open GUI
	Wait For Status 	PreviewLoaded
	# Close GUI

Select Preview Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Open GUI
	Wait For Status 	PreviewLoaded
	Click Tab 	 Preview
	# Close GUI

	# Accessability Settings test was to verify Terminal is set to 'check'
	# 		https://stackoverflow.com/questions/62035751/pyautogui-not-running-on-mac-catalina
	# MacOS Accessability Settings
	# 	[Tags]	macos-latest
	#
	# 	# setting -> security & privacy -> Accessibility -> Terminal 'check'
	#
	# 	# Open Settings
	# 	${img}=	Set Variable		${platform}_settings.png
	# 	Wait For 	${img} 	 timeout=${default_image_timeout}
	# 	@{coordinates}= 	Locate		${img}
	# 	Click Image		${img}
	#
	#
	# 	# Open security & privacy
	# 	${img}=	Set Variable		${platform}_settings_privsec.png
	# 	Wait For 	${img} 	 timeout=${default_image_timeout}
	# 	Click Image		${img}
	#
	# 	# Open Accessibility
	# 	${img}=	Set Variable		${platform}_settings_accessibility.png
	# 	${imgsd}=	Set Variable		${platform}_settings_scrolldown.png
	# 	${found}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=10
	# 	WHILE 	not ${found}
	# 		Take A Screenshot
	# 		Click Image		${imgsd}
	# 		${found}= 	Run Keyword And Return Status 	Wait For 	${img} 	 timeout=10
	# 	END
	# 	Take A Screenshot
	# 	Click Image		${img}
	#
	# 	# Open Check Terminal
	#
	# 	Sleep 	10.5
	# 	Take A Screenshot
	# 	Fatal Error 	Intentional Fail
	#
	# 	Click Image		reporter_${platform}_button_closewindow.png
	# 	Run Keyword And Ignore Error 	Click Image		reporter_${platform}_button_closewindow.png
	# 	Take A Screenshot
	# 	Sleep 	0.5
	#
	#
	# 	Fatal Error 	Intentional Fail
	#
	# 	[Teardown] 		Fatal Error 	Intentional Fail

# Intentional Fail
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
# 	...								Ensure this is commented out before release or pull request
# 	Fail

*** Keywords ***
