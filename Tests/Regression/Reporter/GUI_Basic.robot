*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}

*** Variables ***
${IMAGE_DIR} 	${CURDIR}${/}Images${/}file_method
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py
${process}		None

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest		windows-latest		ubuntu-latest
	Open GUI
	Wait For Status 	PreviewLoaded
	Close GUI

Select Preview Tab
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	Open GUI
	Wait For Status 	PreviewLoaded
	Click Tab 	 Preview
	Close GUI

First Run
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #147
	${epoch}=	Get Time	epoch
	Open GUI	-i 	blank_${epoch}.ini
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	60
	Close GUI

# Intentional Fail
# 	[Tags]	ubuntu-latest		windows-latest		macos-latest
# 	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
# 	...								Ensure this is commented out before release or pull request
# 	Fail

*** Keywords ***
Click Tab
	[Arguments]		${tabname}
	${tabnamel}= 	Convert To Lower Case 	${tabname}
	${img}=	Set Variable		reporter_${platform}_tab_${tabnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot

Wait For Status
	[Arguments]		${status}	${timeout}=300
	${statusl}= 	Convert To Lower Case 	${status}
	${img}=	Set Variable		reporter_${platform}_status_${statusl}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=${timeout}
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	0.1
	Take A Screenshot

Open GUI
	[Arguments]		@{appargs}
	${var}= 	Get Variables
	Log 	${var}
	Get Platform
	${keyword}= 	Set Variable 	Open GUI ${platform}
	Run Keyword 	${keyword} 	@{appargs}

Get Platform
	&{platforms}= 	Create Dictionary 	Linux=ubuntu 	Darwin=macos 	Java=notsupported 	Windows=windows
	${os}= 	Evaluate 	platform.system() 	platform
	Set Suite Variable    ${platform}    ${platforms}[${os}]


Open GUI windows
	[Arguments]		@{appargs}
	# Set Suite Variable    ${platform}    windows
	${args}= 	Evaluate 	" \t".join(@{appargs})
	Set Confidence		0.9
	# ${process}= 	Start Process 	python3 	${pyfile}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	${process}= 	Start Process 	python 	${pyfile} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# reporter_windows_status_previewloaded
	# Wait For Status 	PreviewLoaded
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI ubuntu
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    ubuntu
	Set Confidence		0.9
	Start Process 	python3 	${pyfile} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI macos
	[Arguments]		${appargs}=${EMPTY}
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	Start Process 	python3 	${pyfile} 	-g 	5 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	# Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


Close GUI
	${keyword}= 	Set Variable 	Close GUI ${platform}
	${running}= 	Is Process Running 	${process}
	IF 	${running}
		Run Keyword 	${keyword}
	ELSE
		# ${result}= 	Get Process Result 	${process}
		${result}= 	Wait For Process 	${process} 	timeout=60
		Check Result 	${result}
	END

Check Result
	[Arguments]		${result}
	Log 	${result.stderr}
	Should Not Contain 	${result.stderr} 	Traceback
	Should Be Equal As Integers 	${result.rc} 	0

Close GUI windows
	Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	# Press Combination 	Key.f4 	Key.alt
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	End Process If Still Running

Close GUI ubuntu
	Press Combination 	Key.esc
	Press Combination 	x 	Key.ctrl
	End Process If Still Running

Close GUI macos
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		reporter_${platform}_menu_python3.png
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	End Process If Still Running

End Process If Still Running
	${result}= 	Wait For Process 	${process} 	timeout=60
	${running}= 	Is Process Running 	${process}
	IF 	not ${running}
		Check Result 	${result}
	ELSE
		Take A Screenshot
		${result} = 	Terminate Process		${process}
		Check Result 	${result}
		Fail 	Had to Terminate Process
	END
