*** Settings ***
Documentation 	This resource file contains keywords for Reporter command line only.

Resource 	../../Common/Common.resource

*** Variables ***
${cmd_reporter} 	rfswarm-reporter
${pyfile}			${EXECDIR}${/}rfswarm_reporter${/}rfswarm_reporter.py

*** Keywords ***
Check Icon Install
	VAR 	${projname}= 		rfswarm-reporter 		scope=TEST
	VAR 	${dispname}= 		RFSwarm Reporter 		scope=TEST
	Run Keyword 	Check Icon Install For ${platform}

Check Icon Install For Macos
	${Status}= 	Run Keyword And Return Status 	Directory Should Exist 	%{HOME}${/}Applications${/}${projname}.app
	IF 	${Status}
		${appfolder}= 		Set Variable    %{HOME}${/}Applications${/}${dispname}.app
	ELSE
		${appfolder}= 		Set Variable    ${/}Applications${/}${dispname}.app
	END
	Directory Should Exist 	${appfolder} 		.app Folder not found

	Directory Should Exist 	${appfolder}${/}Contents 		Contents Folder not found
	Directory Should Exist 	${appfolder}${/}Contents${/}MacOS 		MacOS Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources 		Resources Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset 		iconset Folder not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset${/}icon_*.png 		Icons Images not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.icns 		icns File not found

	File Should Exist 	${appfolder}${/}Contents${/}Info.plist 		plist File not found
	Show Log 	 					${appfolder}${/}Contents${/}Info.plist

	File Should Exist 	${appfolder}${/}Contents${/}PkgInfo 		PkgInfo File not found
	Show Log 	 					${appfolder}${/}Contents${/}PkgInfo

	File Should Exist 	${appfolder}${/}Contents${/}MacOS${/}${projname} 		Executable Symbolic Link File not found

Check Icon Install For Windows
	Log 	%{USERPROFILE}
	Log 	%{APPDATA}
	Directory Should Exist 	%{APPDATA} 		APPDATA Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft 		Microsoft Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows 		Windows Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu 		Start Menu Directory not found
	File Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu${/}${dispname}.lnk 		Shortcut File not found

Check Icon Install For Ubuntu
	Log 	%{HOME}
	# /home/dave/.local/share/applications/rfswarm-manager.desktop
	${Status}= 	Run Keyword And Return Status 	File Should Exist 	%{HOME}${/}.local${/}share${/}applications${/}${projname}.desktop
	IF 	${Status}
		${pathprefix}= 		Set Variable    %{HOME}${/}.local${/}share
	ELSE
		${pathprefix}= 		Set Variable    ${/}usr${/}share
	END
	File Should Exist 	${pathprefix}${/}applications${/}${projname}.desktop 		Desktop File not found

	File Should Exist 	${pathprefix}${/}icons${/}hicolor${/}128x128${/}apps${/}${projname}.png 		Icon File not found

Open Reporter
	[Arguments]		@{appargs}
	${var}= 	Get Variables
	Log 	${var}
	${process}= 	Start Process 	${cmd_reporter} 	@{appargs}    alias=Reporter 	stdout=${OUTPUT DIR}${/}stdout_reporter.txt 	stderr=${OUTPUT DIR}${/}stderr_reporter.txt
	Set Suite Variable 	$process 	${process}
	Sleep	3

Get Reporter PIP Data
	Run Process	pip	show	rfswarm-reporter		alias=data
	${pip_data}	Get Process Result	data
	Should Not Be Empty		${pip_data.stdout}		msg=Reporter must be installed with pip
	Log	${pip_data.stdout}
	RETURN		${pip_data.stdout}

Get Reporter Default Save Path
	${pip_data}=	Get Reporter PIP Data
	${pip_data_list}=	Split String	${pip_data}
	${i}=	Get Index From List	${pip_data_list}	Location:
	${location}=	Set Variable	${pip_data_list}[${i + 1}]
	RETURN	${location}${/}rfswarm_reporter${/}

Get Reporter INI Location
	${location}=	Get Reporter Default Save Path
	RETURN	${location}${/}RFSwarmReporter.ini
