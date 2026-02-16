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
- Rev 0.a
	- Build date: 12/25/2025
    - Alpha testing initial release
	- Intended for use with PyDash App Rev2.0
    - See Project_Tracker.md for current working notes/issues that are WIP
	
## Future Development
The below is a list of wants/needs for future revisions, listed in no order of importance

* Documentation: App documentation
    - make a full user guide word file / PDF and upload to github
    - should explain all the views, fields, and various functions of the application
* QoL: Dash Editor Window - Focus shift, field validity check
    - Implement a mechanic in the element editor window so that if focus is shifted (like clicked away from the current field) and a required value isn't set, a warning/error should be displayed
    - For example, if editing a dash element and the "background pad" option is checked and then no color is specified, but the user clicks away to another widget, it should say "hey....you uh...need to specify <thing>"
    - Another example would be that a text value for the the "static text" element shouldn't be allowed to be blank. If a user updated/cleared that value and then attempted to navigate away, a warning/error should be displayed
* Improvement: Updated background pad generation
    - Currently, the "BBox" function is used to generate the dimentions for the label/value background padding. The issues is that the background pad shape can be kinda odd based on the linespace of some fonts. This does appear to be VERY font dependent.
    - For example, the bbox return for "Cascadia Mono" is very large above the text; much larger than the actual font letters. Some other typeface have asymetric above/below line spacing (like cascadia mono). At the same time, the default windows font (Segoe UI Variable Text) has a VERY tight BBOX return (which is great!)
    - See if there's a better way to draw that so that the pad distance around the text is just around the text letters, not the font linespace. Unsure if this is really possible or not.
        + alternatively, since the fonts used in the dash files are going to be limited, maybe make a test "pad preview" program to see which fonts are better/easier/tighter than others. Could use this to find appropriate font families with apprioriate spacing/fitting. Those will ultimately be the fonts chosen to have in the final PyDash load.
* Improvement: General code cleanup
    - there's more than a few spots where code is a little kledugy and could be improved.
    - For example, I'm not sure that the class <FrmEdit_bind_widget_control> is needed. This was originally used because it's a function common to all dash elements.
        + However, for example, when a static or data label has its pad background changed, the chosen method was to delete and then re-create to make it "Easier" for managing the pad. The issue is then that the existing ref to the pad object (in that class instance) doesn't update, so the new "upd_refs" function was added to handle that. Is this really the best way to handle that? Or can I do better?
        + It just feels like there's maybe a better way to handle that and/or streamline/modularize the code more. 
    - Another example of code cleanup is that in the "page" class, there really doesn't need to be a dict for each element type.
        + In theory, having the separate dicts allows for different elements with the same ref name but like...that's not really a concern in practice. I think chaning to a single "elements" dict would be fine and would arguably streamline a few of the places in the code. Each element would have its own unique key anyway and then the various values (element type class) don't care.
        + There are a couple different spots where there's an actual element dependent action could be handled by a switch statement and determining what the associated class is OR could add a common "type" attribute to all classes and then ignored when/where not needed
    - Another is that in the common dash element type defs, some of the methods are shared (or very similar) across the different element types
        + For example, the "upd_pad_obj" method is identical between static and data labels.
		+ this was initially done so that when needed, the various methods could be called by using <instance>.<method>. It additionally means any element-specific idiosynchrasies can be modified within the class defintion.
        + Figure out the best way that these could be condensed and/or use a single method. Maybe as-is really is the best way to do it still. The concern is that currently with multiple similar methods its just a maintainence nightmare and is a potential error trap when udpating. Maybe use a single common function definition with "multiple displatch" that has passed object references which would make it more modular (and still retain per-element differences)?
    - Also consolidate by function
        + for example, many of the "com_defs" functions would fit well into the "editor control" class...but then I'm not sure how many of those are used outside of that main window (like in the XML file). So some of them being in the "com defs" may be better/cleaner than passing a master ref everywhere. But also if the master ref is already there.....
    - variable and function naming clarity
        + some of the function/method names are a little convoluted and/or unclear and/or repeated. Make it better
            * for example, "buildPages" in com_defs is just establisting the page base canvas object. Casual reading makes it seem much more than that. Can be better about this.
* Improvement: editor control class
    - Should try to move as many of the "common" functions here as makes sense
    - ALSO look out for any lengthy functions in the "main window" class that should be here
        + for example, all the gibberish under the "new_element" function in the MainWindow class could/should be in the editor control class. Or at least it feels more appropriate to have it in the editor control class
    - Doing the above will also likely help consolidate code and prevent reppetition
