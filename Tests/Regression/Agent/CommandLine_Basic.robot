*** Settings ***
Library 	OperatingSystem

*** Test Cases ***
Robot Version
	[Documentation] 	Logs the robot framework version used
	[Tags] 	ubuntu-latest 	macos-latest 	windows-latest
	${Robot_Version}= 	Get Robot Framework version
	Log 	Robot Version: ${Robot_Version} 	console=True

Agent Version
	[Documentation] 	Logs the Agent version to console
	[Tags] 	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Get Agent Version
	Log 	${\n}${result} 	console=True

	Should Contain	${result}	Version
	Should Contain	${result}	Agent

Agent Help
	[Documentation] 	Logs the Agent Help to console
	[Tags] 	ubuntu-latest 	macos-latest 	windows-latest
	${result}= 	Get Agent help
	Log 	${\n}${result} 	console=True

	Should Contain	${result}	AGENTNAME

*** Keywords ***
Get Robot Framework version
	${Robot_Version} =	Evaluate	robot.__version__ 	modules=robot
	RETURN 	${Robot_Version}

Get Agent Version
	${agent_version}= 	Run 	rfswarm-agent -v
	RETURN 	${agent_version}

Get Agent Help
	${agent_help}= 	Run 	rfswarm-agent -h
	RETURN 	${agent_help}
