*** Settings ***
Resource 	Common.resource

Resource 	Directories_and_Files.resource

*** Keywords ***
Find Log
	[Documentation] 	Returns path to the stdout and stderr log file for current test
	[Arguments] 	${component_name}=${COMPONENT}
	${comp} 	Convert To Lower Case 	${component_name}
	${tname} 		Convert To Save Path 	${TEST NAME}

	File Should Exist 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt
	File Should Exist 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt

	RETURN 		${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt

Show Log
	[Arguments]		${filename}
	File Should Exist 	${filename} 	The log could not be displayed. Provided file does not exists.
	Log 		${\n}--VVV--${filename}--VVV-- 		console=True
	${filedata}= 	Get File 	${filename} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata} 		console=True
	Log 		--ɅɅɅ--${filename}--ɅɅɅ--${\n}${\n} 		console=True
	RETURN 		${filedata}

Read Log
	[Arguments]		${filepath}
	Log 		${filepath}
	${filedata}= 	Get File 	${filepath} 		encoding=SYSTEM 		encoding_errors=ignore
	Log 		${filedata}
	RETURN 		${filedata}

Check Logs
	[Arguments] 	${component_name}=${COMPONENT}
	${comp} 	Convert To Lower Case 	${component_name}
	${tname} 	Convert To Save Path 	${TEST NAME}

	File Should Exist 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt 	Can't find ${component_name} stdout
	File Should Exist 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt 	Can't find ${component_name} stderr

	${stdout_component}= 		Read Log 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stdout_${comp}.txt
	${stderr_component}= 		Read Log 	${OUTPUT DIR}${/}stdout${/}${tname}${/}stderr_${comp}.txt
	# Run Keyword And Warn On Failure 	Should Be Equal As Integers 	${result.rc} 	0

	Should Not Contain 	${stdout_component} 	RuntimeError
	Should Not Contain 	${stderr_component} 	RuntimeError
	Should Not Contain 	${stdout_component} 	ValueError
	Should Not Contain 	${stderr_component} 	ValueError
	Should Not Contain 	${stdout_component} 	Traceback
	Should Not Contain 	${stderr_component} 	Traceback
	Should Not Contain 	${stdout_component} 	Exception
	Should Not Contain 	${stderr_component} 	Exception
	Should Not Contain 	${stdout_component} 	OSError
	Should Not Contain 	${stderr_component} 	OSError
	Should Not Contain 	${stdout_component} 	KeyError
	Should Not Contain 	${stderr_component} 	KeyError
