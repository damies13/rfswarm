# rfswarm Agent
[Return to Index](README.md)

rfswarm agent is the component that actually runs the Robot Framework test cases and returns the results to rfswarm. The agent has no GUI

- [Command-line Interface](#command-line-interface)
- [Install and Setup](#install-and-setup)
  - [Robot Framework](#1-robot-framework)
  - [Install Using pip](#2-install-using-pip)
  - [Run Agent 1st time](#3-run-agent-1st-time)
  - [Run Agent](#4-run-agent)
  - [Manually install the prerequisites](#5-manually-install-the-prerequisites)
  - [Manually Run Agent](#6-manually-run-agent)
  - [Prerequisites that some systems may require](#7-prerequisites-that-some-systems-may-require)
- [INI File Settings](configuration_files_agent.md)
- [Agent polling of the Manager](#agent-polling-of-the-manager)
  - [Disconnected State](#disconnected-state)
  - [Connected State](#connected-state)
  - [Running State](#running-state)

## Command-line Interface

These command-line options allow you to override the ini file configuration but do not update the ini file.

Additionally the debug (-g) levels 1-3 will give extra information on the console useful for troubleshooting your environment. debug levels above 5 are more for debugging the code and get very noisy so are not recommended for normal use.

```console
$ rfswarm-agent -h
Robot Framework Swarm: Run Agent
	Version 0.6.4
usage: rfswarm_agent.py [-h] [-g DEBUG] [-v] [-i INI] [-m MANAGER] [-d AGENTDIR] [-r ROBOT] [-x] [-a AGENTNAME] [-p PROPERTY]

optional arguments:
  -h, --help            show this help message and exit
  -g DEBUG, --debug DEBUG
                        Set debug level, default level is 0
  -v, --version         Display the version and exit
  -i INI, --ini INI     path to alternate ini file
  -m MANAGER, --manager MANAGER
                        The manager to connect to e.g. http://localhost:8138/
  -d AGENTDIR, --agentdir AGENTDIR
                        The directory the agent should use for files
  -r ROBOT, --robot ROBOT
                        The robot framework executable
  -x, --xmlmode         XML Mode, fall back to pasing the output.xml after each iteration
  -a AGENTNAME, --agentname AGENTNAME
                        Set agent name
  -p PROPERTY, --property PROPERTY
                        Add a custom property, if multiple properties are required use this argument for each property e.g. -p property1 -p "Property 2"

```

If you pass in an unsupported command-line option, you will get this prompt:
```console
$ rfswarm-agent -?
Robot Framework Swarm: Run Agent
Robot Framework Swarm: Run Agent
	Version 0.6.4
usage: rfswarm_agent.py [-h] [-g DEBUG] [-v] [-i INI] [-m MANAGER] [-d AGENTDIR] [-r ROBOT] [-x] [-a AGENTNAME] [-p PROPERTY]
rfswarm_agent.py: error: unrecognized arguments: -?
```

## Install and Setup

### 1. Robot Framework
Firstly ensure Robot Framework is installed with the libraries needed for your application, then try running your test case from the command-line of you agent machine e.g.
```console
robot -t "test case" script.robot
```

### 2. Install Using pip

The Agent machine needs to use a minimum of Python 3.6
> timespec feature of datetime's isoformat requires Python 3.6+

```console
pip* install rfswarm-agent
```
\*some systems might need you to use pip3 and or sudo

Next, desktop users can optionally install the desktop icon
- In the start menu for Windows
- In the Applications folder for Mac
- As a .desktop file for Linux (known to work for Gnome, KDE, Cinamon, XFCE, LXQt, should also work for other desktop environments that support standard .desktop files)

Using the command
```console
rfswarm-manager -c icon
```

### 3. Run Agent 1st time

```console
rfswarm-agent
```

when you see output like this, type CTRL+c to stop the agent:
```console
$ rfswarm-agent
Robot Framework Swarm: Run Agent
	Version 0.6.1
	Configuration File:  /home/dave/.local/lib/python3.8/site-packages/rfswarm_agent/RFSwarmAgent.ini
```

Now edit RFSwarmAgent.ini and change `http://localhost:8138/` to `http://\<your rfswarm server\>:8138/`

### 4. Run Agent

Now you agent is setup and ready to use, so run it again and wait for it to try connecting to your rfswarm server.
```console
rfswarm-agent
```

Note if your rfswarm server is already running you should see output like this and your agent should appear in the Agents tab in the GUI:
```console
$ rfswarm-agent
Robot Framework Swarm: Run Agent
	Version 0.6.1
	Configuration File:  /home/dave/.local/lib/python3.8/site-packages/rfswarm_agent/RFSwarmAgent.ini
Server Conected http://DavesMBPSG:8138/ 2020-12-16 19:34:44 ( 1608111284 )
```

![Image](Images/MacOS_Agents_ready_v0.6.3.png "Agents Ready")


### 5. Manually install the prerequisites

The Agent machine needs to use a minimum of Python 3.6
> timespec feature of datetime's isoformat requires Python 3.6+

Additionally the following pip command might be needed if these are not already installed on your system:
```console
pip* install configparser requests psutil
```
\*some systems might need you to use pip3 and or sudo


### 6. Manually Run Agent

Now you agent is setup and ready to use, so run it again and wait for it to try connecting to your rfswarm server.
```console
python rfswarm_agent.py
```

Note if your rfswarm server is already running you should see output like this and your agent should appear in the Agents tab in the GUI:
```console
Robot Framework Swarm: Run Agent
	Version 0.6.4
	Configuration File:  /path/to/RFSwarmAgent.ini
Manager Connected http://managerhostname:8138/ 2021-02-14 09:44:42 ( 1613259882 )
```

![Image](Images/MacOS_Agents_ready_v0.6.3.png "Agents Ready")


### 7. Prerequisites that some systems may require

So far I encountered this on a ARM Linux machine, but it may apply to others as well.

On some python environments not all the pre-requisite packages are compiled for your platform, so for example on ARM Linux systems psutil needs:

```console
pip* install setuptools
```

Then setuptools also required the python-dev package, so on a Debian based system I ran:

```console
apt install python3-dev
```

You may need to do something similar.


## Agent polling of the Manager

### Disconnected State
When the agent starts up, or is disconnected from the Manager it is in the disconnected state, in this state the agent will attempt to connect to the Manager every 10 seconds until connected (enter Connected State) or the agent is stopped.

### Connected State
When the agent is connected to the Manager but is not running any robots it is in the connected state, in this state the agent will poll the Manager every 10 seconds for the following:
- Update the Manager with the agent status
- Get a list of any script files that need to be downloaded locally
  - if a script file in the list has not already been download, then download the file.
- Get the assigned tests
  - if the assigned test start time has been reached for one of the assigned tests, then the agent will switch to the running state

### Running State
When the agent is in the running state, the polling interval is reduced to 2 seconds and the polling is reduced to:
- Update the Manager with the agent status
- Get the assigned tests

Once the end time for all tests has been reached and the tests have finished executing then the agent will return to the Connected State.

Note: during the Running State, script files are not checked or download, so ensure there is enough time between loading the scenario and running the scenario so the agents can download all the required files.
