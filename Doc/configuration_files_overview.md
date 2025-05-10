# RFSwarm Configuration files Overview
[Return to Index](README.md)
1. [Overview](#overview)
1. [Agent configuration](configuration_files_agent.md)
	1. [Agent Configuration File](configuration_files_agent.md#configuration-file)
1. [Manager configuration](configuration_files_manager.md)
	1. [Manager Configuration File](configuration_files_manager.md#configuration-file)
	1. [Scenario File](configuration_files_manager.md#scenario-file)
1. [Reporter configuration](configuration_files_reporter.md)
	1. [Reporter Configuration File](configuration_files_reporter.md#configuration-file)
	1. [Template File](configuration_files_reporter.md#template-file)

## Overview

Since the initial version of RFSwarm the configuration files have by design always been plain text using python's [configparser](https://docs.python.org/3/library/configparser.html) module, these files follow the standard ini file format that is well known and familiar to many IT people.

The intention was that if you created a scenario file or report template you could easily check this file into a version control system and any changes made to your test scenarios or report templates would be easily managed by the version control system.

An unexpected benefit of this design is that some RFSwarm users dynamically generate their scenario file or report template in their CI build process, and others just manually construct their scenario file or report template and check it in without using the RFSwarm GUI at all.

Prior to RFSawrm version 1.5.0 only this ini file format is supported.

With RFSawrm version 1.5.0 in addition to the ini file format, Yaml and JSON file formats are now also supported. The ini file format will remain the default, however it's now possible to save your scenario and report template files in these new formats and use them with RFSwarm.

The documentation links above detail the the ini file format, what the section names are and the possible option and values within each section. If you wish to construct a JSON or Yaml file, when referring to the documentation use the table below to translate the ini file format setting to the JSON or Yaml file format

| ini file | JSON File | Yaml File |
| ---- | ---- | ---- |
<td>
	```
	[Section]
	option = value
	```
</td>
<td>
	```json
	{
		"Section": {
			"option" = "value"
		}
	}
	```
</td>
<td>
	```yaml
	Section:
		option: value
	```
</td>
