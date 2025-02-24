"""Module providing a function reading ini type file
and returns dictionary with the content of the file."""

import configparser


def read_ini_file(filename):
	"""Read ini file and return dictionary."""
	config = configparser.ConfigParser()
	config.read(filename)

	variables = {}
	for section in config.sections():
		variables[section] = {}
		for key, value in config.items(section):
			variables[section][key] = value
	return variables


def change_ini_option(filename, section, optionname, new_value):
	"""Open ini change setting and close"""
	print("filename:", filename)
	print("section:", section, " optionname:", optionname, " new_value:", new_value)

	config = configparser.ConfigParser()
	print("Before:", config, dict(config))
	config.read(filename)
	print("Read:", config, dict(config))

	if section not in config:
		config[section] = {}
	print("section:", config, dict(config))

	config[section][optionname] = new_value

	with open(filename, 'w') as configfile:
		config.write(configfile)

	print("After:", config, dict(config))
