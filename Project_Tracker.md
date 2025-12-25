# PyDash Builder - Project Tracker
project tracker for WIP issues, what's currently being worked on, and anything that may need to move to the actual README file

## Version
Version: 0.a - Alpha Testing
Build Date: 12/25/2025

# WIP Version TODO list
* Alpha Test Errors and Required Fixes
    - `class` Indicator_Bar : `method` get_edtr_wgt_kwargs
        + when updating the width/height in the element properties view, function does not appropriate handle when the "width" or "height" are zero'd out.
        + Look at the "position" equivalents for how this should be handled
        + Also the "size" field for the bullet indicator handles this appropriately
    - `class` Label_Static and `class` Label_Data : `method` (TBD)
        + When updating the font family in the "theme-font" menu view, the backgroud padding objects do not appropriately re-size to the updated new width of the font element
        + Same thing happens when updating the font size in the "theme-font" menu
        + Verified then when updating either the "text" or "max value" that it appropriate re-sizes
    - `class` (TBD) : `method` (TBD)
        + when placing element, the "current selected element" in the editor element properties should be the one that was just placed
        + currently, the focus does not shift on placing a new element which is kind of a klunky interaction
    - `class` Label_Data : `method` (TBD)
        + Potential unknown issue when first placing "Data" type labels and assigning warning/danger limits
        + In testing, placing a new data label, clicking on it, and then updating the limits doesn't seem to initially commit
        + Editing other elements, then re-clicking the (problem) element and updating the values seems to commit
        + Unknown/unsure entry conditions but should try to replicate in testing
    - `class` Label_Static : `method` XML_dashCFG_checkErrs
        + In testing with the "showcase config", placing the RPM marker labels identified an issue with the configuration checker. Labels do not have background padding but are identified as "missing the background color"
        + The background color should only be required if the element has background padding enabled
        + Verified the "Label_Data" class type does this appropriately
    - `method` parseXML : call to `method` buildPages
        + When directories were moved, the source files for background images could not be found when opening an existing config
        + Include a "check" for the images at external paths at this point and warn/prompt the user if they cannot be found
        + Have a similar function in the "theme - images" editor view, so should just be able to call it again, here in the initial load stage
* Final Testing
    - Make a whole new dash configuration from scratch with the builder and then test if it functions with the pydash app. IT HAS TO BE SEAMLESS so make sure its completely working.
* Update github
    - upload the PyDash Builder github
        + update the github readme including future updates, etc.
        + do an executable build for windows (see next bullet point)
    - use PyInstaller to make a condensed executable
        + would be preferred so people can/could just run the whole prog w/o needing python, libraries, etc.
        + put the pyinstaller executables in the "release" part of the git page
    - MacOS support (future)
        + look at getting a Mac Mini so can run PyInstaller on MacOS to generate a different standalone support for MacOS
    - Linux support (future)
        + clone project into Ubuntu VM and run PyInstaller there for Linux support

# Future Updates
Include any items below in the appropriate README.md file section
(none)