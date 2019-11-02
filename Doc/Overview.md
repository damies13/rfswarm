
[Index](Index.md)

## Overview / Concepts

rfswarm is made up of 2 components, the [GUI / Server](rfswarm_py.md) where you plan and run your test scenario and the [Agents](rfswarm_agent_py.md) which runs the Robot Framework tests.

### GUI / Server

This is the swarm scheduler, controller and monitor

You only need one of these, the machine you use for this can be an ordinary desktop machine, as this component is not expected to have exceptional CPU or memory requirements.

While python is required to run this component, Robot Framework is not required. However as this is most likely to be your own desktop machine you may need Robot Framework installed to develop and test your test cases in preparation for performance testing.


### Agents

This is the component that actually executes the tests, so Robot Framework need to be installed on these machines.

How many and what specifications these machines need will depend on your application under test. Some examples of what to consider:

 - A web application being tested using SeleniumLibrary, My initial tests indicate that with headlessfirefox, a mid range desktop PC should be able to support around 50 virtual users, obviously this will vary depending on the amount of think time you include, how javascript heavy your application is a few short (~5 minutes) runs with 10, 30 & 50 users on one agent should give you a feel for what your agent machines are capable of. This is quite comparable to JMeter and loadrunner when using TruClient protocol.
 - An application using libraries such as SudsLibrary, RESTinstance, HTTP library (Requests), Database Library (Python), SSHLibrary, TFTPLibrary, etc should be fairly low resource usage on the agent machine and will probably let you run many more virtual users than a SeleniumLibrary based test.
 - A thick client desktop application using libraries such as AutoItLibrary, SikuliLibrary, WhiteLibrary, etc will probably limit you to 1 (one) virtual user per agent, though some possible work arounds for this might be:
 	* Running the agents in minimal virtual machines (e.g. 1-2 cpu cores and 2-4GB ram) and then running multiple VM's on the physical machines allocated for your agents.
	* Install Microsoft Terminal Services (Windows Server)/ Citrix (Windows Server) / Xvnc (Linux/Unix) on your agent machine and then run an agent in each desktop session
