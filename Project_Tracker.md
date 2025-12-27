# PyDash Builder - Project Tracker
project tracker for WIP issues, what's currently being worked on, and anything that may need to move to the actual README file

## Version
Version: 0.a - Alpha Testing
Build Date: 12/25/2025

# WIP Version TODO list
* Final Testing
    - Make a whole new dash configuration from scratch with the builder and then test if it functions with the pydash app. IT HAS TO BE SEAMLESS so make sure its completely working.
* Update github
    - upload the PyDash Builder github
        + update the github readme including future updates, etc.
        + do an executable build for windows (see next bullet point)
    - Make a release archive and upload
        + use PyInstaller to make a condensed executable archive
            * would be preferred so people can/could just run the whole prog w/o needing python, libraries, etc.
            * put the pyinstaller executables in the "release" part of the git page
            * MacOS support (future)
                - look at getting a Mac Mini so can run PyInstaller on MacOS to generate a different standalone support for MacOS
            * Linux support (future)
                - clone project into Ubuntu VM and run PyInstaller there for Linux support
        + Include the quickstart
        + Include the required fonts

# Future Updates
Include any items below in the appropriate README.md file section

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