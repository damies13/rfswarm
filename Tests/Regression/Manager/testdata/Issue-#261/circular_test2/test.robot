*** Settings ***
*** Settings ***
Resource          resources/core-ui/resources/generic-resources/ui-login.resource
Resource          resources/robot-dashboard/resources/Kiwi_Resources/page_kiwi.resource
Resource          resources/robot-dashboard/resources/Kiwi_Resources/applying_drilldowns.resource

Metadata	File    resources/robot-rv/config/variables.selieea0016.yaml

# Suite Teardown    Close All Browsers

*** Test Cases ***
Basic test
	No Operation
