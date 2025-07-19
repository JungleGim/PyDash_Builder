# PyDash_Builder - Information
This readme covers the dash builder portion of the PyDash. For the Dash App, PCB design, Enclosure design, or OS design, see the below repositories:
- PyDash_PCB
- PyDash_App
- PyDash_Enclosure
- PyDash_OS

## Introduction
The PyDash buidler (also just "builder" or "dash configurator") is a python script that launches a user environment to build the dash layout configuration file, that is then sent to the PyDash app. The builder environment should be an easy to navigate visual editor environment where users can pick, place, and update the various aspects that define a PyDash layout.

In summary, users are able to configure the following elements to build a PyDash layout:
- Custom Themes containing:
	- Named colors
	- Named Fonts
	- Images
- Dash display pages containing:
	- Display various labels and gauge text
	- Bar and bullet indicators
	- Set background images
	- Set the order of the display pages
- CAN configuration information:
	- PID of the PyDash itself
	- CAN data filters
	- Define CAN channels used for requesting (*or listening for) information
- Other PyDash configuration parameters:
	- Backlight brightness

After completing a PhDash layout, users can save the configuration file for opening or editing later. Users can also then generate the layout configuration file which will include the PyDash config.xml file and any supporting references (like images). These files can then be uploaded to the dash for a new customized layout!

The builder application also contains a local help file for users to reference the various aspects of the software.

Additional details on the design considerations, required packages, and key features are included in the "Methodology" section of this readme.

# Project Status
## Revlog
- Rev 0: TBD
	- Initial issue for use with PyDash Rev2.0
	
## Future Development
The below is a list of wants/needs for future revisions; loosely listed in order of importance.
- TODO: List future dev options

## Repository Directory Map
The following information describes the folders found in the root directory of this repository
- (folder) App
	- This is the main application folder
	- (folder) archive
		- Contains previous versions of the application. TBD will be superseded with the full implementation of GIT
- (folder) Dev-Testing
	- This folder contains some of the WIP or simplified applications used to develop the app. Usually the intent is to create smaller, focused elements that can be integrated into the main program later.

# Requirements
## Build Environment
Currently, VSCode on a windows environment is being used to develop the program. Ultimately any IDE that supports python should be applicable. Depending on the required python packages, additional installation steps may be required.

## Dependent Packages
### Tk/Tkinter
Tk and Tkinter are both included by default with the main python package. If users have installed a limited package, addition of the Tk GUI toolkit may be required

### Pillow
Pillow is used for some graphical tools and processing in the app

To install:
  (windows):      "pip install Pillow"
  (Linux):        "sudo apt-get install python3-pil python3-pil.imagetk"
		
### Compileall
The python "compileall" package is used in the current windows environment to provide a compiled python package. A compiled python package provides some overhead streamlining when running the program on the dash.
		(windows):			"pip install compileall2"
		
To compile, from command line in python program directory type `python -m compileall . -q`. Then copy files from the `pycache` folders into the desired deployment directory. Note that any file structure and dependent directories (like image file) need to be copied as well.

# Methodology
## Key Considerations and Constraints
TODO: list out the key considerations for making/maintaining this application

## Application and Codebase Features
The following sections describe the thought process behind some of the different key features in the code. This is not meant as a definitive list but is meant to help supplement the comments in the code and explain some of the various aspects of the code. As a disclaimer, I'm a hobbyist button masher so there likely are some "non-pythonic" things going on in the code which I apologize for in advance.

### Graphical Layout
TODO: explain the various application views

### Application Flow
TODO: explain the various application elements

### Application code elements and files
The following discusses some of the code elements and library files along with the intent of their operation/existence. Again, this is not meant as a complete definitive guide but should supplement the existing code comments.

#### Files and Libraries
TODO: list out the various files and what they contain

#### Code Elements
TODO: Discuss the various code elements like classes and function groups and what the purpose of them are.

# Application HELP file
See the "help.py" file in the lib folder for a discussion of the various application views and features. The separate help file is where documentation on the application operation will be maintained.
 
TODO: make help file

# Known bugs and bug fixes
No current known bugs

# FAQ section
No current FAQ

# Copyright and licensing information
TBD this section is a work in progress to list the correct, legal licensure information. However, as a generic disclaimer;
 
The information included is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software or tools included in this repository.

# General Notes and References
While I am an engineer by trade, my area of focus is not computer architecture or system engineering. Likely some people have already looked at various aspects of the codebase and just shook their heads. That being said, I've compiled a list of considerations and notes for the project that have helped me along the way. These are listed below, in no particular order.

## Notes

## References
Throughout the project, I have used many references, related to various aspects/items of the project. These are all compiled in the list below, in no particular order
- [Tk and Frames - lots of sub-links](https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter)
