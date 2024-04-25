*** Settings ***
Library 	OperatingSystem
Library 	Process


*** Keywords ***
Clean Up Old Files
		[Tags]	ubuntu-latest 	macos-latest 	windows-latest
		# cleanup previous output
		Log To Console    ${OUTPUT DIR}
		Remove File    ${OUTPUT DIR}${/}*.txt
		Remove File    ${OUTPUT DIR}${/}*.png
		# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*
