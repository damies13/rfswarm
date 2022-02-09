[Index](README.md)

## rfswarm Reporter

rfswarm Reporter is the reporting tool component, you would use this at some point after the performance test has completed.

- [User Interface](#User-Interface)
	- [Settings Pane](#Settings-Pane)
	- [Preview Pane](#Preview-Pane)
	- [Report Sections](#Report-Sections)
	- [Section Types](#Section-Types)
		- [Heading](#Heading-Section)
		- [Contents](#Contents-Section)
		- [Note](#Note-Section)
		- [Data Graph](#Data-Graph-Section)
		- [Data Table](#Data-Table-Section)
	- [Example Report](#Example-Report)
- [Command Line Interface](#Command-Line-Interface)
- [Install and Setup](#Install-and-Setup)
- [Credits](#Credits)

### User Interface

The initial screen when launching the rfswarm Reporter is the top level report, on the settings pane.
> ![Image](Images/MacOS_Reporter_v1.0.0_Report_Settings.png)

Starting from the top left of the screen we have the main toolbar:

|	|	|	|
|---|---|---|
| Open Result	|	![image](Images/REP_folder_table.gif)	| Select a result folder	|
| New Template	|	![image](Images/REP_page_add.gif)	| Start a new default template	|
| Open Template	|	![image](Images/REP_folder_page.gif)	| Open an existing template	|
| Save Template	|	![image](Images/REP_page_save.gif)	| Save the current template	|
|	|	|	|
| Export HTML	|	![image](Images/REP_page_white_world.gif)	| Generate a html report	|
| Export Word	|	![image](Images/REP_page_word.gif)	| Generate a Word report	|
| Export Excel	|	![image](Images/REP_page_excel.gif)	| Generate an Excel report	|

Under the main toolbar is the section toolbar:
|	|	|	|
|---|---|---|
| Add Section	|	![image](Images/REP_add.gif)	| Opens the add section dialogue	|
| Remove Section	|	![image](Images/REP_delete.gif)	| Removes the currently selected section	|
| Move Section Up	|	![image](Images/REP_resultset_up.gif)	| Moves the currently selected section above the section currently above it	|
| Move Section Down	|	![image](Images/REP_resultset_down.gif)	| Moves the currently selected section below the section currently below it	|

To the right of the section toolbar is the ![image](Images/REP_report.gif) Preview / ![image](Images/REP_cog.gif) Settings toggle, used to switch between the [Settings Pane](#Settings-Pane) and the [Preview Pane](#Preview-Pane) (pictured below)

#### Settings Pane

When Report is selected, the settings pane will display settings the global report settings. when any other section is selected the settings pane will display settings specific to the selected section.

##### Global Report Settings

> ![Image](Images/MacOS_Reporter_v1.0.0_Report_Settings.png)

|	|	|
|---|---|
| Title | If no template is selected the title will try to get the scenario name from the test result otherwise it will take the title that was set in the template.  |
| Date Format | Here you can select the date format you wish to use in the report (defaults to yyyy-mm-dd) |
| Time Format | Here you can select the time format you wish to use in the report (defaults to HH:MM) |
| Time Zone | Times in rfswarm are stored using epoch time also known as unix timestamp, as such all times are UTC with no timezone offset. To display the expected times rfswram Reporter needs to know the timeszone to apply to the timestamp. This should default to the timezone of your local machine, however you may want to display times in your report for another timezone. |
| Start Time | This value is extracted from the results database, to display it on the title page, enable the checkbox in the display column |
| End Time | This value is extracted from the results database, to display it on the title page, enable the checkbox in the display column |
| Logo Image | This setting lets you add a picture to the title page of your report, typically this would be your organisation's logo, but it can be anything you want. the field is read only but will show the file name of the file you selected. Click the ![image](Images/REP_picture.gif)Select Picture button and browse to the image you want to use. Then enable the checkbox in the display column |
| Font | This setting allows you to choose the font and font size to be used throughout the report. Headings and titles use the same font however the font size will be scaled proportionally to the base font size. |
| Highlight Colour | This setting allows you to choose a colour for headings and column headings, Click the ![image](Images/REP_color_swatch.gif)Colour Swatch button next to the colour preview to bring up the system colour picker and choose a colour. For best results choose the colour that matches your organisation's branding. |
| Percentile | This setting allows the percentile value used throughout the report, it defaults to 90%. |


#### Preview Pane
When Report is selected, the preview pane will display a preview of the entire report.
> ![Image](Images/MacOS_Reporter_v1.0.0_Report_Preview.png)

When any other section is selected the preview pane will display a preview of the currently selected section and any subsections.
> ![Image](Images/MacOS_Reporter_v1.0.0_Template_Preview.png)

#### Report Sections
To Add a new Section
- first select Report, then click the ![image](Images/REP_add.gif)add section button
- A dialogue will appear where you can enter the section name, enter the section name and click OK.

> _you can change this name at anytime if you need to, so don't worry too much about getting the perfect name._

> ![Image](Images/MacOS_Reporter_v1.0.0_NewSection.png)

Likewise if you want to add a subsection;
- Select the section that will be the parent
> ![Image](Images/MacOS_Reporter_v1.0.0_SectionSelect.png)

- Then click the ![image](Images/REP_add.gif)add section button and enter the name of the new sub section.
> ![Image](Images/MacOS_Reporter_v1.0.0_NewSubSection.png)

You can then click the `>` beside the section name to expand it and show the sub sections. Click the `V` beside the section name to minimise it again.
> ![Image](Images/MacOS_Reporter_v1.0.0_SectionExpand.png)

To remove a section or subsection, select it than click the ![image](Images/REP_delete.gif)Remove Section button

To move a section up:
- Select the section that you want to move
> ![Image](Images/MacOS_Reporter_v1.0.0_SubSectionSelect3.png)

- Click the ![image](Images/REP_resultset_up.gif)Move Up button
> ![Image](Images/MacOS_Reporter_v1.0.0_SubSectionMoveUp.png)

To move a section down:
- Select the section that you want to move
> ![Image](Images/MacOS_Reporter_v1.0.0_SubSectionSelect1.png)

- Click the ![image](Images/REP_resultset_down.gif)Move Down button
> ![Image](Images/MacOS_Reporter_v1.0.0_SubSectionMoveDown.png)

#### Section Types
> ![Image](Images/MacOS_Reporter_v1.0.0_SectionTypes.png)

Each section is used to display different types of information, the various section types are:
- [Heading](#Heading-Section)
- [Contents](#Contents-Section)
- [Note](#Note-Section)
- [Data Graph](#Data-Graph-Section)
- [Data Table](#Data-Table-Section)

##### Heading Section
The heading section is used for grouping subsections that contain related information, so the only setting here is the heading name which allows you to change the name of the section.

> _top level sections automatically get a page break before them in word reports and a new tab in excel reports._

> ![Image](Images/MacOS_Reporter_v1.0.0_Heading_Settings.png)

##### Contents Section
The contents section is used for adding contents to a report.
> ![Image](Images/MacOS_Reporter_v1.0.0_Contents_Settings.png)

Typically this would be a "Table of contents", however you can also choose a "Table of Graphs" or "Table of Tables" where that adds value to your report.
> ![Image](Images/MacOS_Reporter_v1.0.0_Contents_Settings_Mode.png)

Additionally you can control how many levels of subsections are displayed in the contents, this defaults to 1, which will only show top level sections, however you can select up to 6 levels if needed.
> ![Image](Images/MacOS_Reporter_v1.0.0_Contents_Settings_Level.png)

##### Note Section
The note section is used for adding free text sections to your report, some examples of what you might use this for are:
- An Executive Summary
- A description of the test
- A conclusion to the test results
- Observations relating to specific graphs or table of results
> ![Image](Images/MacOS_Reporter_v1.0.0_Template_Settings.png)

##### Data Graph Section
The data graph section is used for displaying graphs of test results and other metrics collected during the test.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Settings.png)
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Settings_Type.png)

The data sources for the graphs can be:
- [Metric](#Data-Graph-Metric)
- [Result](#Data-Graph-Result)
- [Custom SQL](#Data-Graph-SQL)

###### Data Graph Metric
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Metric.png)

**Number value** - All metrics are stored in the results database as strings, if you want rfswarm Reporter to treat the metric value as a numeric check this check box

**Metric Type** - This option list is auto generated based on the metric types in the results, the types, Agent, Scenario and Summary will always be in the list as these are created by rfswarm Manager, Other custom types you add will also show here.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Metric_Type.png)

**Primary Metric** - This option list is auto generated based on the primary metrics in the results, it will be updated with a filtered set based on the metric types selection
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Metric_Primary.png)

**Secondary Metric** - This option list is auto generated based on the secondary metrics in the results, it will be updated with a filtered set based on the metric types or primary metrics selections.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Metric_Secondary.png)

###### Data Graph Result
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Result.png)

**Result Type** - This option lets you choose between the Response Time, TPS or Total TPS.
|	|	|
|---|---|
| Response Time | The time the keyword took, as measured by robot framework and then reported back to the Manager by the Agent |
| TPS (Transactions per Second) | Simply a count of the number of times each keyword recorded a result in any given second. |
| Total TPS | Simply a count of the number of times all keywords recorded a result in any given second. |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Result_Type.png)

**Filter Result** - This option lets you choose between the None, Pass or Fail.
|	|	|
|---|---|
| None | Does not filter results (shows all) |
| Pass | Filters the results to only show when a keyword returned a pass state |
| Fail | Filters the results to only show when a keyword returned a fail state |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Result_FilterResult.png)

**Filter Type** - This option is used in with **Filter Pattern**, if the Filter Type is None, then Filter Pattern is ignored, otherwise Filter Pattern is used to filter the results shown.
| Filter Type | Filter Pattern | Result |
|---|---|---|
| None |  | Filter Pattern is ignored |
| Wildcard (Unix Glob) | \*abc\* | Only results that contain 'abc' will be shown |
| Not Wildcard (Unix Glob) | \*abc\* | Results that contain 'abc' will not be shown, all other results will be shown |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_Result_FilterType.png)

###### Data Graph SQL
The SQL option allows you to write your own SQL statement to produce graphs that couldn't be produced with the other options.

This option is intended as an option of last resort or as a stop gap while waiting for a feature to be implemented.

It's recommended to use a sqlite client to test out your sql statements before putting them into here.

When constructing the SQL for graphs, it's important to note that the column names should be named as "Time", "Value" and "Name" in that order.
|	|	|
|---|---|
| Time | Should return an epoch time value, this will be displayed on the x axis |
| Value | Should return a numeric value, this will be displayed on the y axis |
| Name | Should return a string value, this used to give a unique colour to the line, it will also be used to match the colour with the first data column in a Data Table |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataGraph_SQL.png)

##### Data Table Section
The data table section is used for displaying tables of test results and other metrics collected during the test.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Settings.png)

**Show graph colours** - When enabled will display a colour swatch in the first column of the table that matches the first data column to the matching data value on a related graph, this is useful for creating legend tables.

> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Settings_Type.png)

The data sources for the graphs can be:
- [Metric](#Data-Table-Metric)
- [Result](#Data-Table-Result)
- [ResultSummary](#Data-Table-ResultSummary)
- [Custom SQL](#Data-Table-SQL)

###### Data Table Metric
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Metric.png)

**Number value** - All metrics are stored in the results database as strings, if you want rfswarm Reporter to treat the metric value as a numeric check this check box
**Show counts** - Use this checkbox if you want a count of the number of times this metric was recorded (do not use with number value)

**Metric Type** - This option list is auto generated based on the metric types in the results, the types, Agent, Scenario and Summary will always be in the list as these are created by rfswarm Manager, Other custom types you add will also show here.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Metric_Type.png)

**Primary Metric** - This option list is auto generated based on the primary metrics in the results, it will be updated with a filtered set based on the metric types selection
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Metric_Primary.png)

**Secondary Metric** - This option list is auto generated based on the secondary metrics in the results, it will be updated with a filtered set based on the metric types or primary metrics selections.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Metric_Secondary.png)

###### Data Table Result
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Result.png)

**Result Type** - This option lets you choose between the Response Time, TPS or Total TPS.
|	|	|
|---|---|
| Response Time | The time the keyword took, as measured by robot framework and then reported back to the Manager by the Agent |
| TPS (Transactions per Second) | Simply a count of the number of times each keyword recorded a result in any given second. |
| Total TPS | Simply a count of the number of times all keywords recorded a result in any given second. |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Result_Type.png)

**Filter Result** - This option lets you choose between the None, Pass or Fail.
|	|	|
|---|---|
| None | Does not filter results (shows all) |
| Pass | Filters the results to only show when a keyword returned a pass state |
| Fail | Filters the results to only show when a keyword returned a fail state |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Result_FilterResult.png)

**Filter Type** - This option is used in with **Filter Pattern**, if the Filter Type is None, then Filter Pattern is ignored, otherwise Filter Pattern is used to filter the results shown.
| Filter Type | Filter Pattern | Result |
|---|---|---|
| None |  | Filter Pattern is ignored |
| Wildcard (Unix Glob) | \*abc\* | Only results that contain 'abc' will be shown |
| Not Wildcard (Unix Glob) | \*abc\* | Results that contain 'abc' will not be shown, all other results will be shown |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_Result_FilterType.png)

###### Data Table ResultSummary
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_ResultSummary.png)

**Filter Type** - This option is used in with **Filter Pattern**, if the Filter Type is None, then Filter Pattern is ignored, otherwise Filter Pattern is used to filter the results shown.
| Filter Type | Filter Pattern | Result |
|---|---|---|
| None |  | Filter Pattern is ignored |
| Wildcard (Unix Glob) | \*abc\* | Only results that contain 'abc' will be shown |
| Not Wildcard (Unix Glob) | \*abc\* | Results that contain 'abc' will not be shown, all other results will be shown |
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_ResultSummary_FilterType.png)

###### Data Table SQL
The SQL option allows you to write your own SQL statement to produce graphs that couldn't be produced with the other options.

This option is intended as an option of last resort or as a stop gap while waiting for a feature to be implemented.

It's recommended to use a sqlite client to test out your sql statements before putting them into here.

When constructing the SQL for graphs, it's important to note that the column names will be used as the table headings, so it's recommended in your SELECT statement to use `as 'Heading Name'` to control the headings.

Also note that **Show graph colours** will use values of the first data column to match the colours for each table row to the line colours on a graph.
> ![Image](Images/MacOS_Reporter_v1.0.0_DataTable_SQL.png)

#### Example Report
This is an example of a template you could create and use for reporting your test results. It shows some of the capabilities of the reporting tool.
> ![Image](Images/MacOS_Reporter_v1.0.0_Example_Report.png)

|  |  |  |
|---|---|---|
| [HTML](Images/Example_20210214_204637_browseOC100.html) | [Word](Images/Example_20210214_204637_browseOC100.docx) | [Excel](Images/Example_20210214_204637_browseOC100.xlsx) |
| You will need to use the "copy raw contents" button and save to a .html file to see this report  | You need to click the Download button to see this report | You need to click the Download button to see this report |


### Command Line Interface

These command line options allow you to override the ini file configuration but do not update the ini file. The inclusion of the nogui option also allows for inclusion in CI/CD pipelines.

Additionally the debug (-g) levels 1-3 will give extra information on the console useful for troubleshooting your environment. debug levels above 5 are more for debugging the code and get very noisy so are not recommended for normal use.

```
$ rfswarm-reporter -h
Robot Framework Swarm: Reporter
	Version 1.0.0
usage: rfswarm_reporter.py [-h] [-g DEBUG] [-v] [-i INI] [-n] [-d DIR] [-t TEMPLATE] [--html] [--docx] [--xlsx]

optional arguments:
  -h, --help            show this help message and exit
  -g DEBUG, --debug DEBUG
                        Set debug level, default level is 0
  -v, --version         Display the version and exit
  -i INI, --ini INI     path to alternate ini file
  -n, --nogui           Don't display the GUI
  -d DIR, --dir DIR     Results directory
  -t TEMPLATE, --template TEMPLATE
                        Specify the template
  --html                Generate a HTML report
  --docx                Generate a MS Word report
  --xlsx                Generate a MS Excel report
```

If you pass in an unsupported command line option, you will get this prompt:
```
$ rfswarm-reporter -?
Robot Framework Swarm: Reporter
	Version 1.0.0
usage: rfswarm_reporter.py [-h] [-g DEBUG] [-v] [-i INI] [-n] [-d DIR] [-t TEMPLATE] [--html] [--docx] [--xlsx]
rfswarm-reporter: error: unrecognized arguments: -?
```

### Install and Setup

#### 1. Install
##### 1.1 Prerequisites
- The Reporter machine needs to use a minimum of Python 3.9
- tkinter may need to be installed, or it may already installed on your system, if it's not installed consult the [python documentation](https://tkdocs.com/tutorial/install.html) on how to install for your system.

On Debian based systems this will probably work
```
apt install python3-tk
```

##### 1.2 Install

Once you have the prerequisites sorted, the installation is simply
```
pip* install rfswarm-reporter
```

\*some systems might need you to use pip3 and or sudo


#### 3. Run the Reporter

```
rfswarm-reporter
```

#### 4. Manual Install the prerequisites

- The Manager machine needs to use a minimum of Python 3.9
- tkinter may need to be installed, or it may already installed on your system, if it's not installed consult the [python documentation](https://tkdocs.com/tutorial/install.html) on how to install for your system.

On Debian based systems this will probably work
```
apt install python3-tk
```

Additionally the following pip command might be needed if these are not already installed on your system:
```
pip* install configparser pillow matplotlib python-docx openpyxl tzlocal>=4.1
```

\*some systems might need you to use pip3 and or sudo

#### 5. Manual Run the Manager

Use this method if you did not install using pip

```
python* rfswarm_reporter.py
```
\*or python3 on some systems


### Credits

The icons used for the buttons in the Manager GUI were derived from the Creative Commons licensed (Silk icon set 1.3)[http://www.famfamfam.com/lab/icons/silk/]
