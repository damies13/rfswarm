
import os
import sys

from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
	"""Post-installation for installation mode."""
	def run(self):
		install.run(self)
		# PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
		sys.stdout.write("Creating Desktop Shortcut for RFSwarm Manager...\n")
		install_dir = join(ROOT_DIR, SOURCE_DIR)
		sys.stdout.write("install_dir: " + install_dir + "\n")

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
	packages=setuptools.find_packages(exclude=["*fswarm_report*", "*fswarm_agen*", "build/*"]),
	# I needed a recent version of pip (pip 21.0.1 worked my previous <20 version didn't) for matplotlib
	# 	to actually install withput error
	# https://matplotlib.org/stable/users/installing.html
	install_requires=['configparser', 'HTTPServer', 'pillow>=9.1.0', 'psutil', 'pip>=21,>=22', 'matplotlib', 'requests'],
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
	cmdclass={
		'install': PostInstallCommand,
	},
	entry_points={'console_scripts': ['rfswarm = rfswarm_manager.rfswarm:RFSwarm', 'rfswarm-manager = rfswarm_manager.rfswarm:RFSwarm']},
)



# https://pypi.org/project/pyshortcuts/
