# Manager API V2
[Return to Index](README.md)

What's new with the v2 api:
- REST compliant API
- all data can be accessed via the api so that the webui can use this api to render it's data

> [!TIP]
> all the paths below will be relative to `/api/v2`

## for all api end points
GET - returns the values related to the specified path as JSON
- to get the value(s) use GET `/path?<key>`
- to filter by a value use GET `/path?<key>=<value>`, here the value can be a glob pattern

PUT - can be used to update a single value or a small number of values `/path?<key>=<new value>&<key>=<new value>`

POST - can be used with a JSON body to update many values

DELETE - can be used to remove items from the plan and monitoring screens (e.g. test rows)

## `/scenario`

returns/updates the details of the currently loaded scenario / manager

| Key | Detail |
|:--- |:------ |
| scenario 	| The Scenario Name |
| file | The file name |
| path | The full file path |
| time_start | The start time of the scenario |
| time_elapsed | The elapsed time of the scenario |
| time_stop | The time stop button was pressed |
| time_abort | The time abort (stop now) button was pressed |
| time_end | The finish time of the scenario |
| csv | True if the generate csv files button was pressed |
| robots | The number of runnung robots |
| monitoring | The number of runnung monitoring robots |
| version | The manager version (read only) |
| variables | A list of Scenario variables to pass from the manager to the agent (e.g. Environment variables) |
| var_name | Scenario variable's name |
| var_type | Scenario variable's type (path, value, etc) |
| var_value | Scenario variable's value |

### `/scenario/settings`

returns/updates the currently loaded scenario's global settings

to get settings related to a specific pane you can use `/scenario/settings/<pane>`, likewise to set settings by put to a specific pane use `/scenario/settings/<pane>?<key>=<new value>`

| Pane | Key | Detail |
|:---- |:--- |:------ |
| scenario | upload	| Upload Logs |
| scenario | index	| Show run results grouped by robot index (boolean) |
| scenario | iteration	| Show run results grouped by iteration number (boolean) |
| scenario | sequence	| Show run results grouped by sequence number (boolean) |
| scenario | percentile	| Run results  |
| test_defaults | name_mode	| Result Name Mode |
| test_defaults | exclude	| Exclude Libraries |
| test_defaults | options	| Robot comandline options |
| test_defaults | test_time	| Include Test Time |
| test_defaults | repeater	| Test Repeater |
| test_defaults | sleep_inject	| Inject Sleep |
| test_defaults | sleep_min	| Inject Sleep Minimum |
| test_defaults | sleep_max	| Inject Sleep Maximum |
| test_defaults | sleep_exclude	| Exclude Sleep |
| test_defaults | pacing_time	| Apply Pacing Time |
| test_defaults | pacing_from	| Apply Pacing From (Start/End) |
| test_defaults | log_html	| Disable log.html |
| test_defaults | report_html	| Disable report.html |
| test_defaults | output_xml	| Disable output.xml |
| manager | bind_ip	| Bind IP Address |
| manager | bind_port	| Bind Port Number |
| manager | results	| Results location |

### `/scenario/plan`

returns/updates the details of the currently loaded scenario's plan screen

| Key | Detail |
|:--- |:------ |
| rows 	| The number of rows in the plan |
| schedule_start | Whether the Sheduled Start is enabled or not (boolean value) |
| schedule_time | The Sheduled Start time (epoch time) |

### `/scenario/plan/<index>`

returns/updates the details of a specific test rown within the currently loaded scenario's plan screen

| Key | Detail |
|:--- |:------ |
| index | The test row index number (read only?) |
| robots | The number of robots |
| delay | The number of robots |
| rampup | The number of robots |
| run | The number of robots |
| file | The number of robots |
| test | The number of robots |
| file | The number of robots |
| name_mode	| Result Name Mode |
| exclude	| Exclude Libraries |
| options	| Robot comandline options |
| test_time	| Include Test Time |
| repeater	| Test Repeater |
| sleep_inject	| Inject Sleep |
| sleep_min	| Inject Sleep Minimum |
| sleep_max	| Inject Sleep Maximum |
| sleep_exclude	| Exclude Sleep |
| pacing_time	| Apply Pacing Time |
| pacing_from	| Apply Pacing From (Start/End) |
| log_html	| Disable log.html |
| report_html	| Disable report.html |
| output_xml	| Disable output.xml |

### `/scenario/plan/<filter index>`

| Key | Detail |
|:--- |:------ |
| index | The Agent Filter index number (read only?) |
| require	| Required (Boolean) False = Exclude |
| value	| The Agent Filder Value |

### `/scenario/monitoring`

returns/updates the details of the currently loaded scenario's monitoring screen

| Key | Detail |
|:--- |:------ |
| rows 	| The number of rows in the plan |
| time_before | The monitoring time before the test starts |
| time_after | The monitoring time after the test ends |

### `/scenario/monitoring/<index>`

returns/updates the details of a specific test rown within the currently loaded scenario's monitoring screen

