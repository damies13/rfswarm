# rfswarm (Robot Framework Swarm)


<img align="right" src="Doc/Images/Icon_Information.png">

## About
rfswarm is a testing tool that allows you use [Robot Framework](https://robotframework.org/) test cases for performance or load testing.

> _Swarm being the collective noun for Robots, just as Flock is for Birds and Herd for Sheep, so it made sense to use swarm for a performance testing tool using Robot Framework, hence rfswarm_

![Image](Doc/Images/MacOS_Plan_v0.8.0_saved_opened.png "Plan - Planning a performance test")

While Robot Framework is normally used for functional or regression testing, it has long been considered the holy grail in testing for there to be synergies between the functional and performance testing scripts so that effort expended in creating test cases for one does not need to be duplicated for the other which is currently the normal case.

rfswarm aims to solve this problem by allowing you to take an existing functional or regression test case written in Robot Framework, make some minor adjustments to make the test case suitable for performance testing and then run the Robot Framework test case with as many virtual users (robots) as needed to generate load on the application under test.

rfswarm is written completely in python, so if you are already using Robot Framework, then you will already have most of what you need to use rfswarm and will be familiar with pip to get any extra components you need.

To learn more about rfswarm please refer to the [Documentation](Doc/README.md)

![Image](Doc/Images/MacOS_Run_v0.6.3_100u_2h.png "Run - Showing results being collected live")

<img align="right" src="Doc/Images/Icon_Help.png">

## Getting Help

- [rfswarm Documentation](Doc/README.md)
- [Discord](https://discord.gg/jJfCMrqCsT)
- [Reporting Issues / Known Issues](https://github.com/damies13/rfswarm/issues)

<kbd align="centre">
<img align="centre" height="350" src="Doc/Images/Manager&Agent_Example.png">
</kbd><br>
An example of how your rfswarm setup might look.

<img align="right" src="Doc/Images/Icon_Donate.png">

## Donations

If you would like to thank me for this project please consider using one of the sponsorship methods:
- [Github](https://github.com/sponsors/damies13/)
- [PayPal.me](https://paypal.me/damies13/5) (the $5 is a suggestion, feel free to change to any amount you would like)
