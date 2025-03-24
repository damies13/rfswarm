*** Test Cases ***
TPS Test
    Sleep Keyword

*** Keywords ***
Sleep Keyword
    [Documentation]  Measuring TPS with this keyword [Variable sleep]
    ${value}=   Evaluate    ((${RFS_ITERATION} % 5) + 5.1) / 10
    # ${value}=   Evaluate    ${RFS_ITERATION} / 2
    Sleep   ${value}