* Feature Request: XML integration
    - build an "error check" function to validate the XML file being opened.
        + the potential concern is that users may have edited the dash configuration save file outside of the program and made typos/errors.
        + The intentin of this function would be to validate an XML file being opened for things like:
            * valid XML file (all tags are closed?)
            * check to make sure the required major secitons for a dash config are there
            * make sure the values/required values make sense (like the current "check config" function before saving)
            * etc.
        + When complete, report results to user. Should perform this check before opening XML files
* Improvement: Editor Button Enable/Disable State Handling
    - Editor First Open / Allowed functions / Add element buttons
        + currently, the "add element" buttons are enabled all the time, but do have a check if there's a page currently defined (so a new element can be added).
        + A more user friendly way to do this would be to have some kind of "lockout" for when the editor doesn't have a valid page selected.
        + The desired fucntionality would be that the "add element" buttons are disabled if there's not a valid page to add them to.
        + another good thing maybe would be to add a "check pages" function in the editor_control class so that if there's no currently defined pages, the "add element" buttons are disabled (even after creating a "new" config)
    - Wiget delete button
        + do something similar to the above for the "delete element" button where it will only be enabled if there's a dash page element selected.
* Improvement: custom notification window class size/functionality
    - currently works but needs some tweaking to be better
    - make the window vertically resizable up to a certain size, at which point if more space is needed (because of long text) a vertical scroll bar should appear
* Feature request: Add a new "analog gauge" dash element
    - not 100% sure how this would work yet, but some ideas:
        + treat as a square (circle) and use a "size" param similar to the existing bullet indicator to scale the gauge
        + "default" would be a solid background color with the foreground color for the markings
        + standard shape would be just a circle, but can also provide a "sweep" parameter. Default needle "Sweep" would be like 300* with a 60* wedge centered at the bottom for the gauge display name
        + Otional gauge background image - should figure out how to "fill" a round object with the image or maybe restrict it to an image format for the gauges? latter would be much easier to implement but onus is on the user then to make their own backgrounds
        + Optional needle color (default use same as foreground color)
        + Needle is maybe just a long/thin rectangle?
        + much like the current "indicator_bar" class, the min/max values would set the bounds of the "sweep" and then the needle position would be relative to the defined min/max values.
        + would also need "major" and "minor" divisions for the definition to provide gauge tic-marks
        + would need a new function to handle the drawing of the text
    - since all of this is relatively complex (lots of elements) potentially the easiest way to handle this in the editor would be to use a sub-canvas for each analog gauge.
        + That would keep everything inside of it relative as well and so any "move" commands with click/drag or position updates would just move the chanvas and handling all the individiual gauge element moves wouldn't be needed.
        + Also may handle the "gauge shape" easier with a mask or something (via PIL library)? Would make the gauge face just a similar background color/object like pages are now. Then chosing a "shape" in the gauge drop-down would change how it's masked. Then users would just need to keep the image as a "square" and keep relative positioning for any like, gauge colors or self-imposed text/labels in mind.
    - When done, so much of the above is just "static" w.r.t. the actual dash. The dash editor will need to keep these dynamic for user changes in the editor but the dash doesn't (and shouldn't) need to make it programatically.
        + A good solution for this in the "gauge definition" would then to make each of those user defined "digital gauges" just static images. The dash then could use the "place image" function similar to any other image to put them on screen
        + This is already possible with the PIL library using the "ImageGrab" function and would make the downstream dash implemtentation SO much easier.
        + The additional args in the "gauge" element then would be something like the data channel name, "min/max" values, and "sweep angle min/max" limits to draw the needle where it's supposed to be in the dash. Then all the "update" function for this in the dash would need to be is calculate the "needle" angle based on the current data channel value, min/max value, and min/max sweep limits.
* QoL: Make a "copy font" button in the "theme - fonts" menu font definition view
    - The idea is that a user likes everything about the current font but maybe just wants to change the color, size, or family
    - Copying an existing font and then updating the desired fields would be much easier than re-defining a whole new font
* Improvement: In the "font editor" view, update the "preview text" so that it has a wrap width.
    - This will make the "font preview" a much more fixed width
    - Maybe do a fixed height too? Would be great to keep this from auto-sizing
