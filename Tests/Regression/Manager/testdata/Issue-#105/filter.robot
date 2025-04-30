*** Test Cases ***
Filter Test Case 1
    Filter Keyword 11
    Filter Keyword 12
    Filter Fail Keyword 1

Filter Test Case 2
    Filter Keyword 21
    Filter Keyword 22
    Filter Fail Keyword 2

*** Keywords ***
Filter Keyword 11
    [Documentation]  Filter Keyword 11
    Sleep   3

Filter Keyword 12
    [Documentation]  Filter Keyword 12
    Sleep   6

Filter Keyword 21
    [Documentation]  Filter Keyword 21
    Sleep   4

Filter Keyword 22
    [Documentation]  Filter Keyword 22
    Sleep   8

Filter Fail Keyword 1
    [Documentation]  Filter Fail Keyword 1
    Sleep   5
    Fail

Filter Fail Keyword 2
    [Documentation]  Filter Fail Keyword 2
    Sleep   10
    Fail
