*** Settings ***
Library 	ImageHorizonLibrary 	reference_folder=images

# https://eficode.github.io/robotframework-imagehorizonlibrary/doc/ImageHorizonLibrary.html
# https://github.com/Eficode/robotframework-imagehorizonlibrary

*** Test Cases ***

New Test Case
	Click New

*** Keywords ***
Click New
#	Set Confidence	0.75
	Click Image		rfswarm_BG
	Take A Screenshot
#	Locate		GUI_btn_page_white.edt
#	Set Confidence	0.77
#	Locate		GUI_btn_page_white.edt
#	Set Confidence	0.79
#	Locate		GUI_btn_page_white.edt
#	Set Confidence	1
#	Locate		GUI_btn_page_white.edt
	Click Image		btn_new
	Take A Screenshot
