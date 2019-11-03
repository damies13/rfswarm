
[Index](Index.md)

## Preparing a test case for performance

Some of the things you will need to consider when taking a functional or regression test and using it for performance are:
- [Think Time](#Think-Time)
- [Useful Variables](#Useful-Variables)
- [Data Management](#Data-Management)
- [Browser](#Browser)

### Think Time

Because functional and regression tests are designed to run as a single user and test the functionality as quickly as possible, for performance testing we want to simulate real user behaviour so we want to put some user thinking time or pauses into the script, the easiest way to achieve this would be to simply use the Robot Framework's built in sleep command:

```
	Sleep	30
```

The only issue with this is that it can make the script too regular and cause cadence issues, so just like with other performance testing tools we want to have a variable think time, to do this we can import randint from python's random library to pick a time to sleep between a minimum and maximum value, e.g. 15 and 45.

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
Index should be available through the variable `${index}`, this is the number you see in the Index column at the bottom of the plan screen

#### VUser
VUser should be available through the variable `${vuser}`, referring to the Users column at the bottom of the plan screen, this number is the counter of the user from one to the number in the Users column.
While this number on it's own is not unique, it will be unique relative to the Index above, so if you need a unique string in your test you could combine them. e.g. `${index}_${vuser}`
Another way this could be useful is as a data row offset so that each test user is using data from a different section of your data file.

#### Iteration
Iteration should be available through the variable `${iteration}`, This is simply a counter of how many times this test case has been run for this virtual user. This could be useful if for example you need to walk sequentially through a data file because your data is single use.

### Data Management

#### Reading Data Files

Because functional and regression tests are designed to test specific functionality, the test data is designed to test boundary or edge cases so are limited to a small set of cases or static. With performance testing we don't want this, rather we want hundreds or even thousands of different data values so we can better emulate user behaviour and ensure we are not constantly hitting a single cached value and reporting unrealistically fast response times.

So to make life easier in the [Robot Resources](../Robot_Resources) folder there is a [perftest.resource](../Robot_Resources/perftest.resource) file that you can include in the Settings section of your .robot file like this:

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
	${next_row} = 	Evaluate	${vuser} + ${iteration}
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

### Browser

For SeleniumLibrary based scripts you will want to use one of the headless browser types as these should use less resources on the agent so this will allow more virtual users per agent machine.

Refer to the [SeleniumLibrary documentation](https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html#Open%20Browser) for the headless browser types, you should run a trial with each type to confirm they work with your application and what the resource cost is for each.
