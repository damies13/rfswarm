# Configuration files for Agent
[Return to Index](README.md)

## INI File
The INI file is the default configuration file format for the Agent and is created when the Agent is launched for the first time or when the Agent cannot find it in the default directory.

**Default RFSwarmAgent.ini file:**
```ini
[Agent]
agentname = <HOSTNAME>
agentdir = <TEMP>/rfswarmagent
xmlmode = False
excludelibraries = BuiltIn,String,OperatingSystem,perftest
properties = 
swarmmanager = http://localhost:8138/
```

### [Agent]
All of the agent settings are under the Agent section heading

#### Swarm Manager
The swarm manager setting defines the Manager that controls the test and that this agent receives instructions from. The default value is localhost on port 8138. As you will normally run the agent on a different machine to the Manager, this is the first ini file setting you will probably change. For example, you can specify the url of a manager that is on a different network on a different port.
```ini
swarmmanager = http://localhost:8138/
```

#### Agent Directory
The agent directory is the file system location where the agent will download robot files and their dependencies, this also the location the robot files are executed from.
By default a directory called rfswarmagent is created in the logged in users temp directory.
```ini
agentdir = <TEMP>/rfswarmagent
```

#### Robot Command
The robot command is the robot framework executable, this should normally be in your path so this setting should not require changing. However if this is not the case you may need to identify the full path to your robot executable and enter it here.
```ini
robotcmd = robot
```

#### Exclude Libraries
In order to keep the test results focused on the application under test and avoid reporting response times for steps from support libraries, certain libraries are excluded when the agent is processing results to return to the Manager. The default setting is:
```ini
excludelibraries = BuiltIn,String,OperatingSystem,perftest
```
You can add and remove libraries from this list to meet the requirements of your tests.
