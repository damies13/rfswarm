*** Settings ***
Resource 	Common.resource

Resource 	Directories_and_Files.resource

*** Keywords ***
# # # # # # #
# Pip Data: #
# # # # # # #

Get ${component_name} PIP Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${comp} 	Convert To Lower Case 	${component_name}

	Run Process 	pip  show  rfswarm-${comp} 		alias=pip-show
	${pip_data} 	Get Process Result 	pip-show
	Should Not Be Empty 	${pip_data.stdout} 		msg=${comp} must be installed with pip
	Log 	${pip_data.stdout}

	RETURN 	${pip_data.stdout}

Get ${component_name} Default Save Path
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${comp} 	Convert To Lower Case 	${component_name}

	${pip_data} 	Get ${component_name} PIP Data
	${pip_data_list} 	Split String 	${pip_data}
	${i} 	Get Index From List 	${pip_data_list} 	Location:
	VAR 	${location} 	${pip_data_list}[${i + 1}]

	RETURN 	${location}${/}rfswarm_${comp}${/}

# # # # #
# INI:  #
# # # # #

Get ${component_name} INI Location
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location} 	Get ${component_name} Default Save Path

	RETURN 	${location}${/}RFSwarm${component_name}.ini

Create ${component_name} INI File If It Does Not Exist
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location}= 	Get ${component_name} INI Location
	${comp} 	Convert To Lower Case 	${component_name}

	TRY
		File Should Exist	${location}
		File Should Not Be Empty	${location}
	EXCEPT
		Log 	INI file for ${component_name} does not exist or it's empty. Creating new one. 	console=True

		IF  '${component_name}' == 'Manager'
			${process}= 	Start Process  rfswarm-manager  -n
		ELSE IF  '${component_name}' == 'Agent'
			${process}= 	Start Process  rfswarm-agent
		ELSE IF  '${component_name}' == 'Reporter'
			${process}= 	Start Process  rfswarm-reporter  -n
		END
		Wait For File To Exist 	${location}
		Sleep 	5s
		${result}= 	Terminate Process 	${process}

		File Should Exist 	${location}
		File Should Not Be Empty 	${location}
	END

Get ${component_name} INI Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location}= 	Get ${component_name} INI Location

	${status_1}= 	Run Keyword And Return Status 	File Should Exist 			${location}
	${status_2}= 	Run Keyword And Return Status 	File Should Not Be Empty 	${location}
	&{OUTPUT} 	Create Dictionary
	IF  not ${status_1}
		Log 	The ${component_name} INI data could not be read. INI file does not exists. 	console=${True}
		RETURN 	&{OUTPUT}
	ELSE IF 	not ${status_2}
		Log 	The ${component_name} INI data could not be read. INI file is empty. 	console=${True}
		RETURN 	&{OUTPUT}
	END

	${cfg}= 	Evaluate 		configparser.ConfigParser()		modules=configparser
	Evaluate 		$cfg.read('${location}')
	${ini_content}= 	Convert To Dictionary 	${cfg}
	Log 	${ini_content}
	RETURN 	${ini_content}

Show ${component_name} INI Data
	[Documentation] 	Pass the: Manager, Reporter or Agent
	${location}= 	Get ${component_name} INI Location

	${status_1}= 	Run Keyword And Return Status 	File Should Exist 			${location}
	${status_2}= 	Run Keyword And Return Status 	File Should Not Be Empty 	${location}
	&{OUTPUT} 	Create Dictionary
	IF  not ${status_1}
		Log 	The ${component_name} INI data could not be displayed. INI file does not exists. 	console=${True}
		RETURN 	&{OUTPUT}
	ELSE IF 	not ${status_2}
		Log 	The ${component_name} INI data could not be displayed. INI file is empty. 	console=${True}
		RETURN 	&{OUTPUT}
	END

	Log 	${location} 	console=${True}

Change ${component_name} INI Option
	[Documentation] 	Pass the: Manager, Reporter or Agent
	[Arguments] 	${section}  ${option}  ${new_value}
	${location}= 	Get ${component_name} INI Location

	${status_1}= 	Run Keyword And Return Status 	File Should Exist 			${location}
	${status_2}= 	Run Keyword And Return Status 	File Should Not Be Empty 	${location}
	&{OUTPUT} 	Create Dictionary
	IF  not ${status_1}
		Log 	The ${component_name} INI data could not be edited. INI file does not exists. 	console=${True}
		RETURN 	&{OUTPUT}
	ELSE IF 	not ${status_2}
		Log 	The ${component_name} INI data could not be edited. INI file is empty. 	console=${True}
		RETURN 	&{OUTPUT}
	END

	Change INI Option 	${location}  ${section}  ${option}  ${new_value}
