*** Settings ***
Library 	RequestsLibrary
Library 	String
Library 	OperatingSystem

*** Variables ***
${base_url} 		https://geokeo.com/database/island/id


*** Test Cases ***
Make Indonesia Resources
	FOR 	${i} 	IN RANGE 	200
		${resp}= 	GET 	${base_url}/${i + 1}
		${islands}= 	Get Islands From Page 	${resp}
		FOR 	${island} 	IN 	@{islands}
			Make Island Resource File 	${island}
		END
	END


*** Keywords ***
Get Islands From Page
	[Arguments] 	${resp}
	# Log 	${resp.text}
	# VAR 	${pattern} 	<tr>\n.*<td.*>.*\n.*<td[^<]*>(?P<name>[^<]*).*\n.*<td.*>.*\n.*<td[^<]*>(?P<lat>[^<]*).*\n.*<td[^<]*>(?P<long>[^<]*).*
	# VAR 	${pattern} 	<tr>\n.*<td.*>.*\n.*<td[^<]*>([^<]*).*\n.*<td.*>.*\n.*<td[^<]*>([^<]*).*\n.*<td[^<]*>([^<]*).*
	VAR 	${pattern} 	<td.*>.*\n.*<td[^<]*>([^<]*).*\n.*<td.*>.*\n.*<td[^<]*>([^<]*).*\n.*<td[^<]*>([^<]*).*
	# ${islands}= 	Get Regexp Matches 	${resp.text} 	${pattern} 	1 	2 	3
	${islands}= 	Get Regexp Matches 	${resp.text} 	${pattern} 	1 	2 	3
	Log 	${islands}
	RETURN 	${islands}


Make Island Resource File
	[Arguments] 	${island}
	VAR 	${name} 	${island}[0]
	VAR 	${lat} 	${island}[1]
	VAR 	${long} 	${island}[2]

	${filename}= 	Replace String 	${CURDIR}${/}Islands${/}${name}.resource 	${SPACE} 	_
	Log 	${filename}
	Create File 	${filename} 	*** Variables ***\n
	Append To File 	${filename} 	\${NAME}${SPACE * 4}${name}\n
	Append To File 	${filename} 	\${LAT}${SPACE * 4}${lat}\n
	Append To File 	${filename} 	\${LONG}${SPACE * 4}${long}\n

