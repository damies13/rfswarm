
[Index](README.md)

## Overview / Concepts

rfswarm is made up of 3 components, the [Manager](rfswarm_manager.md) where you plan and run your test scenario, the [Agents](rfswarm_agent.md) which runs the Robot Framework tests, and the [Reporter](rfswarm_reporter.md)

- [Manager](#manager)
- [Agents](#Agents)
- [Robot File handling (transfer from Manager to Agent)](#robot-file-handling-transfer-from-manager-to-agent)
- [Reporter](#Reporter)


<kbd>
<img align="centre" height="500" src="Images/Manager&Agent_Example.png">
</kbd><br>
An example of how your rfswarm setup might look.

### Manager

This is the swarm manager where you schedule and monitor your swarm of robots.

You only need one manager, the machine you use for this can be an ordinary desktop machine, as this component is not expected to have exceptional CPU or memory requirements.

While python is required to run this component, Robot Framework is not required. However as this is most likely to be your own desktop machine you may need Robot Framework installed to develop and test your test cases in preparation for performance testing.


### Agents

This is the component that actually executes the tests, so Robot Framework need to be installed on these machines.

How many and what specifications these machines need will depend on your application under test. Some examples of what to consider:

 - A web application being tested using SeleniumLibrary, My initial tests indicate that with headlessfirefox, a mid range desktop PC should be able to support around 50 virtual users, obviously this will vary depending on the amount of think time you include, how javascript heavy your application is a few short (~5 minutes) runs with 10, 30 & 50 users on one agent should give you a feel for what your agent machines are capable of. This is quite comparable to JMeter and loadrunner when using TruClient protocol.
 - An application using libraries such as SudsLibrary, RESTinstance, HTTP library (Requests), Database Library (Python), SSHLibrary, TFTPLibrary, etc should be fairly low resource usage on the agent machine and will probably let you run many more virtual users than a SeleniumLibrary based test.
 - A thick client desktop application using libraries such as AutoItLibrary, SikuliLibrary, WhiteLibrary, etc will probably limit you to 1 (one) virtual user per agent, though some possible work arounds for this might be:
 	* Running the agents in minimal virtual machines (e.g. 1-2 cpu cores and 2-4GB ram) and then running multiple VM's on the physical machines allocated for your agents.
	* Install Microsoft Terminal Services (Windows Server)/ Citrix (Windows Server) / Xvnc (Linux/Unix) on your agent machine and then run an agent in each desktop session
	* using docker images and running the desktop application and the agent with robot framework inside the docker container.

Additional details can be found in the [Hardware Requirements](HardwareRequirements.md#Agents)

### Robot File handling (transfer from Manager to Agent)

Firstly the assumption is made that the Agent and the Manager are not necessarily the same operating system or on the same network (e.g. the Manager might be in a corporate network and the Agent on virtual machine from a cloud provider like AWS). So based on this it is assumed that the Agent and Manager might not have any shared network locations etc. This key assumption drove the design for how the Manager and Agent handle all files.

The Manager and the Agent both internally have the concept of a file hash being the key identifier of a file, then a file also has a relative path and a local path.

#### Manager side
When you select a robot script, the Manager considers the directory this robot file is in to be the base directory, so everything is relative to this robot file.

So the following happens on the Manager when a robot file is selected:
- The Manager does a md5 hash of the file, this hash is used as the key to reference the file from now on.
- The selected robot file is given a relative path of just the file name of the robot file.
- The the scenario file list in the Manager is updated with the the hash and the local and relative paths as properties of the hash.
- The Manager then scans the robot file looking for resource and variable files (support files), for each file found:
	- The support file's relative path and local paths are determined.
	- The Manager does a md5 hash of the support file (Again this hash is used as the key to reference this support file from now on)
	- The the scenario file list in the Manager is updated with the the hash and the local and relative paths as properties of the hash for this support file.

#### Agent side
When the request for a file list is sent from the Agent, the Manager returns a list of hash keys from the Manager's in memory scenario file list.

The Agent then:
- Checks it's internal list of files using the hash as a reference key
- If the file hash is in memory on the Agents file list, then there is nothing further to do for this file, check the next one, until all checked.
- If the file hash is not in memory on the Agents file list:
	- Request the file from the Manager (post to /file, with the hash as the post data)
	- The Manager will return the relative path and the file contents (compressed base 64 string)
	- The Agent the saves the file relative to the scripts directory in temp (the Agent gets temp from the os when it starts)
	- The Agent update it's in memory file list using the hash as the key, the relative path and the local path (this is likely very different to the local path on the Manager) as properties of the hash.

It is not recommended to use fixed paths in your robot file unless you are sure that the path will be the same on the Manager and all Agents.


### Reporter

This component is used to assist you in reporting the results of your performance tests and is a completly optional component. You only need one reporter machine, and if your test schedule is not too busy this can be the same machine as the manager.
