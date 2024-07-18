*** Settings ***

Resource 						%{RF_DIRECTORY}${/}folder${/}file.resource

Metadata 		File 		%{RF_DIRECTORY}${/}anotherdir${/}imagefile.png

*** Test Cases ***
Issue #165 Environment Variable Substitution
	Keyword from RF_DIRECTORY
