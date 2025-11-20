*** Settings ***

*** Variables ***

*** Tasks ***
My Example Test Case
    [Documentation]    run a test case
	Do Somethings
	Do Some Fruity Things
	Do Something


*** Keywords ***
Do Somethings
	Do First Thing
	Do Second Thing
	Do Third Thing

Do Something
	Log 	Do Something
	Sleep 	1

Do First Thing
	Log 	Do First Thing
	Sleep 	0.3

Do Second Thing
	Log 	Do Second Thing
	Sleep 	0.3

Do Third Thing
	Log 	Do Third Thing
	Sleep 	0.3

Do Some Fruity Things
	Do Banana Thing
	Do Mango Thing
	Do Soursop Thing
	Do Guava Thing
	Do Rumbutan Thing
	Do Longan Thing

Do ${Named} Thing
	Log 	Do ${Named} Thing
	Sleep 	0.3

 #
