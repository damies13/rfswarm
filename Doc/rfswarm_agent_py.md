
[Index](Index.md)

## rfswarm_agent.py (Agent)

rfswarm_agent.py is the agent component that actually runs the Robot Framework test cases and returns the results to rfswarm. The agent has no GUI

### Install and Setup

#### 1. Robot Framework
Firstly ensure Robot Framework is installed with the libraries needed for your application, then try running your test case from the command line of you agent machine e.g.
```
robot -t "test case" script.robot
```

#### 2. Install the prerequisites

- The Agent machine needs to use a minimum of Python 3.7
> ThreadingHTTPServer feature of HTTPServer requires was added in Python 3.7

- tkinter may need to be installed
It may already installed on your system, if not consult the python documentation on how to install for your system.

On Debian based systems this will probably work
```
apt install python3-tk
```

Additionally the following pip command might be needed if these are not already installed on your system:
```
pip\* install configparser setuptools hashlib HTTPServer pillow
```
> setuptools (is required by hashlib and HTTPServer)

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

![Image](Images/Agents_ready.png "Agents Ready")
