# Configuration files for Manager
[Return to Index](README.md)

## INI File
The INI file is the default configuration file format for the Manager and is created when the Manager is launched for the first time or when the Manager cannot find it in the default directory.

**Default RFSwarmManager.ini file:**
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
The window height setting defines the height of the main Manager window. This setting is mainly used to reopen the Manager window in the state in which it was closed, you can use this setting to control width manually.
```ini
win_height = 350
```

#### Graph List
The graph list setting is used for saving graphs id's that were created by the user in Manager via: "Graph" > "New Graph Window". These graphs after closing Manager will be saved here in chronological order. This setting is used by Manager to give the user option to reopen these Graph in "Graph" > "Recent".

The graph list setting is used to save graph IDs that have been created by the user in the Manager via: "Graph" > "New Graph Window". These graphs are saved in the configuration file when a new graph is created, and their order is reproduced here. This setting is used by the Manager to give the user the possibility to reopen these graphs via "Graph" > "Recent" without having to save them in the script file.
```ini
graph_list = 681933ac-1,68193880-2
```

### [Plan]
All of the settings that are related to planning in the Manager are under the Plan section heading.

#### Script Directory

```ini
scriptdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
```

#### Scenario Directory

```ini
scenariodir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager
```

#### Scenario File

```ini
scenariofile = 
```

### [Run]
All of the settings that are responsible for the Manager's behaviour during the run in the Manager are under the Run section heading.

#### Result Directory

```ini
resultsdir = C:\rfswarm\venv\Lib\site-packages\rfswarm_manager\results
```

#### Display Index

```ini
display_index = False
```

#### Display Iteration

```ini
display_iteration = False
```

#### Display Sequence

```ini
display_sequence = False
```

#### Display Percentile

```ini
display_percentile = 90
```

### [Server]
All of the settings that are related to the network connectivity of the manager are under the Server section heading.

#### Bind IP Address

```ini
bindip = 
```

#### Bind Port

```ini
bindport = 8138
```

