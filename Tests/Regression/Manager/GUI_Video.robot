*** Settings ***

*** Variables ***
${GUIVID} 		${None}

*** Keywords ***
Video Start Recording
	[Arguments] 	${filepath} 	${fps}=25
	IF 	not ${GUIVID}
		${recorder}= 	Evaluate 	pyscreenrec.ScreenRecorder() 	modules=pyscreenrec
		VAR 	${GUIVID} 	${recorder} 	scope=SUITE
	END
	${GUIVID}.start_recording(${filepath}, ${fps})

Video Stop Recording
	${GUIVID}.stop_recording()

Video Pause Recording
	${GUIVID}.pause_recording()

Video Resume Recording
	${GUIVID}.resume_recording()
