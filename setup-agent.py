import setuptools

with open("README_PyPi.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-agent",
	version="1.4.0",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm Agent",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/rfswarm",
	packages=setuptools.find_packages(exclude=["*fswarm_report*", "*rfswarm_manager*", "build/*"]),
	data_files=[
		('rfswarm_agent/icons', ['rfswarm_agent/icons/rfswarm-agent-128.png']),
		('rfswarm_agent/icons', ['rfswarm_agent/icons/rfswarm-agent-128.ico']),
		('rfswarm_agent/icons', ['rfswarm_agent/icons/rfswarm-agent-1024.png']),
		('rfswarm_agent/icons', ['rfswarm_agent/icons/rfswarm-logo-128.png']),
		('rfswarm_agent/icons', ['rfswarm_agent/icons/rfswarm-logo-128.ico']),
	],
	include_package_data=True,
	install_requires=['configparser', 'requests', 'robotframework', 'psutil'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Framework :: Robot Framework",
		"Framework :: Robot Framework :: Tool",
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
	entry_points={'console_scripts': ['rfswarm-agent = rfswarm_agent.rfswarm_agent:RFSwarm']},
)
