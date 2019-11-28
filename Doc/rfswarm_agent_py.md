
[Index](Index.md)

## rfswarm_agent.py (Agent)

rfswarm_agent.py is the agent component that actually runs the Robot Framework test cases and returns the results to rfswarm. The agent has no GUI

- [Install and Setup](#Install-and-Setup)
	- [Robot Framework](#1-Robot-Framework)
	- [Install the prerequisites](#2-Install-the-prerequisites)
	- [Run Agent 1st time](#3-Run-Agent-1st-time)
	- [Run Agent](#4-Run-Agent)
- [INI File Settings](#INI-File-Settings)
	- [Swarm Server](#Swarm-Server)
	- [Agent Directory](#Agent-Directory)
	- [Robot Command](#Robot-Command)
	- [Exclude Libraries](#Exclude-Libraries)
- [Agent polling of the GUI/Server](#Agent-polling-of-the-GUI-Server)


### Install and Setup

#### 1. Robot Framework
Firstly ensure Robot Framework is installed with the libraries needed for your application, then try running your test case from the command line of you agent machine e.g.
```
robot -t "test case" script.robot
```

#### 2. Install the prerequisites

The Agent machine needs to use a minimum of Python 3.6
> timespec feature of datetime's isoformat requires Python 3.6+

Additionally the following pip command might be needed if these are not already installed on your system:
```
pip* install configparser requests psutil
```
\*some systems might need you to use pip3 and or sudo

#### 3. Run Agent 1st time

```
python rfswarm_agent.py
```
\*or python3 on some systems

when you see output like this, type CTRL+c to stop the agent:
```
Robot Framework Swarm: Run Agent
RFSwarmAgent: mainloop: Running 2019-11-03 00:08:10 ( 1572703690 )isrunning: False isconnected: False
RFSwarmAgent: mainloop: Running 2019-11-03 00:08:20 ( 1572703700 )isrunning: False isconnected: False
RFSwarmAgent: connectserver: Try connecting to http://localhost:8138/
RFSwarmAgent: mainloop: Running 2019-11-03 00:08:30 ( 1572703710 )isrunning: False isconnected: False
RFSwarmAgent: connectserver: Try connecting to http://localhost:8138/
RFSwarmAgent: mainloop: Running 2019-11-03 00:08:40 ( 1572703720 )isrunning: False isconnected: False
RFSwarmAgent: connectserver: Try connecting to http://localhost:8138/
```

Now edit RFSwarmAgent.ini and change http://localhost:8138/ to http://\<your rfswarm server\>:8138/

#### 4. Run Agent

Now you agent is setup and ready to use, so run it again and wait for it to try connecting to your rfswarm server.
```
python rfswarm_agent.py
```

Note if your rfswarm server is already running you should see output like this and your agent should appear in the Agents tab in the GUI:
```
Robot Framework Swarm: Run Agent
RFSwarmAgent: mainloop: Running 2019-11-03 00:17:10 ( 1572704230 )isrunning: False isconnected: False
RFSwarmAgent: connectserver: Try connecting to http://DavesMBPSG.local:8138/
RFSwarmAgent: mainloop: Running 2019-11-03 00:17:20 ( 1572704240 )isrunning: False isconnected: True
RFSwarmAgent: mainloop: Running 2019-11-03 00:17:30 ( 1572704250 )isrunning: False isconnected: True
RFSwarmAgent: mainloop: Running 2019-11-03 00:17:40 ( 1572704260 )isrunning: False isconnected: True
```

![Image](Images/Agents_ready_v0.3.png "Agents Ready")

### INI File Settings

#### [Agent]
All of the agent settings are under the Agent section

#### Swarm Server
The swarm server setting defines the GUI/Server that controls the test and that this agent receives instructions from. The default value is localhost on port 8138. As you will normally run the agent on a different machine to the GUI/Server, this is the first ini file setting you will change.
```
swarmserver = http://localhost:8138/
```

#### Agent Directory
The agent directory is the file system location where the agent will download robot files and their dependancies, this also the location the robot files are executed from.
By default a directory called rfswarmagent is created in the logged in users temp directory.
```
agentdir = <TEMP>/rfswarmagent
```

#### Robot Command
The robot command is the robot framework executable, this should normally be in your path so this setting should not require changing. However if this is not the case you may need to identify the full path to your robot executable and enter it here.
```
robotcmd = robot
```

#### Exclude Libraries
In order to keep the test results focused on the application under test and avoid reporting response times for steps from support libraries, certain libraries are excluded when the agent is processing results to return to the GUI/Server. The default setting is:
```
excludelibraries = BuiltIn,String,OperatingSystem,perftest
```
You can add and remove libraries from this list to meet the requirements of your tests.

### Agent polling of the GUI/Server

#### Disconnected State
When the agent starts up, or is disconnected from the GUI/Server it is in the disconnected state, in this state the agent will attempt to connect to the GUI/Server every 10 seconds until connected (enter Connected State) or the agent is stopped.

#### Connected State
When the agent is connected to the GUI/Server but is not running a robot files it is in the connected state, in this state the agent will poll the GUI/Server every 10 seconds for the following:
- Update the GUI/Server with the agent status
- get a list of any script files that need to be downloaded locally
	- if a script file in the list has not already been download, then download the file.
- Get the assigned tests
	- if the assigned test start time has been reached for one of the assigned tests, then the agent will switch to the running state

#### Running State
When the agent is in the running state, the polling interval is reduced to 2 seconds and the polling is reduced to:
- Update the GUI/Server with the agent status
- Get the assigned tests

Once all the end time for all test has been reached and the tests have finished executing then the agent will return to the Connected State.

Note: during the Running State, script files are not checked or download, so ensure there is enough time between loading the scenario and running the scenario so the agents can download all the required files.
