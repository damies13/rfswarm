
[Index](Index.md)

## Overview / Concepts

rfswarm is made up of 2 components, the [GUI / Server](rfswarm_py.md) where you plan and run your test scenario and the [Agents](rfswarm_agent_py.md) which runs the Robot Framework tests.

### GUI / Server

This is the swarm scheduler, controller and monitor

You only need one of these, the machine you use for this can be an ordinary desktop machine, as this component is not expected to have exceptional CPU or memory requirements.

While python is required to run this component, Robot Framework is not required. However as this is most likely to be your own desktop machine you may need Robot Framework installed to develop and test your test cases in preparation for performance testing.


### Agents

This is the component that actually executes the tests, so Robot Framework need to be installed on these machines.

How many and what specifications these machines need will depend on your application under test.
