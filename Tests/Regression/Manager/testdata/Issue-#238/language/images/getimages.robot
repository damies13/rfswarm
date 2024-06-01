*** Settings ***
Library 				RequestsLibrary
Library 				OperatingSystem

Test Template 	Get Images For Language

*** Test Cases ***
# Issue #238
# Bulgarian		bg
# Bosnian		bs
# Czech		cs
# German		de
# English		en
# Spanish		es
# Finnish		fi
# French		fr
# Hindi		hi
# Italian		it
Dutch		nl
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
Chinese Traditional		zh_tw



*** Keywords ***
Get Images For Language
	[Arguments] 	${langcode}
	Log 	${langcode} 	console=True
	${url}= 	Get Image URL For Language 	${langcode} 	png
	${file}= 	Get Image File Path For Language 	${langcode} 	png
	Download Image To File 	${url} 	${file}

	${url}= 	Get Image URL For Language 	${langcode} 	svg
	${file}= 	Get Image File Path For Language 	${langcode} 	svg
	Download Image To File 	${url} 	${file}

Download Image To File
	[Arguments] 	${url} 	${filepath}
	${response}=    GET  ${url}
	Create Binary File     ${filepath}     ${response.content}

Get Image URL For Language
	[Arguments] 	${langcode} 	${filetype}
	${url}= 	Set Variable    https://dynamic-image.vercel.app/api/generate/${filetype}/yellowish-yellow.${filetype}
	${url}= 	Set Variable    ${url}?icon=https%3A%2F%2Fraw.githubusercontent.com%2Fdamies13%2Frfswarm%2Fmaster%2FDoc%2FImages%2FLogo%2FRFSwarm%2520svg%2Ficon%2520%255Bblue%255D.svg
	${url}= 	Set Variable    ${url}&title=lang_${langcode}
	${url}= 	Set Variable    ${url}&content=${langcode}
	${url}= 	Set Variable    ${url}&ref=website
	RETURN 	${url}

Get Image File Path For Language
	[Arguments] 	${langcode} 	${filetype}
	${fp}= 	Set Variable    ${CURDIR}/lang_${langcode}.${filetype}
	RETURN 	${fp}




#
