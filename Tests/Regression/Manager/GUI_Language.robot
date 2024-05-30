*** Settings ***
Resource 	GUI_Common.robot

Suite Setup 	Set Platform
Test Teardown 	Run Keyword		Close Manager GUI ${platform}
Test Tags 	windows-latest	ubuntu-latest	macos-latest	Issue #238
Test Template 	Add Test In Language

*** Test Cases ***
# Issue #238
Bulgarian		bg
Bosnian		bs
Czech		cs
German		de
English		en
# Spanish		es
# Finnish		fi
# French		fr
# Hindi		hi
# Italian		it
# Dutch		nl
# Polish		pl
# Portuguese		pt
# Brazilian Portuguese		pt_br
# Romanian		ro
# Russian		ru
# Swedish		sv
# Thai		th
# Turkish		tr
# Ukrainian		uk
# Vietnamese		vi
# Chinese Simplified		zh_cn
# Chinese Traditional		zh_tw



*** Keywords ***
Add Test In Language
	[Arguments] 	${langcode}
	Log 	${langcode} 	console=True
	Open Manager GUI
	Click Button	runnew
	Click Button	runscriptrow
	Take A Screenshot
	Press Key.escape 1 Times
	Take A Screenshot

#
