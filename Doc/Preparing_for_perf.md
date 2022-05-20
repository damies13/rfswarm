
[Index](README.md)

## Preparing a test case for performance

Some of the things you will need to consider when taking a functional or regression test and using it for performance are:
- [Think Time](#Think-Time)
- [Useful Variables](#Useful-Variables)
- [Data Management](#Data-Management)
- [Keywords](#Keywords)
- [Browser](#Browser)

### Think Time

Because functional and regression tests are designed to run as a single user and test the functionality as quickly as possible, for performance testing we want to simulate real user behaviour so we want to put some user thinking time or pauses into the script.

Why is this is important?
- Session Time: Users don't immediately start filling in fields the moment the page or screen has loaded, they sit and read information on the screen and then start filling in the fields, often pausing or referring to documents, emails, or paper forms for the next piece of information they need to key in. If you don't simulate this behaviour in a load test, you risk having much shorter session times that wouldn't really occur and this might lead to you missing a memory issue or session limit in your application server.
- Background Polling: Many applications poll the server in the background while the user is idle to update dynamic data displayed on the screen, this is becoming increasingly common with web 2.0 style web applications, by not having any or sufficient user thinking time in your scripts, your robots might not trigger this polling or may not trigger this polling to the same extent as a real user would, so you will end up applying a lighter load on the application server that is realistic. Never under estimate the impact of background polling, application servers have flatlined at 100% CPU from just 5 users logged in and sitting idle because of 1 poorly constructed background polling event that was taking 25% of the application server's CPU per user calling this polling event.
- Overloading your agents: Launching and client applications or web browsers is a hardware intensive (CPU, Memory, and Disk) task for your agent machines, without sufficient user thinking time in your scripts, you will increase the workload you are placing on your agent machines without applying any load to your application under test. This will end up in limiting the number of robots you can run on a single agent machine and potentially limit the overall number of robots you can run in a test or increase significantly the number of agent machines you need to drive a specific load profile.

The easiest way to simulate this user behaviour would be to simply use the Robot Framework's built in sleep command:

```
	Sleep	30
```

The only issue with just using Sleep like this is that it can make the script too regular and cause cadence issues, so just like with other performance testing tools we want to have a variable think time, to do this we can import randint from python's random library to pick a time to sleep between a minimum and maximum value, e.g. 15 and 45.

```
	${number}    Evaluate    random.randint(15, 45)    random
	Sleep    ${number}
```

Adding these 2 lines many places throughout your script could become messy and also a hassle should you need to change the minimum and maximum values. So to make life easier in the [Robot Resources](../Robot_Resources) folder there is a [perftest.resource](../Robot_Resources/perftest.resource) file that you can include in the Settings section of your .robot file like this:

```
*** Settings ***
Resource    perftest.resource
```

Then you can simply include the `Standard Think Time` keyword between each user action in your test cases or keywords. The default minimum is set to 15 seconds and the default maximum is set to 45 seconds. If you want to over ride these defaults for a specific test case or all the test cases in you .robot file simply set a new value to the `${STT_MIN}` and  `${STT_MAX}` variables.

### Useful Variables

When an agent runs a robot test case it passes some variables on to the test case that might be useful to know or used to trigger variations in behaviour in you test cases. While there is no requirement to use these variables they are values that I have had to manually implement in laodrunner scripts, so knowing I would find them useful I have included them by default to make life easier.

#### Index
Index should be available through the variable `${RFS_INDEX}`, this is the number you see in the Index column at the bottom of the plan screen

#### Robot number
Robot number should be available through the variable `${RFS_ROBOT}`, referring to the Robots column at the bottom of the plan screen, this number is the counter of the robot from one to the number in the Robots column.
While this number on it's own is not unique, it will be unique relative to the Index above, so if you need a unique string in your test you could combine them. e.g. `${RFS_INDEX}_${RFS_ROBOT}`
Another way this could be useful is as a data row offset so that each test robot is using data from a different section of your data file.

#### Iteration
Iteration should be available through the variable `${RFS_ITERATION}`, This is simply a counter of how many times this test case has been run for this robot. This could be useful if for example you need to walk sequentially through a data file because your data is single use.

#### Swarm Manager
Swarm Manager should be available through the variable `${RFS_SWARMMANAGER}`, this will be useful for sending custom metric data back to the rfswarm manager, for example when using a robot test / task to collect statistics from the application under test.

### Data Management

Because functional and regression tests are designed to test specific functionality, the test data is designed to test boundary or edge cases so are limited to a small set of cases or are static. With performance testing we don't want this, rather we want hundreds or even thousands of different data values so we can better emulate user behaviour and ensure we are not constantly hitting a single cached value and reporting unrealistically fast response times.

#### [Faker Library](https://github.com/guykisel/robotframework-faker)

[robotframeork-faker](https://github.com/guykisel/robotframework-faker) can produce realistic locale aware generated data values for a large variety of data type including names, email and physical addresses, phone numbers etc.

#### Reading Data Files

To make life easier when reading data from files, in the [Robot Resources](../Robot_Resources) folder there is a [perftest.resource](../Robot_Resources/perftest.resource) file that you can include in the Settings section of your .robot file like this:

```
*** Settings ***
Resource    perftest.resource
```

For Reading Data Files [perftest.resource](../Robot_Resources/perftest.resource) provides the keywords `Get File Dir` and `Get Data Row`

```
*** Test Cases ***
File Test Examples
	${FILE_DIR} = 	Get File Dir
	Get Data Row	${FILE_DIR}/ProductList.csv
	Get Data Row	${FILE_DIR}/ProductList.csv 	"Random"
	Get Data Row	${FILE_DIR}/ProductList.tsv 	"Sequential"
	Get Data Row	${FILE_DIR}/ProductList.csv 	3
	${next_row} = 	Evaluate	${RFS_ROBOT} + ${RFS_ITERATION}
	Get Data Row	${FILE_DIR}/ProductList.csv 	${next_row}

```

- `Get Data Row` defaults to Random, so the first 2 `Get Data Row` examples are the same
- Sequential is only useful if you are accessing multiple rows in the same test case
- The third option is to parse a row number directly, this could be a fixed number or a calculated value

#### Support Files

Robot Framework only has 2 ways to include a file in your robot file, the `Resource` Setting or the `Variables` Setting.

```
*** Settings ***
Resource    perftest.resource
Resource    ../Robot_Resources/perftest.resource
Variables   myvariables.py
```

Unfortunately if you include a csv or tsv file with either `Resource` or `Variables` setting, Robot Framework will error.

Likewise for some test cases you will want to have some additional support files like Images, PDF's, Word or Excel Documents that you want to use for attaching to a web form, loading into a client application etc. If you use either `Resource` or `Variables` setting for these files Robot Framework will most likely error too.

To ensure these files get transferred to the Agent so that your test case can find them rfswarm uses the `Metadata` Setting with the name `File` to provide an additional way to include files. As a bonus when using `Metadata    File` you can also use wildcards to transfer multiple files

```
*** Settings ***
Metadata	File    ProductList.tsv
Metadata	File    *.csv
Metadata	File    images/*.jpg
Metadata	File    uploads/*.*
```

rfswarm ensures all the files referenced using `Resource`, `Variables` and `Metadata    File` in the Settings section of your robot file are transferred to the agent in the same relative path to your robot file.

#### TestDataTable

Often when testing applications there are business processes that produce system generated data or use system generated data from a previous business process. with regression testing it's quite simple to string the business process together in one really long test case and simply pass the value along as a variable.

In performance testing it's not always that simple:
- When you string the business process together the test case may run for many hours or even days, but you want your performance test to only run for a set period like a standard day.
- You want to ensure you hit the transaction rates required for each individual process and the processes in that set will often have different rates that need to be achieved.
- You don't want all the users doing the first step in the process at the start of the performance test and then 2 hours none are doing that process because they are all up to the 3rd or 5th process in the sequence.
So you really need a way to pass these values from one test to another from one robot process to another and robot process and ideally from one robot process on one agent machine to another robot process running a different agent machine.

So to help with this the [TestDataTable](https://github.com/damies13/TestDataTable) project was created. It is a data table server that makes it easy to pass data between scripts and robot processes.

Here's an example of how you might use [TestDataTable](https://github.com/damies13/TestDataTable), your application under test is an online store (shopping cart) and you have the following three scripts that all use the order number created by the application when the user places an order:
1) Create order, User navigates to the online store selects some products and places an order. after success user receives an order number.
2) Check order status, this script simulates the user returning to the online store to check the status of their order.
3) Process Order, this script simulates the store owner or staff member updating the order status from new to processed and adding the shipping tracking number and link.

- Script 1, would save the order number (and the username details of the user that placed the order) into a TestDataTable column called "orders"
- Script 3, would pick up order numbers from the "orders" column in the TestDataTable, and once the order has been processed place the order number to another column called "processed" in the TestDataTable.
- Depending on your requirements script 2 could pick up order numbers from either or both columns, order numbers picked up from the "orders" column would be returned to the "orders" and order numbers picked up from the "processed" column would be returned to the "completed" column.

By setting up your scripts to operate this way you can also run scripts 1 & 3 prior to the test to ensure there is some data already available so that when you run your test all the scripts have data to work with from the start of the test, likewise system generated data from your first test doesn't need to go wasted and can be used for the next test.

TestDataTable's regression test cases provide 2 alternate ways you can use TestDataTable with your test cases:
- [Using Robot Framework's RequestsLibrary, JsonValidator and Collections Libraries](https://github.com/damies13/TestDataTable/blob/master/Regression_Tests/TestDataTable-API_requests.robot)
- [Using Robot Framework's REST Library](https://github.com/damies13/TestDataTable/blob/master/Regression_Tests/TestDataTable-API_REST.robot)

Both methods demonstrate TestDataTable's functionality, and for more details you can refer to [TestDataTable's documentation](https://github.com/damies13/TestDataTable/blob/master/Doc/Index.md).

Why is TestDataTable a seperate project? simply because I wanted TestDataTable to be able to be used by other test tools as well, for example there is nothing stopping you to use TestDataTable with your regression test suite to make your test cases shorter and enable them to run in parallel, likewise TestDataTable could be used by other performance test tools like JMeter.

### Keywords

As you will most likely have built your own custom keywords for navigating your AUT, you may want to get the time taken for these keywords, so controlling which keywords are reported to the Manager and which are not is as simple as including or leaving out the [keyword [Documentation]](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#user-keyword-documentation)

Consider the following keyword examples

```
*** Keywords ***
Example Keyword
    [Documentation]    TC01 My Example Keyword
    No Operation

Quiet Keyword
    No Operation

Match Keyword
    [Documentation]    ${TEST NAME}
    No Operation


```

#### No Operation
Would not have a timing measured by default because this keyword belongs to the builtin which is one of the default [excluded libraries](./rfswarm_agent.md#exclude-libraries)

#### Example Keyword
Would have a timing measured by default, this would be reported in the Manager as "TC01 My Example Keyword" along with the time taken to perform the step No Operation

#### Quiet Keyword
Would not have a timing measured, because it has no [Documentation], however it will still get executed wherever it is called.

#### Match Keyword
Would have a timing measured by default, this would be reported in the Manager as "Match Keyword" because the variable ${TEST NAME} gets evaluated by robot framework before being passed to rfswarm via the listener.


### Browser

#### [SeleniumLibrary](https://robotframework.org/SeleniumLibrary/)
For SeleniumLibrary based scripts you will want to use one of the headless browser types as these should use less resources on the agent so this will allow more virtual users per agent machine.

Refer to the [SeleniumLibrary documentation](https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html#Open%20Browser) for the headless browser types, you should run a trial with each type to confirm they work with your application and what the resource cost is for each.

You may also want to consider converting your scripts to run using [Browser Library](https://robotframework-browser.org/), this is not required for using rfswarm but Browser Library does provide features not available in SeleniumLibrary that you may find useful.

#### [Browser Library](https://robotframework-browser.org/)
For Browser Library based scripts you will want to use the headless = True option when calling [Open Browser](https://marketsquare.github.io/robotframework-browser/Browser.html#Open%20Browser).
