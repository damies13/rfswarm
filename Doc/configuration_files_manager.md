# Configuration files for Manager
[Return to Index](README.md)

1. [Configuration File](#configuration-file)
1. [Scenario File](#scenario-file)

## Configuration File
The configuration File is the default configuration file format for the Manager and is created when the Manager is launched for the first time or when the Manager cannot find it in the default directory.

**Example default RFSwarmManager.ini file:**
```ini
[GUI]
win_width = 800
win_height = 350
graph_list =
donation_reminder = 1746482031

[Plan]
scriptdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
scenariodir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
scenariofile =

[Run]
resultsdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager\results
display_index = False
display_iteration = False
display_sequence = False
display_percentile = 90

[Server]
bindip =
bindport = 8138
```

### [GUI]
All of the settings that are related to user interface are under the GUI section heading.

#### Window Width
The window width setting defines the width of the main Manager window. This setting is mainly used to reopen the Manager window in the state in which it was closed, you can use this setting to control width manually.
```ini
win_width = 800
```

#### Window Height
The window height setting defines the height of the main Manager window. This setting is mainly used to reopen the Manager window in the state in which it was closed, you can use this setting to control height manually.
```ini
win_height = 350
```

#### Configuration File Graph List
The graph list setting is used to save graph IDs that have been created by the user in the Manager via: "Graph" > "New Graph Window". These graphs are saved in the configuration file when a new graph is created, and their order is reproduced here.
This setting is used by the Manager to give the user the ability to reopen these graphs via: "Graph" > "Recent" without having to save them in the scenario file.
```ini
graph_list = 681933ac-1,68193880-2
```

#### Donation Reminder
This setting is only used by the Manager to control donation reminders .
```ini
donation_reminder = 1746482031
```

### [Plan]
All of the settings that are related to planning in the Manager are under the Plan section heading.

#### Script Directory
This setting defines the default path that the created tests/tasks groups in Manager "Plan" menu will refer to and create relative paths to them. This setting is necessary so that the Manager can find these files and be consistent in determining them.
```ini
scriptdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
```

#### Scenario Directory
This setting defines the default path for scenario files which will be shown when saving or opening scenarios.
```ini
scenariodir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
```

#### Manager Scenario File
The scenario file setting specifies the path to the scenario file which will be opened in the Manager at the opening of the application.
```ini
scenariofile = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager\this-is-my-scenario.rfs
```

### [Run]
All of the settings that are responsible for the Manager's behaviour during the run in the Manager are under the Run section heading.

#### Result Directory
The result directory is the location where Manger will save collected results from performance test.
```ini
resultsdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager\results
```

#### Display Index
This setting determines whether to display results separated based on the individual test cases.
```ini
display_index = False
```

#### Display Iteration
This setting determines whether to display results separated based on the test iteration.
```ini
display_iteration = False
```

#### Display Sequence
This setting determines whether to display results separated based on the sequence within the test case.
```ini
display_sequence = False
```

#### Display Percentile
The display percentile sets which percentile will be included in the run. Specifies the percentage of requests which were completed in a time equal to or less than the achieved value.
```ini
display_percentile = 95
```

### [Server]
All of the settings that are related to the network connectivity of the Manager are under the Server section heading.

#### Bind IP Address
The bind ip address specify the IP address that Manager will listen and send requests. This setting is really useful if the machine has multiple network interfaces.
For more information follow: [rfswarm Manager: bind ip address](rfswarm_manager.md#bind-ip-address)
```ini
bindip = 192.168.0.99
```

#### Bind Port
The bind port setting is used for changing Manger port.
For more information follow: [rfswarm Manager: bind port number](rfswarm_manager.md#bind-port-number)
```ini
bindport = 8138
```

### [Monitoring]

#### Monitoring Script Directory
This setting defines the default path that the created tests/tasks groups in Manager "Monitoring" menu will refer to and create relative paths to them. This setting is necessary so that the Manager can find these files and be consistent in determining them.
```ini
scriptdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
```

## Scenario File
This file is used to save the configuration of the scenario that will be executed by the Manager to perform a personalised test. This file is created after saving it in the Manager and contains the settings that the user has set up.
This file can later be reopened in the Manager in order to recreate configuration.
The extension of this file is: .rfs
**Example scenario file:**
```ini
[Scenario]
uploadmode = err
scriptcount = 2
monitortimebefore = 60
monitortimeafter = 120
monitorcount = 1
graphlist =

[Script Defaults]
resultnamemode = doco
excludelibraries = BuiltIn,String,OperatingSystem,perftest
testrepeater = True
injectsleepenabled = True
disableloglog = True
disablelogoutput = True
robotoptions = -v "var1:123"

[1]
robots = 8
delay = 10
rampup = 30
run = 320
test = Test1
script = ..\..\..\..\performance_tests.robot

[2]
robots = 3
delay = 0
rampup = 40
run = 600
test = Test2
script = ..\..\..\..\performance_tests.robot

[m1]
robots = 1
delay = 0
rampup = 0
run = 0
test = Basic Data
script = ..\..\..\..\rfswarm\Tests\Monitor_Basic.robot
```

### [Scenario]
In this section heading you will find the settings for the general structure and flow of the test that you want to perform.

#### Upload Mode
This setting determines the way in which files will be transferred from the Agent to the Manager. The options are: def (All Deferred), err (On Error Only), imm (Immediately).
For more information follow: [rfswarm Manager: settings for the scenario](rfswarm_manager.md#settings-for-the-scenario-and-rfswarm-image)
```ini
uploadmode = err
```

#### Script Count
This setting describes the number of created script indices in the Manager "Plan" screen. This number must match the actual number of tests/tasks groups that were configured and should be edited with care.
```ini
scriptcount = 2
```

#### Monitor Time Before
This setting is not visible by default in the Manager's configuration file and must be configured via the Manager's "Monitor" menu screen once configured, this option will appear.
This setting determines the monitoring time before the tests start and is given in seconds. For more information follow: [rfswarm Manager: monitoring](rfswarm_manager.md#monitoring)
```ini
monitortimebefore = 60
```

#### Monitor Time After
This setting is not visible by default in the Manager's configuration file and must be configured via the Manager's "Monitor" menu screen. Once configured, this option will appear.
This setting determines the post-test monitoring time and is given in seconds. For more information follow: [rfswarm Manager: monitoring](rfswarm_manager.md#monitoring)
```ini
monitortimeafter = 120
```

#### Monitor Count
This setting is not visible by default in the Manager's configuration file and must be configured via the Manager's "Monitor" menu screen. Once configured, this option will appear.
This setting describes the number of created monitoring script indices in the Manager "Monitor" screen. This number must match the actual number of monitoring tests/tasks groups that were configured and should be edited with care.
```ini
monitorcount = 3
```

#### Scenario Graph List
This setting is not visible by default in the Manager's scenario file and will appear after saving the scenario file when at least one graph was open before the Manager was closed.
These graphs settings are saved in the scenario file, and their order is reproduced here. This setting is used by the Manager to give the user the ability to reopen these graphs via: "Graph" > "Scenario".
```ini
graphlist = 68193c4e-1
```

### [Script Defaults]
In this section heading you will find the global scenario settings that are applied to all settings.
This section header is **not visible in the scenario file by default**, as it contains the global settings for the Manager and will appear if the default global settings are changed in any way.
For more information about settings under this section heading follow: [rfswarm Manager: scenario settings](rfswarm_manager.md#scenario-settings)

#### Result Name Mode
This setting defines response times named in the test results.
The possible values are: doco (Documentation), info (Information), kywrd (Keyword), kywrdargs (Keyword & Arguments)
If "Default" option is set up, this setting is deleted from configuration file.
```ini
resultnamemode = doco
```

#### Exclude Libraries
This setting determines which libraries are excludes from reporting in the test results.
```ini
excludelibraries = BuiltIn,String,OperatingSystem,perftest,DateTime
```

#### Test Repeater
Determines whether the test repeater is enabled or not.
```ini
testrepeater = True
```

#### Inject Sleep
This setting appears when the inject sleep is enabled in the Manager settings. By default there is only the setting: ‘injectsleepenable’, but if times are set other than the default, they are also saved here.
```ini
injectsleepenabled = True
injectsleepminimum = 10
injectsleepmaximum = 50
```

#### Disable Log
These settings specify which logs manager will disable when saving results from running tests in the result directory and which not.
```ini
disableloglog = True
disablelogreport = True
disablelogoutput = False
```

#### Robot Options
Robot Options setting is used for saving additional command-line options to the robot executable.
```ini
robotoptions = -v "var1:123"
```

### [plan_index]
The header of the plan index section represents the created test group in the "Plan" menu of the Manager and has its index value, for example: [1] or [2] and so on.
There can theoretically be an unlimited number of these sections. They should be numbered from 1 to the number of indices defined in the [Scenario] section. This heading contains settings about the test group in question.
For more information follow: [rfswarm Manager: plan](rfswarm_manager.md#plan)

#### Robots
The robots setting is the number of robots (virtual users) you are planning to run in the scenario for this ([plan_index]) test group that this setting is under.
```ini
robots = 125
```

#### Delay
The delay setting is the amount of time in seconds to wait before starting Ramp Up.
```ini
delay = 180
```

#### Ramp Up
The ramp up setting is the amount of seconds the Manager has to get from 0 virtual users (robots) to the number of virtual users (robots) defined in the Robots.
```ini
rampup = 1800
```

#### Run
The ramp up setting is the amount of seconds to keep all the virtual users (robots) defined in the Robots running after Ramp Up has finished.
```ini
run = 4515
```

#### Test
The test setting is selected test you want to run for this ([plan_index]) test group.
```ini
test = Send Requests To Site
```

#### Script
The script setting is selected robot file that contains the test you want to assign to this ([plan_index]) test group.
```ini
script = ..\..\..\..\performance_tests.robot
```

### [monitoring_index]
The header of the monitoring index section represents the created test group in the "Monitoring" menu of the Manager and has its index value, for example: [m1] or [m2] and so on.
There can theoretically be an unlimited number of these sections.
This section has the same settings as [plan_index] section, but the difference is it that it has the different purpose.
For more information follow: [rfswarm Manager: monitoring](rfswarm_manager.md#monitoring)

## Common Sections
These sections are used in all the previously mentioned configuration files.

### [graph_id]
The header of the graph ID contains settings that are related to the graph window and it's configuration. The name of the section is actually the ID of the graph, for example: [68193c4e-1] or [68193c4e-2] and so on.
There can theoretically be an unlimited number of these sections.
For more information follow: [rfswarm Manager: monitoring](rfswarm_manager.md#graphs)

#### ID
The graph ID is made from the epoch time converted to hexadecimal notation and an additional appended number indicating the graph number symbolising the order.
```ini
id = 6819dcc8-1
```

#### Open
The open setting determines whether the graph should be opened on the start of the Manager or not. When true, the chart will be displayed as soon as the manager is launched.
```ini
open = True
```

#### Window Width & Height
These settings have the same purpose as in the GUI section of the configuration file.
```ini
win_width = 761
win_height = 371
```

#### Windows Location x & y
These settings are responsible for reopening the graph in the same place on the screen where it was before the application was closed.
```ini
win_location_x = 494
win_location_y = 295
```

#### Window screen
The windows screen setting is used for placing graph on the screen. It's used for specify at which screen the graph will appear. This setting will ensure that the graph opens on a good screen.
```ini
win_screen = :0.0
```

#### Name
The name setting defines the name of the graph to be displayed in the title of the graph window. This is used to easily navigate and aggregate graphs.
```ini
name = Filter Metric
```

#### Show Settings
This setting determines whether the settings are to be displayed on the graph with plotted data or not.
```ini
show_settings = True
```

#### Show Legend
This setting determines whether a legend of the plotted data is to be displayed on the graph or not.
```ini
show_legend = 1
```

#### Data Type
The data type setting determines which data from the Manager's database is displayed on the graph and the primary metric and secondary metric settings are later selected based on this setting.
```ini
data_type = Metric
```

#### Metric Type
This setting determines the specific type of metric.
```ini
metric_type = Summary
```

#### Primary Metric
This setting determines the specific type of primary metric.
```ini
primary_metric = Clicking link Purchase
```

#### Secondary Metric
This setting determines the specific type of secondary metric.
```ini
secondary_metric = min
```

#### Filter Agent
This setting specifies filtering by saved agent name so that the displayed data in the graph could be only related to that specific agent.
```ini
filter_agent = Browser_Agent_nr_3
```

#### Enable Filter Agent
This setting determines whether data is to be filtered by agent name or not.
```ini
en_filter_agent = 1
```

#### Filter Name
This setting determine if the filter pattern will limit results shown or restrict results from being shown. The possible options are:
- Wildcard (Unix Glob): filter data for a graph by selecting only matching entries.
- Not Wildcard (Unix Glob): excludes specific patterns, ensuring unwanted data is not displayed.
```ini
filter_name = Wildcard (Unix Glob)
```

#### Filter Pattern
This setting is closely linked to the filter_name setting. This setting is used to store the pattern used in the graph, so that the data can be filtered according to the filter_name type used.
```ini
filter_pattern = Click Button *
```

#### Granularity Seconds
This setting is used to specify the length of the window in which data will be smoothed based on the selected granularity type.
```ini
granularity_seconds = 60
```

#### Granularity Type
This setting is used to determine the type of granularity used in the graph to smooth the data plot based on the selected method. The possible types are: Average, Maximum, Minimum.
```ini
granularity_type = Maximum
```
