*** Keywords ***
Keyword from RF_DIRECTORY
	[Documentation] 	Keyword from RF_DIRECTORY
	Log 	This Keyword is from a resource file in RF_DIRECTORY
	Log 	This an environment variable: %{RF_MAGICNUM} 		console=true
	Should Be Equal As Strings 		%{RF_MAGICNUM} 		Thirteen
