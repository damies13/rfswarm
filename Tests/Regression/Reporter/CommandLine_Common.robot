*** Settings ***
Library 	OperatingSystem
Library 	Process
Library 	DatabaseLibrary
Library 	String
Library 	Collections

*** Keywords ***
Get Modules From Program .py File That Are Not BuildIn
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #123
	[Arguments]		${file_path}	${last_line_number_of_notbuildin}
	${manager_content}	Get File	${file_path}
	${manager_content_lines}	Split String	${manager_content}	separator=\n
	
	${j}	Set Variable	${0}
	${j_old}	Set Variable	${0}
	FOR  ${i}  IN RANGE  0  ${last_line_number_of_notbuildin}
		${j_old}	Set Variable	${j}
		${j}	Get Index From List	${manager_content_lines}	start=${j + 1}		value= 
	END
	${custom_imports_lines}	Set Variable	${manager_content_lines}[${j_old + 1}:${j}]
	Log	${custom_imports_lines}
	
	${imports}	Create List
	${length}	Get Length	${custom_imports_lines}
	FOR  ${i}  IN RANGE  0  ${length}
		@{custom_imports_elements}	Create List
		FOR  ${x}  IN  ${custom_imports_lines}[${i}]
			@{list}	Split String	${x}
			FOR  ${j}  IN  @{list}
				Append To List	${custom_imports_elements}	${j}
			END
		END

		${length2}	Get Length	${custom_imports_elements}
		FOR  ${j}  IN RANGE  0  ${length2}
			IF  '${custom_imports_elements}[${j}]' == 'import' or '${custom_imports_elements}[${j}]' == 'from'
				${module_name}	Split String	${custom_imports_elements}[${j + 1}]	separator=.
				Append To List	${imports}	${module_name}[0]
				BREAK
			END
		END
	END
	
	RETURN	${imports}

Get Install Requires From Setup File
	[Arguments]		${file_path}
	${setup_content}	Get File	${file_path}
	${setup_content_lines}	Split String	${setup_content}	separator=\n
	FOR  ${line}  IN  @{setup_content_lines}
		# There is probably better solution for this:
		${setup_content_elements}	Split String	${line}	separator=s=
		TRY
			IF  '${setup_content_elements}[0]' == '\tinstall_require'
				${install_requires}	Set Variable	${setup_content_elements}[1][2:-3]
				${install_requires}	Split String	${install_requires}	separator=', '

				${refactored_requires}	Create List
				FOR  ${items}  IN  @{install_requires}
					@{sliced_times}		Create List
					@{sliced_times1}	Split String	${items}	separator=>=
					Append To List	${sliced_times}		@{sliced_times1}
					@{sliced_times2}	Split String	${items}	separator=-
					Append To List	${sliced_times}		@{sliced_times2}
					
					FOR  ${i}  IN   @{sliced_times}
						Append To List	${refactored_requires}	${i}

					END
				END

				BREAK
			END
		EXCEPT
			No Operation
		END
	END

	RETURN	${refactored_requires}