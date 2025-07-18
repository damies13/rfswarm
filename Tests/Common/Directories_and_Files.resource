*** Settings ***
Resource 	Common.resource

*** Keywords ***
# # # # # # # # # # # # # # # # #
# Paths, directories and files: #
# # # # # # # # # # # # # # # # #

Wait For File To Exist
	[Arguments] 	${filepath} 	${timeout}=${120}
	TRY
		WHILE    True 	limit=${timeout} seconds
			TRY
				Sleep 	500 ms
				File Should Exist 		${filepath}
			EXCEPT
				CONTINUE
			END
			BREAK
		END
	EXCEPT
		Fail 		File '${filepath}' does not exist after ${timeout} seconds
	END

Clean Up Old Files
	[Tags]	ubuntu-latest 	macos-latest 	windows-latest
	# cleanup previous output
	Log    ${OUTPUT DIR}    console=${True}
	Remove File    ${OUTPUT DIR}${/}*.txt
	Remove File    ${OUTPUT DIR}${/}*.png
	# Remove File    ${OUTPUT DIR}${/}sikuli_captured${/}*.*

Clear Result Directory
	[Documentation] 	Clears all files and directories in "$RESULTS_DIR" directory. Use with caution.
	[Arguments] 	${RES_DIR}=${RESULTS_DIR}
	@{run_result_dirs}= 	List Directories In Directory 	${RES_DIR} 	absolute=${True}
	FOR  ${dir}  IN  @{run_result_dirs}
		Remove Directory 	${dir} 	recursive=${True}
	END

Show Dir Contents
	[Arguments]		${dir}
	${filesnfolders}= 	Evaluate    glob.glob("${dir}${/}*", recursive=True) 	modules=glob
	FOR 	${item} 	IN 	${filesnfolders}
		Log 	${item} 	console=True
	END

Find Absolute Paths And Names For Files In Directory
	[Documentation]	This algorithm analyses the specified path and returns all
	...    file names with their absolute paths even those that are in subdirectories
	[Arguments]		${given_path}	@{excluded_files}
	VAR 	${curr_dir} 	${given_path}
	@{absolute_paths}	Create List
	@{file_names}	Create List
	${new_dir}		List Directories In Directory	${curr_dir}	absolute=${True}

	#=== Collecting data section ===
	@{dir_files_path}=		List Files In Directory		${curr_dir}	absolute=${True}
	@{dir_file_names}=		List Files In Directory		${curr_dir}

	${length}	Get Length	${dir_files_path}
	FOR  ${i}  IN RANGE  0  ${length}
		IF  '${dir_file_names}[${i}]' not in ${excluded_files}
			Append To List	${absolute_paths}	${dir_files_path}[${i}]
			Append To List	${file_names}	${dir_file_names}[${i}]
		END
	END

	#=== Merging data section ===
	FOR  ${specific_dir}  IN  @{new_dir}
		${next_absolute_paths}	${next_file_names}
		...    Find Absolute Paths And Names For Files In Directory	${specific_dir}	@{excluded_files}

		${length}	Get Length	${next_absolute_paths}
		FOR  ${i}  IN RANGE  0  ${length}
			${bad_list}	Get Length	${next_absolute_paths}
			IF  ${bad_list} != ${0}
				Append To List	${absolute_paths}	${next_absolute_paths}[${i}]
				Append To List	${file_names}	${next_file_names}[${i}]
			END
		END
	END

	RETURN	${absolute_paths}	${file_names}

List Files In Directory And Sub Directories
	[Arguments] 	${path} 	${pattern}=None 	${absolute}=False
	@{files}= 	List Files In Directory 	${path} 	${pattern} 	${absolute}
	FOR 	${file} 	IN 	@{files}
		${fpath} 	${ext} = 	Split Extension 	${file}
		IF 		'${ext}' == 'pyc'
			Remove Values From List 		${files} 	${file}
		END
	END
	@{dirs}= 	List Directories In Directory 	${path}
	FOR 	${dir} 	IN 	@{dirs}
		@{sd_files}= 	List Files In Directory And Sub Directories 	${path}${/}${dir} 	${pattern} 	${absolute}
		FOR 	${file} 	IN 	@{sd_files}
			IF 	${absolute}
				Append To List 	${files} 	${file}
			ELSE
				Append To List 	${files} 	${dir}${/}${file}
			END
		END
	END
	RETURN 	${files}

