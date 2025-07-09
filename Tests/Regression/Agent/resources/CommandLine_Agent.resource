*** Settings ***
Documentation 	This resource file contains keywords for Agent command line only.

Resource 	../../../Common/Common.resource

Library 	HttpCtrl.Server

# datapath: /home/runner/work/rfswarm/rfswarm/rfswarm_manager/results/PreRun
# datapath: /opt/hostedtoolcache/Python/3.9.18/x64/lib/python3.9/site-packages/rfswarm_manager/results/PreRun -- let's control the output path rather than leaving it to chance
# datapath: /opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/rfswarm_manager/PreRun

*** Keywords ***
Test Agent Connectivity
	#[Setup] 	Start Server	127.0.0.1	8138

	# wait for GET poll to /
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method} 	GET
	Should Be Equal 	${url}		/

	# wait for POST to /Jobs
	Wait For Request 		20
	Reply By	200
	${method}=	Get Request Method
	${url}= 	Get Request Url
	Should Be Equal 	${method}	POST
	#Should Be Equal 	${url}		/Jobs

	#[Teardown]	Stop Server

#
