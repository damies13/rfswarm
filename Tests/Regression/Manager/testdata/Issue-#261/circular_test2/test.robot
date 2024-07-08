*** Settings ***
*** Settings ***
Resource          resources/core-ui/resources/generic-resources/ui-login.resource
Resource          resources/robot-dashboard/resources/KPIIA_Resources/page_kpiia.resource
Resource          resources/robot-dashboard/resources/KPIIA_Resources/applying_drilldowns.resource

Metadata	File    resources/robot-rv/config/variables.selieea0016.yaml

# Suite Teardown    Close All Browsers

*** Test Cases ***
Basic test
	No Operation
