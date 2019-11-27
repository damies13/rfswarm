
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

Some screen shots below of rfswarm in action:
##### Plan
This is where you construct your test scenario, choose your test cases and number of virtual users
![Image](Images/Plan_saved_opened_v0.3.png "Plan - Planning a performance test")
![Image](Images/Plan_unsaved_v0.3.png "Plan - New")
##### Run
This is where you monitor your test scenario as it runs, here you will see number of robots running, how long the has been running and live updates of the test results
![Image](Images/Run_Start_v0.4.png "Run - Just Started")
![Image](Images/Run_v0.4.png "Run - Showing results being collected live")
##### Agents
This is where you can see which agents have connected, number of robots on each agent and monitor the performance of the agents
![Image](Images/Agents_ready_v0.3.png "Agents Ready")
![Image](Images/Agents_stopping_v0.3.png "Agents Stopping")

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