Get Relative Paths
	[Arguments] 	${base} 		${paths_in}

	${paths_out}= 	Create List
	FOR 	${item} 	IN 		@{paths_in}
		${relpath}= 	Evaluate 	os.path.relpath(r"${item}", start=r"${base}") 	modules=os.path
		Append To List 	${paths_out} 	${relpath}
	END
	RETURN 	${paths_out}

# # # # # # # # # #
# Icon Installs:  #
# # # # # # # # # #

Check Icon Install
	${comp} 	Convert To Lower Case 	${COMPONENT}
	VAR 	${projname}= 		rfswarm-${comp} 		scope=TEST
	VAR 	${dispname}= 		RFSwarm ${COMPONENT} 	scope=TEST
	Run Keyword 	Check Icon Install For ${PLATFORM}

Check Icon Install For Macos
	${Status}= 	Run Keyword And Return Status 	Directory Should Exist 	%{HOME}${/}Applications${/}${projname}.app
	IF 	${Status}
		VAR 	${appfolder} 	%{HOME}${/}Applications${/}${dispname}.app
	ELSE
		VAR 	${appfolder} 	${/}Applications${/}${dispname}.app
	END
	Directory Should Exist 	${appfolder} 		.app Folder not found

	Directory Should Exist 	${appfolder}${/}Contents 		Contents Folder not found
	Directory Should Exist 	${appfolder}${/}Contents${/}MacOS 		MacOS Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources 		Resources Folder not found

	Directory Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset 		iconset Folder not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.iconset${/}icon_*.png 		Icons Images not found

	File Should Exist 	${appfolder}${/}Contents${/}Resources${/}${projname}.icns 		icns File not found

	File Should Exist 	${appfolder}${/}Contents${/}Info.plist 		plist File not found
	# Show Log 	 					${appfolder}${/}Contents${/}PkgInfo
	Log 	 					${appfolder}${/}Contents${/}Info.plist 	console=${True}

	File Should Exist 	${appfolder}${/}Contents${/}PkgInfo 		PkgInfo File not found
	# Show Log 	 					${appfolder}${/}Contents${/}PkgInfo
	Log 	 					${appfolder}${/}Contents${/}PkgInfo 	console=${True}

	File Should Exist 	${appfolder}${/}Contents${/}MacOS${/}${projname} 		Executable Symbolic Link File not found

Check Icon Install For Windows
	Log 	%{USERPROFILE}
	Log 	%{APPDATA}
	Directory Should Exist 	%{APPDATA} 		APPDATA Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft 		Microsoft Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows 		Windows Directory not found
	Directory Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu 		Start Menu Directory not found
	File Should Exist 	%{APPDATA}${/}Microsoft${/}Windows${/}Start Menu${/}${dispname}.lnk 		Shortcut File not found

Check Icon Install For Ubuntu
	Log 	%{HOME}
	# /home/dave/.local/share/applications/rfswarm-manager.desktop
	${Status}= 	Run Keyword And Return Status 	File Should Exist 	%{HOME}${/}.local${/}share${/}applications${/}${projname}.desktop
	IF 	${Status}
		VAR 	${pathprefix} 	%{HOME}${/}.local${/}share
	ELSE
		VAR 	${pathprefix} 	${/}usr${/}share
	END

	File Should Exist 	${pathprefix}${/}applications${/}${projname}.desktop 		Desktop File not found
	File Should Exist 	${pathprefix}${/}icons${/}hicolor${/}128x128${/}apps${/}${projname}.png 		Icon File not found
