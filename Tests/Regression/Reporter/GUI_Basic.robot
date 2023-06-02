*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	String
Library 	Collections

Library 	ImageHorizonLibrary 	reference_folder=${IMAGE_DIR}
Library 	OCRLibrary

Test Teardown 	Close GUI

*** Variables ***
${IMAGE_DIR} 	${CURDIR}${/}Images${/}file_method
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py
${process}		None
${sssleep}		0.5

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

First Run
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #147
	${testdata}= 	Set Variable    Issue-#147
	${resultdata}= 	Set Variable    20230320_185055_demo
	${basefolder}= 	Set Variable    ${CURDIR}${/}testdata${/}${testdata}
	Should Exist	${basefolder}
	Log to console 	basefolder: ${basefolder} 	console=True
	${resultfolder}= 	Set Variable    ${basefolder}${/}${resultdata}
	Should Exist	${resultfolder}
	Log 	resultfolder: ${resultfolder} 	console=True
	${epoch}=	Get Time	epoch
	Open GUI	-i 	blank_${epoch}.ini 	-d 	${resultfolder}
	# Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded 	120
	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded
	# Close GUI

New Data Table Section
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #149
	Open GUI
	Wait For Status 	PreviewLoaded
	# Click Section			toc
	# This should click Report
	Click Section			Report
	# Click Text			toc 	0 	-20
	# Click To The Below Of Image 	reporter_${platform}_button_removesection.png 	20

	Take A Screenshot

	Click Button 			AddSection

	Click To The Below Of Image 	reporter_${platform}_label_sectionname.png 	20
	Type 	Issue #149
	Click Button 			OK
	Take A Screenshot
	Click Section			Issue#149

	Select Field With Label 	Type

	Select Option 	DataTable

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	Select Field With Label 	ShowGraphColours 	60

	Select Field With Label 	DataType 	60

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	Find Text 	Filter Type:

	Find Text 	Result Name

	# data table screen didn't load try to click Generate HTML

	# Click Button 	GenerateHTML

	Sleep 	10
	Take A Screenshot


	# Close GUI


Intentional Fail
	[Tags]	ubuntu-latest		windows-latest		macos-latest
	[Documentation]		Uncomment this test if you want to trigger updating Screenshots in the git repo
	...								Ensure this is commented out before release or pull request
	Fail

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
	Sleep 	${sssleep}
	Take A Screenshot

Click Section
	[Arguments]		${sectname}
	${sectnamel}= 	Convert To Lower Case 	${sectname}
	${img}=	Set Variable		reporter_${platform}_section_${sectnamel}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	Take A Screenshot

Select Option
	[Arguments]		${optname}
	${optnamel}= 	Convert To Lower Case 	${optname}
	${img}=	Set Variable		reporter_${platform}_option_${optnamel}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
	Take A Screenshot

Select Field With Label
	[Arguments]		${label} 	${offsetx}=50 	${offsety}=0
	${labell}= 	Convert To Lower Case 	${label}
	${img}=	Set Variable		reporter_${platform}_label_${labell}.png
	Log		${CURDIR}
 	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}

	${x}= 	Evaluate 	${coordinates}[0]+${offsetx}
	${y}= 	Evaluate 	${coordinates}[1]+${offsety}
	@{coordinates}= 	Create List 	${x} 	${y}
	Move To 	${coordinates}
	Click

	Sleep 	${sssleep}
	Take A Screenshot

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
	Take A Screenshot

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



Click Button
	[Arguments]		${bttnname}
	${bttnnamel}= 	Convert To Lower Case 	${bttnname}
	${img}=	Set Variable		reporter_${platform}_button_${bttnnamel}.png
	Log		${CURDIR}
	Log		${IMAGE_DIR}
	Wait For 	${img} 	 timeout=300
	@{coordinates}= 	Locate		${img}
	Click Image		${img}
	Sleep 	${sssleep}
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
	Sleep 	${sssleep}
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
	${process}= 	Start Process 	python 	${pyfile} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
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
	${process}= 	Start Process 	python3 	${pyfile} 	-g 	6 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot

Open GUI macos
	[Arguments]		@{appargs}
	Set Suite Variable    ${platform}    macos
	Set Confidence		0.9
	${process}= 	Start Process 	python3 	${pyfile} 	-g 	5 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Set Suite Variable 	$process 	${process}
	# Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot


Close GUI
	${keyword}= 	Set Variable 	Close GUI ${platform}
	IF 	${process}
		${running}= 	Is Process Running 	${process}
		IF 	${running}
			Run Keyword 	${keyword}
		ELSE
			# ${result}= 	Get Process Result 	${process}
			${result}= 	Wait For Process 	${process} 	timeout=60
			Check Result 	${result}
		END
	END
	Set Suite Variable 	$process 	None
	Sleep 	0.5

Check Result
	[Arguments]		${result}
	Log 	${result.stderr}
	Should Not Contain 	${result.stderr} 	Traceback
	Should Be Equal As Integers 	${result.rc} 	0

Close GUI windows
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	# Press Combination 	Key.f4 	Key.alt
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI ubuntu
	# Press Combination 	Key.esc
	# Press Combination 	x 	Key.ctrl
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
	End Process If Still Running

Close GUI macos
	# Press Combination 	Key.esc
	# Press Combination 	q 	Key.command
	# Click Image		reporter_${platform}_menu_python3.png
	Click Image		reporter_${platform}_button_closewindow.png
	Take A Screenshot
	Sleep 	0.5
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
