*** Settings ***
Resource          resources/folder-1/a.resource
Resource          resources/folder-2/b.resource

Metadata	File    resources/config.yaml

# Suite Teardown    Close All Browsers

*** Test Cases ***
Basic test
	Keyword A
	Keyword B
