*** Settings ***

*** Variables ***
${STT_MIN}			15
${STT_MAX}			45

*** Keywords ***
Standard Think Time
	${number}    Evaluate    random.randint(${STT_MIN}, ${STT_MAX})    random
	Sleep    ${number}
