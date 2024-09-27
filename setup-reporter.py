import setuptools

with open("README_PyPi.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-reporter",
	version="1.4.0",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm reporter",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/rfswarm",
	packages=setuptools.find_packages(exclude=["*fswarm_manag*", "*fswarm_agen*", "build/*"]),
	# I needed a recent version of pip (pip 21.0.1 worked my previous <20 version didn't) for matplotlib
	# 	to actually install withput error
	# https://matplotlib.org/stable/users/installing.html
	# zoneinfo requires python 3.9
	# tzlocal is needed to get the local timezone in a format that zoneinfo likes
	data_files=[
		('rfswarm_reporter/icons', ['rfswarm_reporter/icons/rfswarm-reporter-128.png']),
		('rfswarm_reporter/icons', ['rfswarm_reporter/icons/rfswarm-reporter-128.ico']),
		('rfswarm_reporter/icons', ['rfswarm_reporter/icons/rfswarm-reporter-1024.png']),
		('rfswarm_reporter/icons', ['rfswarm_reporter/icons/rfswarm-logo-128.png']),
		('rfswarm_reporter/icons', ['rfswarm_reporter/icons/rfswarm-logo-128.ico']),
	],
	include_package_data=True,
	install_requires=['configparser', 'pillow>=9.1.0', 'pip>=21,>=22', 'matplotlib', 'python-docx', 'openpyxl', 'tzlocal>=4.1', 'lxml'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Framework :: Robot Framework",
		"Framework :: Robot Framework :: Tool",
		"Topic :: Software Development :: Testing",
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.9',
	project_urls={
		'Getting Help': 'https://github.com/damies13/rfswarm#getting-help',
		'Say Thanks!': 'https://github.com/damies13/rfswarm#donations',
		'Source': 'https://github.com/damies13/rfswarm',
	},
	entry_points={'console_scripts': ['rfswarm-reporter = rfswarm_reporter.rfswarm_reporter:RFSwarm']},
	# this breaks console logs
	# entry_points={'gui_scripts': ['rfswarm-reporter = rfswarm_reporter.rfswarm_reporter:RFSwarm']},
)
