*** Settings ***
Resource 	GUI_Common.robot
Suite Setup 	Set Platform

*** Test Cases ***
First Run
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #147
	Log To Console 	${\n}TAGS: ${TEST TAGS}
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
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest 	Issue #149 	Issue #150
	Log To Console 	${\n}TAGS: ${TEST TAGS}
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

	Select Field With Label 	ShowGraphColours

	Select Field With Label 	DataType

	Select Option 	Result

	Select Field With Label 	ResultType

	Select Option 	ResponseTime

	Run Keyword And Continue On Failure 	Wait For Status 	PreviewLoaded

	# click Generate HTML as partial regression test for Issue #150
	Click Button 	GenerateHTML

	# Wait For Status 	GeneratingXHTMLReport

	Wait For Status 	SavedXHTMLReport

	# Close GUI