* QOL: Make a "copy element" button for the main editor view
    - place next to "delete element"
    - would copy the currently selected element, and display a message like "element <name> copied!
    - After copying, update text and function to "paste element"
    - When "pasting", first prompt for a new reference name and then after the user clicks "OK" use the same "element place" type routine like what's used when creating a new element.
        + should actually be able to juse re-use the "new element" routine or parts from it to make thigns easy.
* QOL: Add a right-click "context menu" for the main editor view
    - this would be helpful for several functions with editing. Some ideas:
        + top of the menu would be "local elements". This would be great if like, one element is stacked (or near) another and the user wants to specify the EXACT element to pick/update
            * this should easily be done using the "find_closest" canvas method and include the `halo` argument with some radius
        + add a separator
        + Then include some common editing things like the copy/paste/delete options
* QOL: More editor keyboard shortcuts
    - Escape Key
        + should de-select whatever currently selected element is in the editor
    - Ctl+C
        + Bind to "copy element"
    - Ctl+V
        + Bind to "paste element"
    - Arrow keys (upd, down, left, right)
        + make a new "bump" function to move the currently selected element up/down/left/right by 1 pixel
        + also press/hold then moves continually
    - Delete key
        + bind to "delete element"
* Improvement: Improved background padding
    - The background padding shape and "extra space" around various fonts is really fucking bothering me
    - Tried doing some testing with various methods (see archive `tkinter_padBox_testing`)
        + used BBOX with different justifications
        + also used "manual" box placement based on a font-point to DPI conversion
        + Tried using a canvas "window" and just....yeah. all the things
        + Some worked better with some fonts and then just broke completely with other fonts
    - Potential solution
        + from all the testing, it looks like probably won't be able to just make a "fixed" bacgkround pad based on the passed font, since literally all of the fonts are different and have different kerning.
        + solution: allow for configuration of the background pad
            * initial pad size can still be handled by the BBOX() method on generation
            * include additional factors for "pad_x_offset", "pad_y_offset", "pad_x_size_adj", and "pad_y_size_adj"
            * the additional factors will let users configure the individual pad for each label
            * allows for the same pad objects and handling currently in the code but then just integrate the above additional factors to change the size and position of the created pad object. IE, the "offset" moves the x/y position by some ammount and the "size adjust" can be some pixel factor to adjust the x/y size of the box.
            * using "relative" sizes for these tweaks then allows for an easy [x_ofst = widget_class.get('pad_x_offset',0)] type approach where if the box tweaks aren't defined then just a '0' value (so no tweak) is used
        + I think because each font is different and then each text label is different (due to potential upper + lower case mixes) this has to be applied at the individual label level, not at the like, overall font level where the same shift would be applied to ALL entries.
* Feature Request: Updated RTR frequency
    - Updates to support "missed message" handling in the dash
    - Update the RTR frequency for CAN channels for ALL entries (RTR or not) to be required
    - If RTR is not enabled, the label should say "expected frequency"
    - XML field outputs for both the dash config and editor save can remain the same
    - Update the error check and required field checks in various views to ensure that the RTR freq field is populated
* Improvement: Updated CAN frame definition
    - Don't use "frames" anymore, change how CAN data is defined for use in the dash
    - Update to "start bit", "number of bits", and "Endian"
    - Endian will ensure the RX'd message is reconstructed correctly
    - "start bit" and "number of bits" will help simplify things and allow like, single big status messages to be used
    - Grayhill keypad and others use single bits so its worth updating

## Repository Directory Map
The following information describes the folders found in the root directory of this repository
* (Builder_Application) lib
	- This is the main application folder and contains everything required for the application to function
* (folder) Dev-Testing
	- This folder contains any WIP or simplified applications used to develop the app.
    - Usually the intent is to create smaller, focused elements that can be integrated into the main program later.
	- This has no direct link to the main application, however is a repository for some of the WIP items
* (folder) Documentation
    - Contains any user documentation like the quick-start guide and user guide
    - (folder) dash_editor_templates
        + contains some test and example templates
    - (file) PyDash_Fonts.zip
        + archive of the required fonts for the application to function correctly

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
## GNU GPLv3
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Additional disclaimer
The information included is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software or tools included in this repository.

# Note from the "Developer"
While I am an engineer by trade, my area of focus is not computer architecture, system engineering, or any computer sciences. Likely, some people have already looked at various aspects of the codebase and just shook their heads. That being said, I'm giving it the good ole college try with this project (and GitHub) and will do my best to keep things up to date.
