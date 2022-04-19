#!/bin/bash
#
#
cd $(dirname "$0")

currversion=$(git describe --abbrev=0 --tags)
echo $currversion
subver=$(date +%s)
if [[ "$currversion" =~ v[0-9]\. ]]; then
	verparts=($(echo $currversion | tr "-" "\n"))
	len=${#verparts[@]}
	if [ $len -gt 1 ]; then
		txtversion=${verparts[0]}.$subver-${verparts[1]}
	else
		txtversion=${verparts[0]}.$subver
	fi
	numver=$(echo $currversion | sed -E 's/v([^-]*)/\1/')
	echo numver\: $numver
	version=$numver.$subver
	echo version\: $version

	sed -i '' -e "s/version *= *\"[^\"]*\"/version=\"${version}\"/" $(find . -name "*.py")
	#	Version Test
	sed -i '' -e "s/#    Version .*/#    Version ${version}/" $(find . -name "*.py")

	rm -R dist/
	# python3 setup*.py sdist bdist_wheel
	rm -R build/
	python3 setup-manager.py sdist bdist_wheel
	rm -R build/
	python3 setup-agent.py sdist bdist_wheel
	rm -R build/
	python3 setup-reporter.py sdist bdist_wheel

	python3 -m twine upload --repository testpypi dist/*${version}*

fi

cd -
