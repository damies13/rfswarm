import setuptools

with open("README_PyPi.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="rfswarm-gui",
	version="0.6.0.1607938580",
	author="damies13",
	author_email="damies13+rfswarm@gmail.com",
	description="rfswarm GUI",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/damies13/TestDataTable",
	# packages = ['rfswarm-gui'],
	# packages=setuptools.find_packages(),
	packages=setuptools.find_packages(
		where = '',
		include = ['rfswarm-gui',],
		exclude = ['rfswarm-agent',]
	),
	# package_dir = {"":"rfswarm-gui"},
	install_requires=['configparser', 'HTTPServer', 'hashlib', 'pillow'],
	classifiers=[
		"Development Status :: 4 - Beta",
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
	entry_points = {'console_scripts': ['rfswarm = rfswarm:RFSwarmCore']},
)
