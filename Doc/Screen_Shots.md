
[Index](Index.md)

## Screen Shots

- [v0.5.0](#v0.5.0)
- [v0.4.4](#v0.4.4)
- [v0.4.3](#v0.4.3)
- [v0.4](#v0.4)
- [v0.3](#v0.3)
- [v0.1](#v0.1)
- [Original](#Original)

### v0.5.0

A simple scenario with 100 robots running the same test case
![Image](Images/Plan_v0.5.0_100u.png)

An example scenario with 2 test groups of 10 robots each running the same test case, the second group starts 420 seconds after the first.
![Image](Images/Plan_v0.5.0_20u_delay_example.png)

A gradual ramp-up scenario (Scalability Test) with 6 test groups of 25 robots each running the same test case, each test group starts 600 seconds (10 minutes) after the previous one, until 150 users are running.
![Image](Images/Plan_v0.5.0_150u_25per10min.png)

An example scenario with 3 test groups each running a different test case, and the second group starts with a 30 second delay.
![Image](Images/Plan_v0.5.0_3tests.png)

Less than a minute into the run starting to get results (new method of gathering results on the agent is working well)
![Image](Images/Run_Start_v0.5.0_39s.png)
![Image](Images/Run_Start_v0.5.0_54s.png)

More than a minute in and getting more results, now getting Standard Deviation and Percentile results.
![Image](Images/Run_Start_v0.5.0_77s.png)
![Image](Images/Run_v0.5.0_100u_6m.png)

2 hours into run, this shows that rfswarm can handle large number of samples well and sustain a run of 100 users over 2 hours
![Image](Images/Run_v0.5.0_98u_2h.png)
![Image](Images/Run_v0.5.0_100u_2h.png)

Run finished sucessfully after 2 hours 20, all robots have stopped.
![Image](Images/Run_Finished_v0.5.0_100u_2h.png)

Clicking the export button (next to stop button) a dialogue gives you the path where the results are stored
![Image](Images/Report_export_v0.5.0.png)

Results export generates 3 csv files:
- test_summary.csv, contains the table in the run screen with the Standard Deviation and Percentile results
- test_agent_data.csv, contains the raw agent status updates, and could be useful for creating a running robots graph.
- test_raw_result.csv, contains the raw result data, and could be useful for creating various graphs.

The sqlite3 database from the test run is also available to enable easy reporting of test results, the db file is retained regardless of clicking the export button or not.
![Image](Images/Results_v0.5.0_100u_2.5hr.png)

Screen shot showing agents when running a test, here you can see one agent is in warning state as memory consumption has exceeded 80%
![Image](Images/Agents_running_v0.5.0.png)

Screen shot showing the prompt to save changes to scenario when closing the application
![Image](Images/Save_prompt_v0.5.0.png)

Screen shot showing a run failing due to an overloaded agent, similarly when the application being tested fails you will see similar error messages with pass or fail counts depending on the library your test uses.
![Image](Images/Run_v0.5.0_crashing_users.png)

Linux Mint 19:
![Image](Images/Linux-v0.5.0_Agents_Ready.png)
![Image](Images/Linux-v0.5.0_Agents_Running.png)
![Image](Images/Linux-v0.5.0_Agents_Stopping.png)
![Image](Images/Linux-v0.5.0_Plan_150u_25per10min.png)
![Image](Images/Linux-v0.5.0_Plan_New.png)
![Image](Images/Linux-v0.5.0_Plan_Save_prompt.png)
![Image](Images/Linux-v0.5.0_Run_6min.png)
![Image](Images/Linux-v0.5.0_Run_Not_Enough_Robots.png)
![Image](Images/Linux-v0.5.0_Run_Report_prompt.png)
![Image](Images/Linux-v0.5.0_Run_Robots_Available.png)
![Image](Images/Linux-v0.5.0_Run_Start_10sec.png)
![Image](Images/Linux-v0.5.0_Run_Start_2min.png)
![Image](Images/Linux-v0.5.0_Run_Start_52sec.png)
![Image](Images/Linux-v0.5.0_Run_percnt_and_stddev.png)
![Image](Images/Linux-v0.5.0_Run_webdriver_fails.png)





### v0.4.4

![Image](Images/Plan_v0.4.4.png)
![Image](Images/Run_Start_v0.4.4.png)
![Image](Images/Run_v0.4.4.png)
![Image](Images/Run_v0.4.4_100u_25min.png)
![Image](Images/Agents_running_v0.4.4.png)

### v0.4.3

![Image](Images/Linux-Plan-v0.4.3.png)
![Image](Images/Linux-Run-v0.4.3-10u1hr.png)
![Image](Images/Linux-Run-v0.4.3-50u1hr.png)
![Image](Images/Linux-Agents-v0.4.3.png)
![Image](Images/Linux-Run-v0.4.3-Overloaded-Agent.png)
![Image](Images/Linux-Agents-v0.4.3-Overloaded-Agents.png)


### v0.4

![Image](Images/Run_v0.4.png "Run - Showing results being collected live")
![Image](Images/Run_Start_v0.4.png "Run - Just Started")

### v0.3

![Image](Images/Plan_unsaved_v0.3.png "Plan - New")
![Image](Images/Plan_saved_opened_v0.3.png "Plan - Planning a performance test")
![Image](Images/Run_v0.3.png "Run - Showing results being collected live")
![Image](Images/Run_Start_v0.3.png "Run - Just Started")
![Image](Images/Agents_ready_v0.3.png "Agents Ready")
![Image](Images/Agents_stopping_v0.3.png "Agents Stopping")

### v0.1

![Image](Images/Plan_v0.1.png "Plan - Planning a performance test")
![Image](Images/Run_v0.1.png "Run - Showing results being collected live")
![Image](Images/Agents_ready_v0.1.png "Agents Ready")
![Image](Images/Agents_running_v0.1.png "Agents Running")

### Original

![Image](Images/Run_Orig.png "Run - Showing results being collected live")
