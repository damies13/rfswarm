*** Settings ***
Library 	OperatingSystem
Library 	Process
# Library 	SikuliLibrary 	mode=NEW

# Suite Setup			Sikili Setup
# Suite Teardown		Sikili Teardown

# Import Library	ImageHorizonLibrary	reference_folder=images
Library	ImageHorizonLibrary	reference_folder=${CURDIR}/Images 	confidence=0.9

*** Variables ***
${IMAGE_DIR} 	${CURDIR}/../../Screenshots-doc/img

*** Test Cases ***
GUI Runs and Closes
	[Tags]	macos-latest
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py 	-g 	5    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot
	Wait For 	Title Bar
	Click Image 	Title Bar
	Take A Screenshot
	Press Combination 	q 	Key.command
	${result}= 	Wait For Process 	Manager
	Should Be Equal As Integers 	${result.rc} 	0

GUI Runs and Closes
	[Tags]	windows-latest
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot
	Wait For 	Title Bar
	Click Image 	Title Bar
	Take A Screenshot

	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	Manager
	Should Be Equal As Integers 	${result.rc} 	0


GUI Runs and Closes
	[Tags]	ubuntu-latest
	Start Process 	python3 	${EXECDIR}${/}rfswarm_manager${/}rfswarm.py    alias=Manager 	stdout=${OUTPUT DIR}${/}stdout.txt 	stderr=${OUTPUT DIR}${/}stderr.txt
	Sleep 	60
	# Capture Screen
	Set Screenshot Folder 	${OUTPUT DIR}
	Take A Screenshot
	# Wait For 	Title Bar
	# Click Image 	Title Bar
	# Take A Screenshot

	Press Combination 	x 	Key.ctrl
	${result}= 	Wait For Process 	Manager
	Should Be Equal As Integers 	${result.rc} 	0

*** Keywords ***
