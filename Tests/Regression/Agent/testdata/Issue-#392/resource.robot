*** Settings ***
Library    RequestsLibrary
Library    Collections
Library    BuiltIn
# Library    JSONLibrary

*** Variables ***
${BASE_URL} 			http://vizzuality.testhost.lan
${LOGOUT_ENDPOINT} 		${BASE_URL}/oauth/access_token
${X_AUTH_TOKEN} 		${EMPTY}
${X_ORIGIN} 			vizzuality.testhost.lan

*** Keywords ***
Login And Get Token
    [Documentation]    Logs in and returns the token
    [Arguments]    ${session}    ${userAuthInfo}
    ${USERNAME}    Set Variable        ${userAuthInfo}[USERNAME]
    ${PASSWORD}    Set Variable        ${userAuthInfo}[PASSWORD]
    Create Session    ${session}    ${BASE_URL}    verify=${pathCert}
    ${login_payload}=    Create Dictionary    username=${userAuthInfo}[USERNAME]    password=${userAuthInfo}[PASSWORD]    origin=${X_ORIGIN}
    ${headers}=    Create Dictionary    X-Auth-Token=${X_AUTH_TOKEN}
    ${response}=    POST On Session    ${session}    ${LOGOUT_ENDPOINT}    json=${login_payload}    headers=${headers}
    Status Should Be    200    ${response}
    ${token}=    Set Variable    ${response.headers['x-auth-token']}
    Set Global Variable    ${X_AUTH_TOKEN}    ${token}
