*** Test Cases ***
Error Only Test
    Sleep Fail Keyword
Just Sleep For 5s
    Sleep Keyword

*** Keywords ***
Sleep Fail Keyword
    [Documentation]  Error Only
    Sleep   25
    Fail
Sleep Keyword
    [Documentation]  Sleep For 5s
    Sleep   5
