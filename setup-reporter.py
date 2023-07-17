import setuptools

with open("README_PyPi.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-reporter",
	version="1.1.4",
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
	install_requires=['configparser', 'pillow>=9.1.0', 'pip>=21,>=22', 'matplotlib', 'python-docx', 'openpyxl', 'tzlocal>=4.1'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
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
)
