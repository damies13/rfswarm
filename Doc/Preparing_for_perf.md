
[Index](Index.md)

## Preparing a test case for performance

Some of the things you will need to consider when taking a functional or regression test and using it for performance are:
- [think time](#think-time)
- [data management](#data-management)

### think time

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


### data management

Because functional and regression tests are designed to test specific functionality, the test data is designed to test boundary or edge cases so are limited to a small set of cases or static. With performance testing we don't want this, rather we want hundreds or even thousands of different data values so we can better emulate user behaviour and ensure we are not constantly hitting a single cached value and reporting unrealistically fast response times.

.