| Key | Detail |
|:--- |:------ |
| index | The test row index number (read only?) |
| robots | The number of robots |
| delay | The number of robots |
| rampup | The number of robots |
| run | The number of robots |
| file | The number of robots |
| test | The number of robots |
| file | The number of robots |
| name_mode	| Result Name Mode |
| exclude	| Exclude Libraries |
| options	| Robot comandline options |
| test_time	| Include Test Time |
| repeater	| Test Repeater |
| sleep_inject	| Inject Sleep |
| sleep_min	| Inject Sleep Minimum |
| sleep_max	| Inject Sleep Maximum |
| sleep_exclude	| Exclude Sleep |
| pacing_time	| Apply Pacing Time |
| pacing_from	| Apply Pacing From (Start/End) |
| log_html	| Disable log.html |
| report_html	| Disable report.html |
| output_xml	| Disable output.xml |

### `/scenario/monitoring/<filter index>`

| Key | Detail |
|:--- |:------ |
| index | The Agent Filter index number (read only?) |
| require	| Required (Boolean) False = Exclude |
| value	| The Agent Filder Value |


## `/agent`

returns/updates the list of agents connected to the manager

| Key | Detail |
|:--- |:------ |
| name | The Agent's Name |
| status | The Agent's status |
| last_seen | The last ime the Agent updated the manager |
| robots | The number of running robots |
| robots_assigned | The number of robots assigned |
| monitor | The number of running monitor robots |
| monitor_assigned | The number of monitor robots assigned |
| load | The Agent's load (we need to rename this #435) |
| %CPU | The Agent's Percentage CPU Usage |
| %MEM | The Agent's Percentage Memory Usage |
| %NET | The Agent's Percentage Network Usage |
| version | The Agent's version number |
| libraries | The list of robot framework libraries installed on the Agent |

## `/agent/<agent name>`

returns/updates the details of a specific agent

Same keys as above?

## `/jobs`

returns/updates the list of robot jobs for the scenario with the assigned to agents

| Key | Detail |
|:--- |:------ |
| id | The Jobs's ID assigned when it was created |
| status | the current status of the job |
| iteration | the current iteration of the job |
| hash | the robot file hash |
| test | the robot test name |
| time_start | The start time of the job |
| time_end | The finish time of the job |

### `/jobs/<id>`

returns/updates the details of a specific job assigned 

Same keys as above?

## `/graph`

returns/updates the list of graphs for this scenario

| Key | Detail |
|:--- |:------ |
| id | The graph's ID |
| name | The graph's Name |

### `/graph/<graph_id>`

returns/updates the settings of a specific graph

| Key | Detail |
|:--- |:------ |
| id | The graph's ID |
| name | The graph's Name |
| name | The graph's Name |
| name | The graph's Name |
| name | The graph's Name |
| name | The graph's Name |
| name | The graph's Name |


## `/table`

returns/updates the list of tables for this scenario

| Key | Detail |
|:--- |:------ |
| id | The table's ID |
| name | The table's Name |

### `/table/<table_id>`

returns/updates the settings of a specific table

## `/result`

returns/updates the result data 

| Key | Detail |
|:--- |:------ |
| agent | The agent name |
| name | The result name |
| result | The result (PASS/FAIL) |
| time_elapsed | The result keyword's elapsed time |
| time_start | The result keyword's start time |
| time_end | The result keyword's end time |
| index | The the scenario row index |
| robot | The Job/Robot number |
| iteration | The iteration number, i.e. the number of times this robot has run this test case |
| sequence | The sequence number of this keyword/result withing this iteration of the test case |

## `/metric`

returns/updates the metric data 

| Key | Detail |
|:--- |:------ |
| agent | The agent name |
| metric_type | The Metric Type |
| time | The Metric Time |
| metric_primary | The Primary Metric |
| metric_secondary | The Secondary Metric |
| metric_value | The Metric Value |
| metrics | A list of Secondary Metric and Value pairs (optional) |

## `/file`

returns a file list

When using GET: 
- if no filter is used a list of scenario files and hashes are returned
- if an extention filter is used a list of scenario files and hashes are returned
- if an extention filter and path that is a directory is given a list of files and directories is returned for the file browser dialogue
- if a path filter that is a file is given a the file's details, hash, relative dir, file name, etc

| Key | Detail |
|:--- |:------ |
| path | file's relative path |
| extention | file extention filter |
| hash | file hash |

### `/file/<file_hash>`

used for uploading / downloading file data

| Key | Detail |
|:--- |:------ |
| path | file's relative path |
| hash | file hash |
| encoding | file compression or encoding, if multople are used, delimited by commas, in the order to be used to decode the file |
| data | The file's data |

By default in v2 the file data will contain a string that is a base64 encoded lzma (7zip) compressed version of the file, the same as with earlier versions of RFSwarm. The agent will base64 decode the string, lzma decompress, then save to a file using the relative file path above relative to the agents temp directory.

The inclusion of the encoding field allows us to change this in future versions, e.g.
- possobly sending raw file data for some file types, as we have seen in the past that compressing the file maxed out the cpu on the agents and took longer than sending the raw files over the local lan would have taken
- possibly haveing a configuration option to allow the user to choose.

## `/messages`

returns info messages (e.g. status bar messages)

| Key | Detail |
|:--- |:------ |
| current | the current message to show on the status bar |
| type | error, warning, info, debug |
| text | the message text |
| messages | a list of messages  |
