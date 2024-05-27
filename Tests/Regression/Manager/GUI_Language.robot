*** Settings ***
Resource 	GUI_Common.robot

Suite Setup 	Set Platform

Test Teardown 	Close Manager GUI

*** Variables ***
@{languages} 		bg 	bs 	cs 	de 	en 	es 	fi 	fr 	hi 	it 	nl 	pl 	pt 	pt_br 	ro 	ru 	sv 	th 	tr 	uk 	vi 	zh_cn 	zh_tw

*** Test Cases ***
# Issue #238
Test Cases For Issue #238
	[Tags]	windows-latest	ubuntu-latest	macos-latest	Issue #238
	[Template]    Add Test In Language
	FOR    ${lang}    IN    @{languages}
		${lang}
	END


*** Keywords ***
Add Test In Language
	[Arguments] 	${langcode}
	Log 	${langcode}
	Open Manager GUI
	Click Button	runnew
	Click Button	selected_runscriptrow
	Take A Screenshot
	Press Key.escape 1 Times
	Take A Screenshot

#
