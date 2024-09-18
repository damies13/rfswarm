
import os

from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

with open("README_PyPi.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setup(
	name="rfswarm-manager",
	version="1.4.0",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm manager",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/rfswarm",
	packages=find_packages(exclude=["*fswarm_repor*", "*fswarm_agen*", "build/*"]),
	# packages=find_packages(where="rfswarm_manager"),
	# package_dir={"": "rfswarm_manager"},
	# package_data={"desktop": ["*.png"]},
	data_files=[
		('rfswarm_manager/icons', ['rfswarm_manager/icons/rfswarm-manager-128.png']),
		('rfswarm_manager/icons', ['rfswarm_manager/icons/rfswarm-manager-128.ico']),
		('rfswarm_manager/icons', ['rfswarm_manager/icons/rfswarm-manager-1024.png']),
		('rfswarm_manager/icons', ['rfswarm_manager/icons/rfswarm-logo-128.png']),
		('rfswarm_manager/icons', ['rfswarm_manager/icons/rfswarm-logo-128.ico']),
	],
	include_package_data=True,
	# I needed a recent version of pip (pip 21.0.1 worked my previous <20 version didn't) for matplotlib
	# 	to actually install withput error
	# https://matplotlib.org/stable/users/installing.html
	install_requires=['configparser', 'HTTPServer', 'pillow>=9.1.0', 'psutil', 'pip>=21,>=22', 'matplotlib'],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Framework :: Robot Framework",
		"Framework :: Robot Framework :: Tool",
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
	# https://stackoverflow.com/questions/68747660/is-there-any-way-to-have-icon-for-exe-file-that-created-as-an-entry-point-using
	entry_points={'console_scripts': ['rfswarm = rfswarm_manager.rfswarm:RFSwarm', 'rfswarm-manager = rfswarm_manager.rfswarm:RFSwarm']},
	# entry_points={'console_scripts': ['rfswarm = rfswarm_manager.rfswarm:RFSwarm', 'rfswarm-manager = rfswarm_manager.rfswarm:RFSwarm'], 'gui_scripts': ['rfswarm-manager-gui = rfswarm_manager.rfswarm:RFSwarm']},
	# this breaks console logs
	# entry_points={'gui_scripts': ['rfswarm = rfswarm_manager.rfswarm:RFSwarm', 'rfswarm-manager = rfswarm_manager.rfswarm:RFSwarm']},
)

# https://pypi.org/project/pyshortcuts/
