import setuptools

with open("README_PyPi.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-manager",
	version="1.1.4",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm manager",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/rfswarm",
	packages=setuptools.find_packages(exclude=["*fswarm_report*", "*fswarm_agen*", "build/*"]),
	# I needed a recent version of pip (pip 21.0.1 worked my previous <20 version didn't) for matplotlib
	# 	to actually install withput error
	# https://matplotlib.org/stable/users/installing.html
	install_requires=['configparser', 'HTTPServer', 'pillow>=9.1.0', 'psutil', 'pip>=21,>=22', 'matplotlib', 'requests'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Topic :: Software Development :: Testing",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.7',
	project_urls={
		'Getting Help': 'https://github.com/damies13/rfswarm#getting-help',
		'Say Thanks!': 'https://github.com/damies13/rfswarm#donations',
		'Source': 'https://github.com/damies13/rfswarm',
	},
	entry_points={'console_scripts': ['rfswarm = rfswarm_manager.rfswarm:RFSwarm', 'rfswarm-manager = rfswarm_manager.rfswarm:RFSwarm']},
)
