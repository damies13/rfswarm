*** Settings ***
Resource    resource.robot
Library		FakerLibrary

*** Variables ***
${session} 		mysession
&{superUser} 	USERNAME=abc 	PASSWORD=xyz
${PATH_CERT} 	/cert/path

*** Tasks ***
User Journey: OPA
    [Documentation]    Logs in and stores the token for future use
    ${random_word}    FakerLibrary.Uuid 4
    Set Suite Variable   ${custom_profile}    ti_${random_word}
    Log    ${PATH_CERT}
	Set Suite Variable   ${X_AUTH_TOKEN}    ${random_word}

    Login And Get Token    ${session}    ${superUser}
