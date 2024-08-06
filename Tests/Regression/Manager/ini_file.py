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
