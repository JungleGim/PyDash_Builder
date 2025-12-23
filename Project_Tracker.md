# PyDash Config Editor Readme
WIP readme for the PyDash configuration editor

## Version
Version: 0.0
Build Date: 11/17/2025

# Global TODO list
* Initial Conditions / Load
	- Currently when the program loads, there are some default values being applied. This kind of results in a messy first "open" dialoge where nothing has been entered but the "Existing configuration" check thinks so.
	- Update the initial open conditions to ensure it's blank slate and that way the first time someone clicks "open" there's not an annoying error message.
	- The default values really should only be added if "new" is clicked.
	- Fixing the above would be a great time to also incorporate the basics of the "enable buttons if new config started" TODO item as well. it'll all basically fall into the same thing where the program opening should default to things disabled and then once a "new" config is created it'll enable buttons (and menu items).
	
* System Fonts
	- Find and implement a list of the available fonts for the builder to use with widgets
	- List of potential fonts googling around
		+ Liberation Sans
		+ Liberation Serif
		+ Liberation Mono
		+ Others
			* Anton
			* Archivo Narrow
			* Lemon
			* Sui Generis (MoTec Font)
			* Migrogramma D Bold Extended
			* (some sort of vintage looking automotive font like Hundell)
		+ These are also some fonts considered but just not different enough
			* Public Sans / IBM Plex Sans / Fira Sans
			* DM Sans / Roboto / Ubutu / Overpass
			* Futura
			* EB Garamond / Gentrium / Open Baskerville
			* Libre Baskerville / Alegreya / Cormorant
			* Gelasio
			* IBM Plex Mono / Fira Mono
						
# Finalization
* When all done with first rev
    - Make a whole new dash configuration from scratch with the builder and then test if it functions with the pydash app. IT HAS TO BE SEAMLESS so make sure its completely working.
    - upload the PyDash Builder github
        + update the github readme including future updates, etc.
        + do an executable build for windows (see next bullet point)
    - use PyInstaller to make a condensed executable
        + would be preferred so people can/could just run the whole prog w/o needing python, libraries, etc.
        + also if that works on windows, look at getting a Mac Mini so can run PyInstaller on MacOS
        + put the pyinstaller executables in the "release" part of the git page

# Future Updates
Include any items below in the appropriate README.md file section

* code documentation
    - make a full user guide word file / PDF and upload to github