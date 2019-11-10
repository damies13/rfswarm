
[Index](Index.md)

## rfswarm.py (GUI / Server)

rfswarm.py is the GUI and central component of rfswarm, this is where you plan, execute and monitor your performance test.

Some screen shots below of rfswarm in action:
##### Plan - This is where you construct your test scenario, choose your test cases and number of virtual users
![Image](Images/Plan_saved_opened_v0.3.png "Plan - Planning a performance test")
![Image](Images/Plan_unsaved_v0.3.png "Plan - New")
##### Run - This is where you monitor your test scenario as it runs, here you will see number of robots running, how long the has been running and live updates of the test results
![Image](Images/Run_Start_v0.3.png "Run - Just Started")
![Image](Images/Run_v0.3.png "Run - Showing results being collected live")
##### Agents - This is where you can see which agents have connected, number of robots on each agent and monitor the performance of the agents
![Image](Images/Agents_ready_v0.3.png "Agents Ready")
![Image](Images/Agents_stopping_v0.3.png "Agents Stopping")

### Install and Setup

#### 1. Install the prerequisites

The Agent machine needs to use a minimum of Python 3.7
> timespec feature of datetime's isoformat requires Python 3.6+

Additionally the following pip command might be needed if these are not already installed on your system:
```
pip\* install configparser requests psutil
```
\*some systems might need you to use pip3 and or sudo

#### 2. Run the GUI Server

```
python rfswarm.py
```
\*or python3 on some systems
