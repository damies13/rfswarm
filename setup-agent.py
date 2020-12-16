import setuptools

with open("README_PyPi.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-agent",
	version="0.6.1",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm Agent",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/rfswarm",
	# packages = ['rfswarm-agent'],
	# packages=setuptools.find_packages(),
	# packages=setuptools.find_packages(
	# 	where = '',
	# 	include = ['rfswarm-agent*',],
	# 	exclude = ['rfswarm-gui',]
	# ),
	packages=setuptools.find_packages(exclude=["*rfswarm_gui*", "build/*"]),
	# packages=setuptools.find_packages(exclude=["*rfswarm_gui*", "build"]),
	# package_dir = {"":"rfswarm-agent"},
	install_requires=['configparser', 'requests', 'robotframework', 'psutil'],
	classifiers=[
		"Development Status :: 4 - Beta",
		"Topic :: Software Development :: Testing",
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
	project_urls={
		'Getting Help': 'https://github.com/damies13/rfswarm#getting-help',
		'Say Thanks!': 'https://github.com/damies13/rfswarm#donations',
		'Source': 'https://github.com/damies13/rfswarm',
	},
	entry_points = {'console_scripts': ['rfswarm-agent = rfswarm_agent.rfswarm_agent:RFSwarmAgent']},
)
