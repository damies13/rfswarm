*** Test Cases ***
Just Sleep For 20s And Fail
    Sleep Fail Keyword
Just Sleep For 20s
    Sleep Keyword

*** Keywords ***
Sleep Fail Keyword
    [Documentation]  Sleep For 20s and Fail
    Sleep   20
    Fail
Sleep Keyword
    [Documentation]  Sleep For 20s
    Sleep   20
