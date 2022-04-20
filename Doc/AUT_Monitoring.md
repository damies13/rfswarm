[Index](README.md)

## AUT Monitoring

The ability to monitor your Application Under Test (AUT) servers and store the monitoring data in the test results has been available as part of the rfswarm Manager since version v0.6.3 and was introduced from feature request #72.

With feature release v0.8.0 this became more useful as you could use the live graphs to monitor this data during a test, and now with release 1.0.0 you can easily include this information in your test reports.

- [Overview](#Overview)
- [Recomendations](#Recomendations)
- [Unix AUT Example](#unix-linux-aut-example)
- [Windows AUT Example](#Windows-AUT-Example)

### Overview

While it may not be obvious at first the process for monitoring and reporting the performance data of your AUT is quite simple and quite flexible.

1. Create a robot framework test case that connects to your AUT server and gathers the performance data you are interested in collecting, as a minimum you will probably want to collect CPU, Memory and Disk IO Information, you may also want to collect network IO, and then depending on the type of server you are monitoring there may be other details you want to monitor.
1. report the details back to the manager using the rfswarm API [POST /Metric](Agent_Communication.md#post-metric)
1. to make this easier the variable `${RFS_SWARMMANAGER}` as documented in the [Swarm Manager](Preparing_for_perf.md#swarm-manager) section of [Useful Variables](Preparing_for_perf.md#useful-variables), can be used to avoid hard coding the manager details.

### Recomendations

- Set up an agent machine in your data center(s) in the same network as your AUT servers to be dedicated to the task of monitoring servers. Configure the agent with a custom property that identifys the agent e.g. "Monitor" or the <datacentre name>. when configuring your test scenario configure the [additional settings > agent filter](https://github.com/damies13/rfswarm/blob/master/Doc/rfswarm_manager.md#agent-filter) for the monitoring robots to require this property and configure the other robots to exclude this property.

### Unix (Linux) AUT Example

The robot file below is an example of connecting to a unix (linux) AUT server via a SSH session using the robot framework SSH library, collecting a variety of statistics from the AUT server and then posting those details to the Manager API using the robot framework Requests Library.

This example may work for you, or you may need to modify it to work with the OS that your AUT uses. It is not intended as a ready to use example, but rather a starting point to help you build a monitoring script for your AUT.

ssh_example.robot
```robotframework
*** Settings ***

Library                SSHLibrary
Suite Teardown         Close All Connections

Library					String
Library					Collections
Library					RequestsLibrary
Library					json

*** Variables ***
${HOST}                Undefined
${USERNAME}            Undefined
${PASSWORD}            Undefined

*** Test Cases ***
Monitor Linux AUT
	${HOST}=		Set Variable    AUT_Server
	${USERNAME}=	Set Variable    AUT_System_User
	${PASSWORD}=	Set Variable    AUT_System_Pass

	# Connect SSH Session to AUT server
	Open Connection And Log In	${HOST}	${USERNAME}	${PASSWORD}

	# Gather the AUT Server statistics every 5 seconds
	# 3600 / 5 = 720 - poll every 5 seconds for 1 hour
	FOR 	${i}	IN RANGE	720
		${epoch}=		Get Time	epoch
		${stats}=	Collect Stats
		Post AUT Stats		${HOST} 	AUT Web 	${epoch}    ${stats}
		Sleep	4
	END

	# at the end of the hour the test will end and disconnect the SSH session (Suite Teardown) if your test scenario is
	# configured to run for more than an hour the agent will automatically restart the test.

*** Keywords ***


Open Connection And Log In
	[Arguments] 	${HOST}=${HOST} 	${USERNAME}=${USERNAME} 	${PASSWORD}=${PASSWORD}
	# keywords from SHH Library
	Open Connection     ${HOST}		width=160
	Login               ${USERNAME}        ${PASSWORD}


Collect Stats
	${lscpu}=	lscpu
	${vmstat}=	vmstat

	${stats}=	Create Dictionary
	FOR 	${k}	IN		@{lscpu.keys()}
		log 	${k}
		Set To Dictionary	${stats} 	lscpu: ${k}		${lscpu["${k}"]}
	END
	FOR 	${k}	IN		@{vmstat.keys()}
		log 	${k}
		log 	${vmstat["${k}"]}
		Set To Dictionary	${stats} 	vmstat: ${k}		${vmstat["${k}"]}
	END
	[Return]	${stats}



lscpu
	Write              lscpu
	${output}=         Read Until       $
	# @{lines}=	Split To Lines	${output}
	@{lines}=	Set Variable	${output.splitlines()}

	${dict}=	Create Dictionary
	FOR 	${line} 	IN		@{lines}
		${key}	${val}=		Set Variable	${line.split(":")}
		Set To Dictionary	${dict} 	${key.strip()}		${val.strip()}
	END

	[Return] 	${dict}



vmstat
	${output}=		Execute Command		vmstat -w 1 2
	@{lines} =	Split To Lines	${output}
	log 	${lines[-1]}
	${line}=		Set Variable	${lines[-1]}
	@{vals} =	Split String	${line}
	log 	${vals}

	${vmstat}=	Create Dictionary
	# Proc
	#
	# r: The number of runnable processes. These are processes that have been launched and are either running or are waiting for their next time-sliced burst of CPU cycles.
	# b: The number of processes in uninterruptible sleep. The process isn’t sleeping, it is performing a blocking system call, and it cannot be interrupted until it has completed its current action. Typically the process is a device driver waiting for some resource to come free. Any queued interrupts for that process are handled when the process resumes its usual activity.
	Set To Dictionary	${vmstat} 	Processes: Runnable 		${vals[0]}
	Set To Dictionary	${vmstat} 	Processes: Uninterruptible	${vals[1]}


	# Memory
	#
	# swpd: the amount of virtual memory used. In other words, how much memory has been swapped out.,
	# free: the amount of idle (currently unused) memory.
	# buff: the amount of memory used as buffers.
	# cache: the amount of memory used as cache.
	Set To Dictionary	${vmstat} 	Memory: Swap 	${vals[2]}
	Set To Dictionary	${vmstat} 	Memory: Free 	${vals[3]}
	Set To Dictionary	${vmstat} 	Memory: Buffers	${vals[4]}
	Set To Dictionary	${vmstat} 	Memory: Cache 	${vals[5]}


	# Swap
	#
	# si: Amount of virtual memory swapped in from swap space.
	# so: Amount of virtual memory swapped out to swap space.
	Set To Dictionary	${vmstat} 	Swap: Swapped In 	${vals[6]}
	Set To Dictionary	${vmstat} 	Swap: Swapped Out	${vals[7]}


	# IO
	#
	# bi: Blocks received from a block device. The number of data blocks used to swap virtual memory back into RAM.
	# bo: Blocks sent to a block device. The number of data blocks used to swap virtual memory out of RAM and into swap space.
	Set To Dictionary	${vmstat} 	IO: Blocks received	${vals[8]}
	Set To Dictionary	${vmstat} 	IO: Blocks sent 	${vals[9]}


	# System
	#
	# in: The number of interrupts per second, including the clock.
	# cs: The number of context switches per second. A context switch is when the kernel swaps from system mode processing into user mode processing.
	Set To Dictionary	${vmstat} 	System: Interrupts/s		${vals[10]}
	Set To Dictionary	${vmstat} 	System: Context Switches/s	${vals[11]}


	# CPU
	#
	# These values are all percentages of the total CPU time.
	#
	# us: Time spent running non-kernel code. That is, how much time is spent in user time processing and in nice time processing.
	# sy: Time spent running kernel code.
	# id: Time spent idle.
	# wa: Time spent waiting for input or output.
	# st: Time stolen from a virtual machine. This is the time a virtual machine has to wait for the hypervisor to finish servicing other virtual machines before it can come back and attend to this virtual machine.
	Set To Dictionary	${vmstat} 	CPU: User	${vals[12]}
	Set To Dictionary	${vmstat} 	CPU: System	${vals[13]}
	Set To Dictionary	${vmstat} 	CPU: Idle	${vals[14]}
	Set To Dictionary	${vmstat} 	CPU: Wait	${vals[15]}
	Set To Dictionary	${vmstat} 	CPU: Stolen	${vals[16]}


	#
	[Return] 	${vmstat}




Post AUT Stats
	[Documentation]		SSH: Post AUT Stats
	[Arguments]		${AUT}	${AUTType}	${AUTTime}    ${Stats}

	# keyword from Requests Library, reuse the session rather than creating a new one if possible
	${exists}= 	Session Exists	rfs
	Run Keyword Unless 	${exists} 	Create Session	rfs 	${RFS_SWARMMANAGER}

	${data}=	Create Dictionary
	Set To Dictionary	${data} 	PrimaryMetric		${AUT}
	Set To Dictionary	${data} 	MetricType			${AUTType}
	Set To Dictionary	${data} 	MetricTime			${AUTTime}
	Set To Dictionary	${data} 	SecondaryMetrics	${Stats}

	# keyword from json Library
	${string_json}= 	json.Dumps	${data}

	# keyword from Requests Library
	${resp}=	Post Request	rfs 	/Metric 	${string_json}
	Log	${resp}
	Log	${resp.content}
	Should Be Equal As Strings	${resp.status_code}	200


```

### Windows AUT Example

The robot file below is an example of connecting to a Windows AUT server via WMI to collect a variety of statistics using Windows Peformance Monitor Counters (Perfmon) from the AUT server and then posting those details to the Manager API using the robot framework Requests Library.

This example may work for you, or you may need to adjust it to work with the locale that your AUT uses. It is not intended as a ready to use example, but rather a starting point to help you build a monitoring script for your AUT.

perfmon_example.robot
```robotframework
*** Settings ***
Library                PerfmonLibrary

Library					String
Library					Collections
Library					RequestsLibrary
Library					json

*** Variables ***
${HOST}                Undefined
${USERNAME}            Undefined
${PASSWORD}            Undefined

*** Test Cases ***
Monitor Windows AUT
	${HOST}=	Set Variable    windowsserver
	${USERNAME}=	Set Variable    domain\\windowsuser
	${PASSWORD}=	Set Variable    domainpassword

	# Connect to Windows AUT server
	# ***	This is only required if you need a different username/password to connect to your AUT server than the current user logged in	***
	Open Connection And Log In 	${HOST} 	${USERNAME} 	${PASSWORD}

	# Gather the AUT Server statistics every 5 seconds
	# 3600 / 5 = 720 - poll every 5 seconds for 1 hour
	FOR 	${i}	IN RANGE	720
		${epoch}=		Get Time	epoch
		${stats}=	Collect Stats 	${HOST}
		Post AUT Stats		${HOST} 	AUT Web 	${epoch}    ${stats}
		Sleep	4
	END

	# at the end of the hour the test will end and disconnect the SSH session (Suite Teardown) if your test scenario is
	# configured to run for more than an hour the agent will automatically restart the test.


*** Keywords ***

Open Connection And Log In
	[Arguments] 	${HOST}=${HOST} 	${USERNAME}=${USERNAME} 	${PASSWORD}=${PASSWORD}
	# keywords from PerfmonLibrary
	Connect To 	${HOST} 	${USERNAME} 	${PASSWORD}


Collect Stats
	[Arguments] 	${HOST}=${HOST}
	
	${stats}=	Create Dictionary
	
	${key} 	${Value}= 	Get Counter 	Memory\\% Committed Bytes In Use 	${HOST}
	Set To Dictionary	${stats} 	${key}		${Value}
	
	${key} 	${Value}= 	Get Counter 	Processor\\_Total\\% Processor Time 	${HOST}
	Set To Dictionary	${stats} 	${key}		${Value}
	
	${key} 	${Value}= 	Get Counter 	System\\Processor Queue Length 	${HOST}
	Set To Dictionary	${stats} 	${key}		${Value}

	[Return]	${stats}



Post AUT Stats
	[Documentation]		SSH: Post AUT Stats
	[Arguments]		${AUT}	${AUTType}	${AUTTime}    ${Stats}

	# keyword from Requests Library, reuse the session rather than creating a new one if possible
	${exists}= 	Session Exists	rfs
	Run Keyword Unless 	${exists} 	Create Session	rfs 	${RFS_SWARMMANAGER}

	${data}=	Create Dictionary
	Set To Dictionary	${data} 	PrimaryMetric		${AUT}
	Set To Dictionary	${data} 	MetricType			${AUTType}
	Set To Dictionary	${data} 	MetricTime			${AUTTime}
	Set To Dictionary	${data} 	SecondaryMetrics	${Stats}

	# keyword from json Library
	${string_json}= 	json.Dumps	${data}

	# keyword from Requests Library
	${resp}=	Post Request	rfs 	/Metric 	${string_json}
	Log	${resp}
	Log	${resp.content}
	Should Be Equal As Strings	${resp.status_code}	200


```
