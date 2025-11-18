# PyDash_Builder - Information
This readme covers the dash builder portion of the PyDash. For the Dash App, PCB design, Enclosure design, or OS design, see the below repositories:
- PyDash_PCB
- [PyDash_App](https://github.com/JungleGim/PyDash_App)
- [PyDash_OS](https://github.com/JungleGim/PyDash_OS)
- PyDash_Enclosure
- [PyDash_Builder](https://github.com/JungleGim/PyDash_Builder)

## Introduction
The PyDash buidler (also just "builder" or "dash configurator") is a python script that launches a graphical user environment to build a PyDash layout configuration file, that is then sent to the PyDash app. The builder graphical environment should be an easy to navigate visual editor environment where users can pick, place, and update the various aspects that define a PyDash layout.

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
	- base PID of the PyDash itself
	- CAN data filters
	- Define CAN channels used for requesting (*or listening for) information
- Other PyDash configuration parameters:
	- Backlight brightness

After completing a PhDash layout, users can save the configuration file for opening or editing later. Users can also then generate the layout configuration file which will include the PyDash config.xml file and any supporting references (like images). These files can then be uploaded to the dash for a new customized layout!

Additional details on the design considerations, required packages, and key features are included in the "Methodology" section of this readme.

# Project Status
## Revlog
- Rev 0
	- Build date: TBD
	- Initial issue for use with PyDash Rev2.0
	
## Future Development
The below is a list of wants/needs for future revisions, listed in no order of importance

* Dash Editor Window - Focus Shift
		- Implement a mechanic in the element editor window so that if focus is shifted (like clicked away from the current field) and a required value isn't set, a warning/error should be displayed
    - For example, if editing a dash element and the "background pad" option is checked and then no color is specified, but the user clicks away to another widget, it should say "hey....you uh...need to specify <thing>"
    - Another example would be that a text value for the the "static text" element shouldn't be allowed to be blank. If a user updated/cleared that value and then attempted to navigate away, a warning/error should be displayed
* Updated background pad generation
    - Currently, the "BBox" function is used to generate the dimentions for the label/value background padding. The issues is that the background pad shape can be kinda odd based on the linespace of some fonts. This does appear to be VERY font dependent.
    - For example, the bbox return for "Cascadia Mono" is very large above the text; much larger than the actual font letters. Some other typeface have asymetric above/below line spacing (like cascadia mono). At the same time, the default windows font (Segoe UI Variable Text) has a VERY tight BBOX return (which is great!)
    - See if there's a better way to draw that so that the pad distance around the text is just around the text letters, not the font linespace. Unsure if this is really possible or not.
        + alternatively, since the fonts used in the dash files are going to be limited, maybe make a test "pad preview" program to see which fonts are better/easier/tighter than others. Could use this to find appropriate font families with apprioriate spacing/fitting. Those will ultimately be the fonts chosen to have in the final PyDash load.
* General code cleanup
    - there's more than a few spots where code is a little kledugy and could be improved.
    - For example, I'm not sure that the class <FrmEdit_bind_widget_control> is needed. This was originally used because it's a function common to all dash elements.
				+ However, for example, when a static or data label has its pad background changed, the chosen method was to delete and then re-create to make it "Easier" for managing the pad. The issue is then that the existing ref to the pad object (in that class instance) doesn't update, so the new "upd_refs" function was added to handle that. Is this really the best way to handle that? Or can I do better?
        + It just feels like there's maybe a better way to handle that and/or streamline/modularize the code more. 
    - Another example of code cleanup is that in the "page" class, there really doesn't need to be a dict for each element type.
        + In theory, having the separate dicts allows for different elements with the same ref name but like...that's not really a concern in practice. I think chaning to a single "elements" dict would be fine and would arguably streamline a few of the places in the code. Each element would have its own unique key anyway and then the various values (element type class) don't care.
        + There are a couple different spots where there's an actual element dependent action could be handled by a switch statement and determining what the associated class is OR could add a common "type" attribute to all classes and then ignored when/where not needed
    - Another is that in the common dash element type defs, some of the functions are shared across the different element types
        + For example, the "upd_pad_obj" function is identical between static and data labels.
        + Figure out the best way that these could be condensed and/or use a single function. They're the same in both cases so having it twice is just error prone. Maybe use a single common function definition that has passed object references which would make it more modular?
    - Also consolidate by function
        + for example, many of the "com_defs" functions would fit well into the "editor control" class...but then I'm not sure how many of those are used outside of that main window (like in the XML file). So some of them being in the "com defs" may be better/cleaner than passing a master ref everywhere. But also if the master ref is already there.....
    - variable and function naming clarity
        + some of the function/method names are a little convoluted and/or unclear and/or repeated. Make it better
            * for example, "buildPages" in com_defs is just establisting the page base canvas object. Casual reading makes it seem much more than that. Can be better about this.
* Fixes: editor control class
    - Should try to move as many of the "common" functions here as makes sense
    - ALSO look out for any lengthy functions in the "main window" class that should be here
        + for example, all the gibberish under the "new_element" function in the MainWindow class could/should be in the editor control class. Or at least it feels more appropriate to have it in the editor control class
    - Doing the above will also likely help consolidate code and prevent reppetition
* Fixes: XML integration
    - build an "error check" function to validate the XML file being opened.
				+ the potential concern is that users may have edited the dash configuration save file outside of the program and made typos/errors.
				+ The intentin of this function would be to validate an XML file being opened for things like:
						* valid XML file (all tags are closed?)
						* check to make sure the required major secitons for a dash config are there
						* make sure the values/required values make sense (like the current "check config" function before saving)
						* etc.
        + When complete, report results to user. Should perform this check before opening XML files
* Fixes: Editor Button Enable/Disable State Handling
    - Editor First Open / Allowed functions / Add element buttons
        + currently, the "add element" buttons are enabled all the time, but do have a check if there's a page currently defined (so a new element can be added). A more user friendly way to do this would be to have some kind of "lockout" for when the editor doesn't have a valid page selected.
        + The desired fucntionality would be that the "add element" buttons are disabled if there's not a valid page to add them to.
        + really should click "new" to create a new config first which would "unlock" all the addition of the objects, etc. Its not really a problem except there's no page to add them to.
        + another good thing maybe would be to add a "check pages" function in the editor_control class so that if there's no currently defined pages, the "add element" buttons are disabled.
    - Wiget delete button
        + do something similar to the above for the "delete element" button where it will only be enabled if there's a dash page element selected.
* Improve custom notification window class
    - currently works but needs some tweaking to be better
    - make the window vertically resizable up to a certain size, at which point if more space is needed (because of long text) a vertical scroll bar should appear

## Repository Directory Map
The following information describes the folders found in the root directory of this repository
- (folder) App
	- This is the main application folder
- (folder) Dev-Testing
	- This folder contains some of the WIP or simplified applications used to develop the app. Usually the intent is to create smaller, focused elements that can be integrated into the main program later.
	- This has no direct link to the main application, however is a repository for some of the WIP items

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
Some of the considerations and/or constraints in making this project are listed below, roughly in order of importance.
- Above all else, the UI should be easy to navigate
- As a close second, user feedback like error messages must be descriptive
		- A simple "cannot save" is not sufficient. Users should be told WHY they can't perform an action
- When possible, There should be visual indicators to what can and cannot be done, at any time
		- For example, if a current page is not selected, the "add element" buttons should be disabled to prevent users from clicking them
		- For example, a dependent field (like the CAN remote request frequency) should only be enabled if its parent field (in this case, the RTR field) satisfies the appropriate conditions.

## Application and Codebase Features
The following sections describe the thought process behind some of the different key features in the code. This is not meant as a definitive list but is meant to help supplement the comments in the code and explain some of the various aspects of the code. As a disclaimer, I'm a hobbyist button masher so there likely are some "non-pythonic" things going on in the code which I apologize for in advance.

### Graphical Layout
The intent was to break up the user view into several sections, detailed below. Each of these serve a separate purpose and 

1. Menu Bar
		a. All core definitions like theme, CAN channels, and other information is contained in the menu.
2. Editor Controls
		a. This area contains the page selection combo box and buttons for adding and removing elements to the current dash page
		b. This section should be how users navigate the dash configuration and add/remove elements
3. Editor Display
		a. This is the visual representation of the PyDash page and its elements. Above all else, this needs to replicate how the dash will look when the configuration file is loaded by the PyDash in the vehicle.
		b. Additional "grpahical" controls should be implemented so that users can click/drag elements easily to edit.
4. Element Properties
		a. This view displays the properties assocaited with the currently selected dash element.
		b. Users are able to directly edit/select properties here associated with the element. Updating element properties in this view will also update the graphical display real-time

### Application Flow
TODO: explain the various application elements, like the "core config", "CAN config", etc and how they all fit into the workflow. This isn't a user guide on how to use those parts of the program, but the intended reason why they're included.

### Application code elements and files
The following discusses some of the code elements and library files along with the intent of their operation/existence. Again, this is not meant as a complete definitive guide but should supplement the existing code comments.

#### Files and Libraries
The following is a list of the various files in the project and their intended purpose or contained code segments

- MainWindow
		- This is the main application window that contains the various UI elements and functions that interact with the rest of the codebase
		- Where possible, the code here should be relatively terse and any repeated/common functions should be in the library files. The intent was to make it so that if functions can be instanced/used/implemented in other parts of the codebase, they're common to the whole project, not just the main window class.
- com_defs
		- the "com_defs" or "common definitions" file is intended to contain code elements that are used throughout the code
		- Note that while some of the "element types" may be somewhat "system wide" they're contained in the com defs file as they're more specific to various dash functions than they are the system operation. This is a bit of a hazy line but the general takeaway is that if it's required for code elements of the editor, its in the "sys" file. If its related to editor objects, its in the "com defs" file.
- editor_control
		- The "editor control" file contains various classes used for the primary control of the editor UI.
		- Some of these persist (like the primary "editrCntl" class), others are directly tied to the various dash page elements to handle editor functions (like the "bind_widget_control" class), and others are only used intermitently when placing widgets.
		- The intent of the primary "editrCntl" class was to track the current state of the editor and how that drives other interactions. It additional provides a quick reference for things like the name of the current selected page and current selected dash element.
- editor_windows
		- The "editor windows" file contains various toplevel classes that are used when navigating the software via various menu views.
		- The exception to this rule is the "widget property" or "element property" class which is used in the editor window (to be moved later)
- XML
		- the "XML" file contains all functions related to opening, saving, and editing XML files. This includes both the final PyDash configuration file, as well as the builder "save files".
		- Generally, the naming convention splits up the files by their function:
				- xmlfile_<xxx>: Functions that deal with XML file handling. An exceptions are the "XML_open" and "XML_save" functions which directly handl the opening and saving of files
				- parseXML_<xxx>: Functions that deal with parsing or reading XML files. These are primarily used in reading the dash configuration save files
				- genXML_<xxx>: Functions called by the "editorXML_gen" function to make the various aspects of the dash configuration save file.
				- XML_dashCFG_<xxx>: functions that deal with saving the output dash configuration file. This is the file that will be transferred to the PyDash for display.
- sys
		- The "sys" or "system" file is a repository for common liraries, global constants, and system (or program) wide settings.
		- For example, the defined "font" strings here are used throughout the code. These are just a simplified means of having several defined theme constants that get used globally and can be edited/updated in one spot.
		- Additional default options are also defined here
		- Finally, some program specific values are also set here like the click/drag delay and the verbose error pop-up wrap length (window width)

# Application HELP file
See the "User_Guide.md" markdown file for a full user guide 

# Known bugs and bug fixes
No current known bugs

# FAQ section
No current FAQ

# Copyright and licensing information
TBD this section is a work in progress to list the correct, legal licensure information. However, as a generic disclaimer;
 
The information included is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software or tools included in this repository.

# Note from the "Developer"
While I am an engineer by trade, my area of focus is not computer architecture, system engineering, or any computer sciences. Likely, some people have already looked at various aspects of the codebase and just shook their heads. That being said, I'm giving it the good ole college try with this project (and GitHub) and will do my best to keep things up to date.

