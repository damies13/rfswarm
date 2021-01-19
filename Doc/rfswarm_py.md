
[Index](README.md)

## rfswarm.py (GUI / Server)

rfswarm.py is the GUI and central server component of rfswarm, this is where you plan, execute and monitor your performance test.

- [User Interface](#User-Interface)
	- [Plan](#Plan)
	- [Run](#Run)
	- [Agents](#Agents)
- [Command Line Interface](#Command-Line-Interface)
- [Install and Setup](#Install-and-Setup)
	- [Install](#1-install)
	- [Adjust the Firewall](#2-Adjust-the-Firewall)
	- [Run the GUI Server](#3-Run-the-GUI-Server)
	- [Manual Install the prerequisites](#4-Manual-Install-the-prerequisites)
	- [Manual Run the GUI Server](#5-Manual-Run-the-GUI-Server)
- [Agent Assignment](#Agent-Assignment)
- [Credits](#Credits)

### User Interface
#### Plan
This is where you construct your test scenario, choose your test cases and number of virtual users. The interface should be intuitive and simple to understand but still allow fairly complex scenarios to be created.

All the time fields (Delay, Ramp Up & Run) are in Seconds, due to the way the [agent polling](./rfswarm_agent_py.md#agent-polling-of-the-guiserver) works it's best not to use values less than 10 seconds.

> _Plan - Planning a performance test_
![Image](Images/MacOS_Plan_saved_opened_v0.6.3.png "Plan - Planning a performance test")

> _Plan - New_
![Image](Images/MacOS_Plan_New_v0.6.3.png "Plan - New")

> _Plan - Delay example_
![Image](Images/MacOS_Plan_v0.6.3_20u_delay_example.png)

> _Plan - gradual ramp-up example_
![Image](Images/MacOS_Plan_v0.6.3_150u_25per10min.png)

> _Plan - Linux (Mint 19.2)_
> ![Image](Images/Linux-v0.5.0_Plan_150u_25per10min.png)

While hopefully this is intuitive, the buttons are (starting top right)

|	|	|	|
|---|---|---|
| New	|	![image](Images/GUI_btn_page_white.edt.gif)		| Create a new scenario	|
| Open	|	![image](Images/GUI_btn_folder_explore.gif)	| Open an existing scenario	|
| Save	|	![image](Images/GUI_btn_disk.gif)			| Save the current scenario	|
| Play	|	![image](Images/GUI_btn_resultset_next.gif)	| Play the current scenario	|
| Add	|	![image](Images/GUI_btn_add.gif)			| Add another test group	|
| Select |	![image](Images/GUI_btn_script.gif)			| Select a robot file	|
| Settings | ![image](Images/GUI_btn_cog.gif)			| Configure additional settings for a test group	|
| Remove |	![image](Images/GUI_btn_cross.gif)			| Remove this test group	|

##### Additional settings for test group ![image](Images/GUI_btn_cog.gif)
When clicking on this button a dialogue will be presented that allows you to configure some additional settings for the test group, by default the dialogue will look like this:
> ![image](Images/MacOS_Plan_v0.6.3_Test_Settings.png)

###### Exclude libraries:
The default value is "BuiltIn,String,OperatingSystem,perftest", this is the same default value as used in the [agent settings](./rfswarm_agent_py.md#exclude-libraries) and if you leave this default but change the agent the settings set on the agent will override this setting.
By configuring this setting you can adjust which keyword's response times are reported in the test results.
If you change this setting here from the default, then for this particular test group the agent setting will be overridden with the settings used here

|agent ini setting|test group setting|result|
|---|---|---|
|default|default|default (BuiltIn,String,OperatingSystem,perftest)|
|configured|default|agent ini setting|
|default|configured|test group setting|
|configured|configured|test group setting|

###### Robot Options:
By default this setting is blank and in most cases wouldnlt be used, it allows you to pass additional command line options to the robot executable, to find out what options can be passed run
`robot -h`
On any machine that has Robot Framework installed

###### Agent Filter:
You can use this setting to modify the default [agent assignment](#agent-assignment) to require test cases to require agents with particular properties or to exclude agents with particular properties.

By default there are no Agent filters applied, and the test group can be run on any available agent.

Here are some examples of when you might need this setting:
- Your AUT has a desktop client and a web ui, the tests executed in the desktop client need an agent with Windows os and the web ui scripts can run on any agent that has SeleniumLibrary available
	- on the desktop client scripts you add a filter rule that Requires "OS: System: windows"
	- on the web ui scripts you add a filter rule that Requires "RobotFramework: Library: seleniumlibrary"
- Your AUT has an internal component that can only be accessed by users in your corporate network and an external component that can only be accessed by internet users
	- in your agents ini file you configure a custom property of "Corp Network" or "Internet" depending on which network the agent sits in.
	- on the internal component scripts you add a filter rule that Requires "Corp Network"
	- on the external component scripts you add a filter rule that Requires "Internet" alternatively you could configure a rule that Excludes "Corp Network"

The combination of multiple require and exclude rules, the default and custom agent properties should allow you to have the control needed to target your test groups to specific agent or groups of agents as needed.

Here is an example of configuring the Filter Rules and using the Robot options:
> ![image](Images/MacOS_Plan_v0.6.3_Test_Settings_Filter_Rules.png)


#### Run
This is where you monitor your test scenario as it runs, here you will see number of robots running, how long the has been running and live updates of the test results.

Unique by check boxes:
- Index, use this if multiple test cases have results with the same result name but you want to keep the result timings separated based on the individual test cases.
- Iteration, use this if you want to keep the result timings separated based on the test iteration.
- Sequence, use this if multiple test steps in the same test case have the same result name but you want to keep the result timings separated based on the sequence within the test case.

%ile (Percentile) field:
The default value is 90, you can adjust the percentile value between 1% and 99% depending on your application's performance requirements.

##### Stop button ![image](Images/GUI_btn_stop.gif)
Use this if you want to stop the test early. You may not notice an immediate reaction as pressing the button just changes the end time on all the test jobs assigned to the current time and stops the ramp-up if the test is still in the ramp-up phase. While there is no benefit to pressing the stop button multiple times there is no harm either, so press to your hearts content.

Once the stop button has been pressed the agents will receive the changed end time when they [poll](./rfswarm_agent_py.md#agent-polling-of-the-guiserver) the GUI/Server next, the agent will change status to stopping which will be returned on the next poll interval and the agent will not start a new iteration for the running tests, however the ones currently running will be allowed to complete.

##### Abort button ![image](Images/GUI_btn_bomb.gif)
This button replaces the Stop button when either of the following happens:
- You press the Stop button
- The test reaches the rampdown period after run is complete

Clicking the Abort button will present a warning dialogue like this:
![image](Images/MacOS_Run_v0.6.3_Abort_Run_Dialogue.png)
Clicking yes on this dialogue will instruct the agents to send a sigterm (^C) to the running robots causing them to abort the currently running test and execute any teardown steps and exit.
You would normally only use this option if your AUT has crashed and you need to stop applying load to the system.

##### Disabled Stop button ![image](Images/GUI_btn_stop_grey.gif)
This button replaces the Stop/Abort buttons when either of the following happens
- You clicked yes to abort the run
- The test completes rampdown
Clicking this button does nothing.

##### CSV Report button ![image](Images/GUI_btn_report.gif)
Use this to generate csv files suitable for use to create reports for your test run, there will be three files generated:
- A Summary file, this is the same data as on the run screen
- A Raw Results file, the is every data point recorded, useful if you want create response time graphs
- An Agents file, this is all the agent stats recorded, useful if you want to graph running robots or agent loads

> _Run - Just started_
![Image](Images/MacOS_Run_Start_v0.6.3_09s.png "Run - Just Started")

> _Run - Just started, first results coming in_
![Image](Images/MacOS_Run_Start_v0.6.3_54s.png "Run - Just started, first results coming in")

> _Run - Showing results being collected live_
![Image](Images/MacOS_Run_v0.6.3_100u_2h.png "Run - Showing results being collected live")

> _Run - Linux_
> ![Image](Images/Linux-v0.5.0_Run_6min.png)

> _Run - Linux Report Saved_
![Image](Images/Linux-v0.5.0_Run_Report_prompt.png)


#### Agents
This is where you can see which agents have connected, number of robots on each agent and monitor the status and performance of the agents.
> _Agents - Ready_
![Image](Images/MacOS_Agents_ready_v0.6.3.png "Agents - Ready")

> _Agents - Running / Warning_
![Image](Images/MacOS_Agents_running_warning_v0.6.3.png "Agents - Running / Warning")

> _Agents - Stopping_
![Image](Images/MacOS_Agents_stopping_v0.6.3.png "Agents - Stopping")

> _Agents - Running (Linux)_
> ![Image](Images/Linux-v0.5.0_Agents_Running.png)

New with v0.6.3 this screen now shows the agent's version and a list of robot framework libraries available on the agent.

### Command Line Interface

These command line options allow you to override the ini file configuration but do not update the ini file.

Additionally the debug (-g) levels 1-3 will give extra information on the console useful for troubleshooting your environment. debug levels above 5 are more for debugging the code and get very noisy so are not recommended for normal use.

```
$ rfswarm -h
Robot Framework Swarm: GUI/Server
	Version 0.6.3
usage: rfswarm [-h] [-g DEBUG] [-v] [-i INI] [-s SCENARIO] [-r] [-a AGENTS] [-n] [-d DIR] [-e IPADDRESS] [-p PORT]

optional arguments:
  -h, --help            show this help message and exit
  -g DEBUG, --debug DEBUG
                        Set debug level, default level is 0
  -v, --version         Display the version and exit
  -i INI, --ini INI     path to alternate ini file
  -s SCENARIO, --scenario SCENARIO
                        Load this scenario file
  -r, --run             Run the scenario automatically after loading
  -a AGENTS, --agents AGENTS
                        Wait for this many agents before starting (default 1)
  -n, --nogui           Don't display the GUI
  -d DIR, --dir DIR     Results directory
  -e IPADDRESS, --ipaddress IPADDRESS
                        IP Address to bind the server to
  -p PORT, --port PORT  Port number to bind the server to
```

If you pass in an unsupported command line option, you will get this prompt:
```
$ rfswarm -?
Robot Framework Swarm: GUI/Server
	Version 0.6.3
usage: rfswarm [-h] [-g DEBUG] [-v] [-i INI] [-s SCENARIO] [-r] [-a AGENTS] [-n] [-d DIR] [-e IPADDRESS] [-p PORT]
rfswarm: error: unrecognized arguments: -?
```

### Install and Setup

#### 1. Install
##### 1.1 Prerequisites
- The GUI/Server machine needs to use a minimum of Python 3.7
> ThreadingHTTPServer feature of HTTPServer requires was added in Python 3.7

- tkinter may need to be installed
It may already installed on your system, if not consult the [python documentation](https://tkdocs.com/tutorial/install.html) on how to install for your system.

On Debian based systems this will probably work
```
apt install python3-tk
```

##### 1.2 Install

Once you have the prerequisites sorted, the installation is simply
```
pip* install rfswarm-gui
```

\*some systems might need you to use pip3 and or sudo

#### 2. Adjust the Firewall

Check if there is a firewall on you GUI / Server machine, if so you may need to adjust the firewall to add a rule to allow communication between the GUI / Server and the Agent.

| Machine | Protocol | Port Number<sup>1</sup> | Direction |
|---|---|---|---|
| GUI / Server | TCP | 8138 | Inbound |
| Agent | TCP | 8138 | Outbound |

<sup>1</sup> This is the default port number, replace with the port number you used if you changed it in the ini file or used the -p command line switch.

Most firewalls on servers and workstations don't require specific rules for outbound, so most likely you will only need to configure the Inbound rule on the GUI / Server machine if it has a firewall.


#### 3. Run the GUI Server

```
rfswarm
```

#### 4. Manual Install the prerequisites

- The GUI/Server machine needs to use a minimum of Python 3.7
> ThreadingHTTPServer feature of HTTPServer requires was added in Python 3.7

- tkinter may need to be installed
It may already installed on your system, if not consult the python documentation on how to install for your system.

On Debian based systems this will probably work
```
apt install python3-tk
```

Additionally the following pip command might be needed if these are not already installed on your system:
```
pip* install configparser setuptools hashlib HTTPServer pillow
```
> setuptools (is required by hashlib and HTTPServer)

\*some systems might need you to use pip3 and or sudo

#### 5. Manual Run the GUI Server

Use this method if you did not install using pip

```
python* rfswarm.py
```
\*or python3 on some systems


### Agent Assignment

As a result of experience with other load testing tools and difficulties in managing load generation machines, the agent assignment algorithm in rfswarm has been designed to switch modes to cater for several scenarios but not require manual intervention

The scenarios rfswarm has been designed to cater for:

1. Need to ensure each agent gets only 1 virtual user each
2. When there is a low number of virtual user, you want them distributed evenly across all the agents
3. When the agent machines are a variety of hardware (newer and older machines) you don't want the virtual user distributed evenly across all the agents, but rather you want the more powerful agents to take a larger share of the virtual users to avoid any agent getting overloaded.
4. Sometimes you need to apply a custom filter to Require/Exclude a test group to run on specific agents or groups of agents.

How the assignment algorithm works:
- As the scenario is ready to start the next virtual user the GUI/Server calls the assignment algorithm
- First the agents are checked against the Agent Filter rules for the test group that is requiring an agent to be assigned, if the agent passes all the filter rules it is added to the list to be sorted.
- Next the assignment algorithm sorts the agents list by the number of virtual users assigned to each agent
- The agent with the lowest number of assigned virtual users is selected, there may be several agents with the equal lowest number of virtual users, e.g. at the start of the test all agents equally have zero (0) virtual users assigned, then the first agent from the list with this assigned count is selected.
- Before returning the selected agent the assigned virtual user count is checked to see if it is greater than 10, if not the selected agent is returned from the assignment algorithm.
- If the selected agent's assigned virtual user count is greater than 10, the selection is discarded and the assignment algorithm returns to the filtered agent list.
	- this time the agent list is sorted by the agent loads (See Load column in the screen shot of the agents tab above), where the load is simply the highest of the 3 monitored percentages (% CPU Usage, % Memory Consumption, % Network bandwidth usage)
	- the machine with the lowest load is selected and returned from the assignment algorithm.


### Credits

The icons used for the buttons in the GUI were derived from the Creative Commons licensed (Silk icon set 1.3)[http://www.famfamfam.com/lab/icons/silk/]
