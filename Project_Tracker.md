# PyDash Config Editor Readme
WIP readme for the PyDash configuration editor

## Version
Version: 0.0
Build Date: 11/17/2025

# Global TODO list
* Fixes: XML integration
    - Make the 'save dash config' function
        + use the existing "genXML" functions for this. Will have to update the functions a bit to know which of the tuple list of args to use (dash vs editor) but the actual XML generation is the same, so may as well use what's already built
        + TODO code changes:
            * finish the "gen_dashCFG" function in the "mainwindow" file
            * make the dash config generation code
* code documentation
    - Update all the functions/methods and include proper text and input attribute/type entires similar to the main CAN channel class
    - make a user guide word file / PDF and upload to github
        + also upload to github
* System Fonts
		- Find and implement a list of the available fonts for the builder to use with widgets

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