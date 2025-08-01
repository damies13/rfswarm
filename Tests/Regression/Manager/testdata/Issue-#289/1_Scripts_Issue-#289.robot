*** Settings ***
Resource    1r_Issue-#289.resource

***Test Cases***
Example Test Case One One
    Log     %{OS}
    Test One

Example Test Case One Two
    Log     %{TEMP}
    Log     %{PATH}
    Test Two

***Keywords***
Test One
    [Documentation]     10 seconds One
    Sleep   10

Test Two
    [Documentation]     7 seconds Fail Two
    Sleep   7
    Fail
