*** Settings ***

*** Keywords ***

Run AppleScript
	[Arguments] 	${scriptstring}
	# https://stackoverflow.com/questions/2940916/how-do-i-embed-an-applescript-in-a-python-script
	# https://ss64.com/mac/osascript.html
	# subprocess.run(['osascript', '-e', cmd], capture_output=True)
	${result}= 	Evaluate 	subprocess.run(['osascript', '-e', "${scriptstring}"], capture_output=True) 	modules=subprocess
	RETURN 	${result}

Run AppleScript File
	[Arguments] 	${filepath}
	# https://stackoverflow.com/questions/2940916/how-do-i-embed-an-applescript-in-a-python-script
	# https://ss64.com/mac/osascript.html
	# subprocess.run(['osascript', '-e', cmd], capture_output=True)
	${result}= 	Evaluate 	subprocess.run(['osascript', "${filepath}"], capture_output=True) 	modules=subprocess

Copy Selection to Clipboard
	# https://www.macscripter.net/t/applescript-to-copy-selected-text-to-the-clipboard-and-passes-it-as-an-argument/74386
	# tell application "System Events" to key code 8 using command down -- copy
	# 			-- is a comment in applescript
	# ${result}= 	Run AppleScript 	tell application "System Events" to key code 8 using command down
	# maybe this way is better
	# https://www.macscripter.net/t/getting-image-and-text-on-the-clipboard/72863
	${result}= 	Run AppleScript 	tell application "System Events" to keystroke "ac" using command down
	RETURN 	${result}

Get Clipboard Text
	${result}= 	Run AppleScript 	get the clipboard as string
	RETURN 	${result.stdout}


# 