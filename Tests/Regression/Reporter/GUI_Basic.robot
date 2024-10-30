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

MacOS Accessability Settings
	[Tags]	macos-latest

	# setting -> security & privacy -> Accessibility -> Terminal 'check'

	# Open Settings
	${img}=	Set Variable		${platform}_finder.png
	Wait For 	${img} 	 timeout=${default_image_timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}

	# Open security & privacy
	# Open Accessibility
	# Open Check Terminal

	Take A Screenshot


# Intentional Fail
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
# 	...								Ensure this is commented out before release or pull request
# 	Fail

*** Keywords ***
