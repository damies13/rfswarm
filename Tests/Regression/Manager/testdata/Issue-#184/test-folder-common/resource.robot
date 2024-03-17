
*** Settings ***


*** Variables ***


*** Keywords ***
Log Vars
  [Documentation]   Log Variables
  Log    RFS_AGENTNAME: ${RFS_AGENTNAME}
  Log    RFS_AGENTVERSION: ${RFS_AGENTVERSION}
  Log    RFS_DEBUGLEVEL: ${RFS_DEBUGLEVEL}
  Log    RFS_EXCLUDELIBRARIES: ${RFS_EXCLUDELIBRARIES}
  Log    RFS_INDEX: ${RFS_INDEX}
  Log    RFS_ITERATION: ${RFS_ITERATION}
  Log    RFS_ROBOT: ${RFS_ROBOT}
  Log    RFS_SWARMMANAGER: ${RFS_SWARMMANAGER}
  Log    SHELL: %{SHELL}
  Log    HOME: %{HOME}
  Log    USER: %{USER}
  Log    DISPLAY: %{DISPLAY}
  Log    PWD: %{PWD}
  # Log    RFS_STATUS: %{RFS_STATUS}

Log Vars Deep
	[Documentation]   Log Variables More
	Log Vars
	Log Vars
	Log Vars


#
