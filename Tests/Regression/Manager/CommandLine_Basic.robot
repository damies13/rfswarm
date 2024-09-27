*** Settings ***
Test Tags       Basic 	CommandLine

Library 	OperatingSystem

Suite Setup			Clean Up Old Files

*** Variables ***
${cmd_agent} 		rfswarm-agent
${cmd_manager} 	rfswarm

*** Test Cases ***
Robot Version
	[Documentation] 	Logs the robot framework version used
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Robot_Version} =	Evaluate	robot.__version__ 	modules=robot
	Log 	${\n}Robot Version: ${Robot_Version} 	console=True

Runner CPU Cores
	[Documentation] 	Logs the Runner's CPU Cores
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${CPU Cores} =	Evaluate	psutil.cpu_count() 	modules=psutil
	Log 	${\n}CPU Cores: ${CPU Cores} 	console=True
	# ${CPU Freq} =	Evaluate	psutil.cpu_freq() 	modules=psutil
	# Log 	${\n}CPU Freq: ${CPU Freq} 	console=True

Runner Memory
	[Documentation] 	Logs the Runner's Memory
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Memory} =	Evaluate	psutil.virtual_memory() 	modules=psutil
	Log 	${\n}Memory: ${Memory} 	console=True

Runner Disks
	[Documentation] 	Logs the Runner's Disks
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${Disks} =	Evaluate	psutil.disk_partitions() 	modules=psutil
	Log 	${\n}Disks: ${Disks} 	console=True

Random Offset
	[Documentation] 	This just prevents all the test runners doing git push at the same time
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	${random} =	Evaluate	random.randint(0, 60)
	Sleep    ${random}

Manager Version
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}= 	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -v
	${result}= 	Run 	${cmd_manager} -v
	Log to console 	${\n}${result}
	Should Contain	${result}	Version
	Should Contain	${result}	Manager

Manager Help
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# ${result}=	Run 	python3 ${EXECDIR}${/}rfswarm_manager${/}rfswarm.py -h
	${result}=	Run 	${cmd_manager} -h
	Log to console 	${\n}${result}
	Should Contain	${result}	IPADDRESS

Show User Dir
	${user_dir}= 	Evaluate 	os.path.expanduser("~") 	modules=os
	Log 	user_dir: ${user_dir} 	console=True
	@{items}= 	List Directory 	${user_dir}
	Log 	items: ${items} 	console=True

*** Keywords ***
Clean Up Old Files
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# cleanup previous output
	Log To Console    ${OUTPUT DIR}
	Remove File    ${OUTPUT DIR}${/}*.txt
	Remove File    ${OUTPUT DIR}${/}*.png
	# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*
