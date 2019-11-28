
[Index](Index.md)

## rfswarm.py (GUI / Server)

rfswarm.py is the GUI and central server component of rfswarm, this is where you plan, execute and monitor your performance test.

- [User Interface](#User-Interface)
	- [Plan](#Plan)
	- [Run](#Run)
	- [Agents](#Agents)
- [Install and Setup](#Install-and-Setup)
	- [Install the prerequisites](#1-install-the-prerequisites)
	- [Adjust the Firewall](#2-Adjust-the-Firewall)
	- [Run the GUI Server](#3-Run-the-GUI-Server)
- [Agent Assignment](#Agent-Assignment)
- [Credits](#Credits)

### User Interface
#### Plan
This is where you construct your test scenario, choose your test cases and number of virtual users

All the time fields (Delay, Ramp Up & Run) are in Seconds, due to the way the [agent polling](./rfswarm_agent_py.md#agent-polling-of-the-guiserver) works it's best not to use values less than 10 seconds.

![Image](Images/Plan_saved_opened_v0.3.png "Plan - Planning a performance test")
	**_Plan - Planning a performance test_**

![Image](Images/Plan_unsaved_v0.3.png "Plan - New")
	**_Plan - New_**

![Image](Images/Linux-Plan-v0.4.3.png "Plan - Linux")
	**_Plan - Linux (Mint 19.2)_**

While hopefully this is intuitive, the buttons are (starting top right)
- New			- Create a new scenario
- Open			- Open an existing scenario
- Save			- Save the current scenario
- Play			- Play the current scenario
- Add (+)		- Add another test group
- Select (...)	- Select a robot file
- Remove (X)	- Remove this test group

#### Run
This is where you monitor your test scenario as it runs, here you will see number of robots running, how long the has been running and live updates of the test results.

Unique by check boxes:
- Index, use this if multiple test cases have results with the same result name but you want to keep the result timings separated based on the individual test cases.
- Iteration, use this if you want to keep the result timings separated based on the test iteration.
- Sequence, use this if multiple test steps in the same test case have the same result name but you want to keep the result timings separated based on the sequence within the test case.

%ile (Percentile) field:
The default value is 90, you can adjust the percentile value between 1% and 99% depending on your application's performance requirements.

Stop button
Use this if you want to stop the test early. You may not notice an immediate reaction as pressing the button just changes the end time on all the test jobs assigned to the current time and stops the ramp-up if the test is still in the ramp-up phase. While there is no benefit to pressing the stop button multiple times there is no harm either, so press to your hearts content.
Once the stop button has been pressed the agents will receive the changed end time when they [poll](./rfswarm_agent_py.md#agent-polling-of-the-guiserver) the GUI/Server next, the agent will change status to stopping which will be returned on the next poll interval and the agent will not start a new iteration for the running tests, however the ones currently running will be allowed to complete.

![Image](Images/Run_Start_v0.4.png "Run - Just Started")
	**_Run - Just Started_**

![Image](Images/Run_v0.4.png "Run - Showing results being collected live")
	**_Run - Showing results being collected live_**

![Image](Images/Linux-Run-v0.4.3-10u1hr.png "Run - Linux 10 users running for over 1 hour")
	**_Run - Linux 10 users running for over 1 hour_**

![Image](Images/Linux-Run-v0.4.3-50u1hr.png "Run - Linux 50 users running for over 1 hour")
	**_Run - Linux 50 users running for over 1 hour_**


#### Agents
This is where you can see which agents have connected, number of robots on each agent and monitor the status and performance of the agents.
![Image](Images/Agents_ready_v0.3.png "Agents - Ready")
	**_Agents - Ready_**

![Image](Images/Agents_stopping_v0.3.png "Agents - Stopping")
	**_Agents - Stopping_**

![Image](Images/Linux-Agents-v0.4.3.png "Agents - Running - Linux")
	**_Agents - Running (Linux)_**

### Install and Setup

#### 1. Install the prerequisites

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

#### 2. Adjust the Firewall

Check if there is a firewall on you GUI / Server machine, if so you may need to adjust the firewall to add a rule to allow communication between the GUI / Server and the Agent.

| Machine | Protocol | Port Number | Direction |
|---|---|---|---|
| GUI / Server | TCP | 8138 | Inbound |
| Agent | TCP | 8138 | Outbound |

Most firewalls on servers and workstations don't require specific rules for outbound, so most likely you will only need to configure the Inbound rule on the GUI / Server machine if it has a firewall.


#### 3. Run the GUI Server

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

How the assignment algorithm works:
- As the scenario is ready to start the next virtual user the GUI/Server calls the assignment algorithm
- First the assignment algorithm sorts the agents list by the number of virtual users assigned to each agent
- The agent with the lowest number of assigned virtual users is selected, there may be several agents with the equal lowest number of virtual users, e.g. at the start of the test all agents equally have zero (0) virtual users assigned, then the first agent from the list with this assigned count is selected.
- Before returning the selected agent the assigned virtual user count is checked to see if it is greater than 10, if not the selected agent is returned from the assignment algorithm.
- If the selected agent's assigned virtual user count is greater than 10, the selection is discarded and the assignment algorithm returns to the agent list.
	- this time the agent list is sorted by the agent loads (See Load column in the screen shot of the agents tab above), where the load is simply the highest of the 3 monitored percentages (% CPU Usage, % Memory Consumption, % Network bandwidth usage)
	- the machine with the lowest load is selected and returned from the assignment algorithm.


### Credits

The icons used for the buttons in the GUI were derived from the Creative Commons licensed (Silk icon set 1.3)[http://www.famfamfam.com/lab/icons/silk/]
