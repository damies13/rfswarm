*** Settings ***
Resource 	resources/GUI_Reporter.resource

Suite Setup 	GUI_Common.GUI Suite Initialization Reporter

Test Teardown 	Close Reporter GUI

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest		windows-latest		ubuntu-latest
	Open Reporter GUI
	Wait For Status 	PreviewLoaded

Select Preview Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Open Reporter GUI
	Wait For Status 	PreviewLoaded
	Click Tab 	 Preview

	# Accessability Settings test was to verify Terminal is set to 'check'
	# 		https://stackoverflow.com/questions/62035751/pyautogui-not-running-on-mac-catalina
	# MacOS Accessability Settings
	# 	[Tags]	macos-latest
	#
	# 	# setting -> security & privacy -> Accessibility -> Terminal 'check'
	#
	# 	# Open Settings
	# 	${img}=	Set Variable		${PLATFORM}_settings.png
	# 	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# 	@{coordinates}= 	Locate		${img}
	# 	Click Image		${img}
	#
	#
	# 	# Open security & privacy
	# 	${img}=	Set Variable		${PLATFORM}_settings_privsec.png
	# 	Wait For 	${img} 	 timeout=${DEFAULT_IMAGE_TIMEOUT}
	# 	Click Image		${img}
	#
	# 	# Open Accessibility
	# 	${img}=	Set Variable		${PLATFORM}_settings_accessibility.png
	# 	${imgsd}=	Set Variable		${PLATFORM}_settings_scrolldown.png
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
	# 	Click Image		reporter_${PLATFORM}_button_closewindow.png
	# 	Run Keyword And Ignore Error 	Click Image		reporter_${PLATFORM}_button_closewindow.png
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
