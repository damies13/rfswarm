
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
	# These environment variables are os specific and don't always work on github actions
  # Log    SHELL: %{SHELL}
  # Log    HOME: %{HOME}
  # Log    USER: %{USER}
  # Log    DISPLAY: %{DISPLAY}
  # Log    PWD: %{PWD}
	# Add environment variables that I can control
	Log    MATRIX_PLATFORM: %{MATRIX_PLATFORM}
	Log    MATRIX_PYTHON: %{MATRIX_PYTHON}
  # Log    RFS_STATUS: %{RFS_STATUS}

Log Vars Deep
	[Documentation]   Log Variables More
	Log Vars
	Log Vars
	Log Vars


#
