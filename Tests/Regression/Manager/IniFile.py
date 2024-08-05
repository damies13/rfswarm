import configparser


def read_ini_file(filename):
	config = configparser.ConfigParser()
	config.read(filename)

	variables = {}
	for section in config.sections():
		variables[section] = {}
		for key, value in config.items(section):
			variables[section][key] = value
	return variables
