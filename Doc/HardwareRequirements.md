
[Index](README.md)

# rfswarm (Robot Framework Swarm) Hardware Requirements

- [Manager](#Manager)
- [Agents](#Agents)

## Manager

The Hardware Requirements for the Manager are pretty minimal, for example to open the Manager and load a scenario takes about 70MB, running this scenario with 300 robots needed around 120MB and used ~50 threads, so a multi core CPU is a good idea.

Recommended minimums:

|CPU|Memory|Disk|
|---|---|---|
|Dual Core 1Ghz| 512MB above OS Requirements|1GB free|

## Agents

The agent requirements really depend on how many robots you want to run and which test library (libraries) you want to use. If you are able to run 1 Robot Framework robot against your application and still have 50Mb free, then you should be able to run the agent with 1 robot, if you are testing with a desktop application using libraries such as AutoItLibrary, SikuliLibrary, WhiteLibrary, etc this is probably all you need as the limiting factor is not hardware anyway.

Below is some examples of the number of users you can run on some pretty low end hardware:

A [2013 11" Macbook Air 1.3GHz dual-core i5 4Gb ram](https://support.apple.com/kb/sp677?locale=en_US) used as a dedicated rfswarm agent is able to run about this many robots:

|Robot Library		|Robots	|Hardware Limitation|struggles with robots	|
|---				|---	|---				|---					|
|SeleniumLibrary	|30		| Memory (Ram) ~80%	|40 					|
|RequestsLibrary	|230	| Memory (Ram) >70%, CPU > 60% at times|240	|
