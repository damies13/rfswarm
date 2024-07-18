*** Settings ***

Resource 	%{RF_DIRECTORY}${/}folder${/}file.resource

*** Test Cases ***
Issue #165 Environment Variable Substitution
	Keyword from RF_DIRECTORY
