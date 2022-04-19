
[Index](README.md)

# rfswarm (Robot Framework Swarm) Frequently Asked Questions

- [Can I run the Agent and the Manager on the same machine?](#can-i-run-the-agent-and-the-manager-on-the-same-machine)
- [The Agent doesn't connect to the Manager?](#the-agent-doesnt-connect-to-the-manager)
- [I have some experience in performance testing, can you translate the terminology between rfswarm and tool xzy?](#i-have-some-experience-in-performance-testing-can-you-translate-the-terminology-between-rfswarm-and-tool-xzy)
- [Can you help me get started? Which test cases should I choose?](#can-you-help-me-get-started-which-test-cases-should-i-choose)
- [Do we have any sample test cases?](#do-we-have-any-sample-test-cases)
- [Is there a tutorial on how to use rfswarm?](#is-there-a-tutorial-on-how-to-use-rfswarm)
- [does rfswarm support IPv6?](#does-rfswarm-support-ipv6)


## Can I run the Agent and the Manager on the same machine?

Yes running the Agent and the Manager on the same machine is ok for small numbers of robots (users), but if you want to run any significant load then you will probably need some separate machines for the agent.

You will probably want to refer to the [Hardware Requirements](HardwareRequirements.md)

## The Agent doesn't connect to the Manager?

There may be a firewall blocking the communication, Windows 10, Recent Mac OSX and some linux desktop distributions come with a firewall enabled by default. Consult your operating system documentation for both the Agent and Manager machines to confirm if this is the case, if so you may need to [add a firewall rule](./rfswarm_py.md#2-adjust-the-firewall).

## I have some experience in performance testing, can you translate the terminology between rfswarm and tool xzy?

This should cover off the main components with the most common tools:

|rfswarm|Loadrunner|JMeter|
|-------|----------|------|
|Manager|Controller|JMeter client (JMeter GUI)|
|Agents|Agent process (sometimes called Load Generators or Injectors)|JMeter servers (JMeterEngine)|
|Reporter|Analysis||
|Scenario|Scenario|Test Plan|
|Test Case|Script|Thread Group|

## Can you help me get started? Which test cases should I choose?

First you need to work out from your existing test cases which ones to use (there may be hundreds to choose from), if you have someone with performance testing experience let them guide you.

Usually the test cases you want to select is the are related to the business processes that make up around 70-80% of user activity in your system. It often surprises people that are not performance testers, that for most applications this is usually 3-5 business processes, so you will want to start with these 3-5 test cases, in addition to these you may also need to add another 1-3 test cases in low user numbers if the business decides that these processes are "mission critical" but this is pretty rare.

But start with one test case from the group that makes 70-80% of user activity, without knowing your application or your companies usage of that application I can't say which ones they are, but let your Business Analyst guide you on that.

Second step is to adjust the test case for performance testing, really this is just about making the script perform more human like, people don't fill in all the fields and click submit within a second of the page loading, so your performance script shouldn't either, add some "think time" to simulate the user reading the information on the screen, cross referencing information in email or on paper, etc.

Also people don't repetitively use the values when they enter information into the system, so, again your performance script shouldn't either, make sure for any value you are entering into the application there is plenty of data variation, for example, if you are entering a person's name, then you'll want a data sheet with several thousand names to pick from, if you have a copy of your production system then this can be quite easy to get, with a simple sql query against you database.

Finally you'll need some machines to run the test, how many will depend on your application, if your application is accessed through a web browser then you can run many users on one agent machine, if it requires a desktop application to access then you may only be able to run one user per agent machine, you'll also need a machine to run the rfswarm Manager

To get started have at least 3 machines ready, run the Manager (rfswarm.py) on your first machine (Machine A), just make sure the Manager loads and you can browse to your robot files.

Next on machines B & C, first make sure that your test cases run on these machines by opening a command line and running robot with the -t switch for your test case (robot -h will explain what you need to do here) and, once you have confirmed that robot works properly on machines B & C then run the agent (rfswarm_agent.py) don't forget to point the agents to Machine A.

Next on Machine A, in the rfswarm Manager, create a new scenario, just make it a really simple to start with, one test case, see this screen:
![Plan New](./Images/MacOS_Plan_v0.8.0_New.png)
The button next to the script field will let you browse for and select your robot file, once you do this the test option list will be populated with the test cases in your robot file, select the one you used above. for the initial test, set the users to 2 and the rampup to 30 (seconds) and run to 120 (seconds / 2 minutes). then click the agents tab and check that machines B & C are showing up in the agents list, if they are, your are good to go, switch back to the plan tab and click play, once you do the ui will switch to the run tab, within 15-30 seconds the test case should start up with 1 user on each machine B and C, and soon you will start seeing results appear in the run tab.

If you get this far successfully then you will be well on the way to using rfswarm, from here it's just adding more users, additional test cases and more agent machines, until you get the load you need to simulate on your application.


## Do we have any sample test cases?

At the moment I'm not providing any sample test cases, the test cases I have, run against opencart (https://www.opencart.com/), so while it would be easy for me to provide some test cases against the opencart demo site, i'm reluctant to do so, as people might load up the demo site without first getting permission to do so. I do not want to encourage this.

Additionally rfswarm is aimed at people / teams already using robot framework, with a performance tester looking to leverage existing functional test scripts for reuse for performance testing as well, so it's expected that rfswarm users will already have test cases, you just need to add some minor adjustments to as covered in the documentation [Preparing for performance](./Preparing_for_perf.md)


## Is there a tutorial on how to use rfswarm?

There is a tutorial planned, but it's still in the early stages, and for now I want to concentrate on fixing bugs and getting rfswarm to version 1.

The first step in the tutorial will be to download the example opencart virtual machine image (https://bitnami.com/stack/opencart/virtual-machine) and set that up on a server that you own / control (this is how I test rfswarm). If you don't have an application you can run robot framework scripts on (i.e. you are trying out rfswarm at home), then this application is quite easy to write robot framework scripts for and has fairly minimal virtual machine requirements.

## does rfswarm support IPv6?

As far as I know all components of rfswarm work with IPv6, what I can confirm works:
- communication between the agents and manager in IPv6 only network
- communication between the agents and manager in IPv6+IPv4 dual stack network
- binding the manager to an IPv6 address
- configuring the agent ini file with IPv6 address of the manager
- configuring the agent ini file with a manager name that only resolves to an IPv6 address

rfswarm works in IPv4 only networks as well.
