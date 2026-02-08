"""
File:       com_defs.py
Function:   This file handles any "common" function and class definitions (hence the name) that are
            used in multiple files. Additionally, any common library dicts are included here.

            NOTE: this is different than any system (application) constants which are contained in the
            sys.py file. An example of the difference is that any application constants are contained in
            this file, like the "dash element types" (DashEle_types) dict.
"""

from .sys import *

#-----------------------------common definitions-----------------------------
#---dash element types
DashEle_types = {'LBL_STAT': 1,     #static label
                 'LBL_DAT':2,       #data label (dynamic value)
                 'IND_BLT':3,       #bullet indicator
                 'IND_BAR':4}       #bar indicator

#---element position
Ele_Order = {'FG': 1,   #foreground
             'BG': 2}   #background

#---element position
Move_Page = {'UP': 1,   #foreground
             'DN': 2}   #background

#---dash page types
DashPg_types = {'GAUGE': 1,     #gauges
                'HELP':2,       #user config menu / help / navigation
                'LIST':3}       #listbox only (like CAN sniffer)

#---notification window types
Popup_types = {'INFO':1,     #generic notification window
                'WARN':2,     #warning window - same as information with a different symbol
                'ERROR':3,    #error window - same as information with a differen symbol
                'YESNO':4,    #notification with a yes/no option
                'OKCNCL':5}   #notification with a ok/cancel

#---xml generation mode
XMLgen_mode = { 'EDTR': 1,   #editor XML file type
                'DASH': 2}   #dash configuration file type

#-----------------------------common functions-----------------------------
def bool_str(val):
    """converts string to boolean value

    :param val: value to convert
    :type val: `string` or `char`
    :returns: the converted value
    :rtype: `boolean`
    """
    if type(val) == bool: return val            #value is already in bool format, no need to convert
    elif val.lower() == 'true': return True     #convert to true
    elif val.lower() == 'false': return False   #convert to false
    return False                                #default return false if unknown

def int_str(val, frmt=10):
    """converts passed value to integer value

    function can handle a `string`(int), `string`(fraction), `integer`, `float`, 
    or `none` type. If passed a `none` or zero-length string, then `none` is returned. If passed value
    is fractional representation, i.e. (1/10) then it is converted into a float (0.1)

    :param val: value to convert
    :type val: `string`, `char`, `integer`, or `float`
    :param frmt: int conversion base, defaults to base-10
    :type frmt: `integer`
    :returns: converted value
    :rtype: `integer` or `float`
    """
    if val == None: return None                 #value is none, so no conversion needed
    elif val == '': return None                 #value is a blank string, so return None
    elif type(val) == int: return val           #value is already in int format, no need to convert
    elif type(val) == float: return val         #value is already in float format, no need to convert
    elif '/' in val:                            #value is in fraction form, split and calculate
        num, den = val.split('/')
        return int(num)/int(den)
    elif '.' in val: return float(val)          #value has a decimal so use float
    elif frmt == 10: return int(val)            #dec format
    elif frmt == 16: return int(val, 16)        #hex format
    return None                                 #if unknown, return None

def list_str(val, offset):
    """converts comma separate string to integer list

    :param val: value to convert
    :type val: `string` or `char`
    :returns: the converted value
    :rtype: `integer` list
    """
    frm_list = [int(x) for x in val.split(',')] #split CSV into integer list
    frm_list = [v + offset for v in frm_list]   #offset values
    return frm_list                             #return list

def strvar_str(val):
    """function converts the passed value for use with stringvars. The most useful implementation
        of this is when trying to represent a (None) value in a stringvar. In this case, the function
        will return a zero-length string (blank string)
        
    :param val: value to convert
    :type val: `string` or `char`
    :returns: the converted value
    :rtype: `string`
    """
    
    rtn_val = ''
    if val is not None: rtn_val=val
    return rtn_val

def tup_str(tup):
    """function converts the passed tuple into a comma-separated string
        
    :param tup: value to convert
    :type tup: `tuple` of any type
    :returns: the converted value
    :rtype: `string`
    """
    csr = ", ".join(tup)
    return csr

def draw_rectangle(prnt_canv, x0, y0, x1, y1, clr, r=pad_radius):
    """function draws a rectagle on the parent canvas. Rectangle is based on the passed coords.
    The start coordinate is upper-left corner of the rectangle, end coordinate is lower-left corner 
    of the rectangle. Can pass an optional value (r) to add a radius to the rectangle corners    
        
    :param prnt_canv: parent canvas to draw rectangle on
    :type prnt_canv: `tk.Canvas`
    :param x0: start x coordinate
    :type x0: `int`
    :param y0: start y coordinate
    :type y0: `int`
    :param x1: end x coordinate
    :type x1: `int`
    :param y1: end y coordinate
    :type y1: `int`
    :param clr: color
    :type clr: HEX string color value
    :param r: (optional) rectangle corner radius
    :type r: num pixels in `int`
    :returns: reference ID of the created object
    :rtype: `tk.canvas` reference
    """
    points = [x0+r, y0, x0+r, y0,   #create the polycon points
              x1-r, y0, x1-r, y0,
              x1, y0,
              x1, y0+r, x1, y0+r,
              x1, y1-r, x1, y1-r,
              x1, y1,
              x1-r, y1, x1-r, y1,
              x0+r, y1, x0+r, y1,
              x0, y1,
              x0, y1-r, x0, y1-r,
              x0, y0+r, x0, y0+r,
              x0, y0]
    
    return prnt_canv.create_polygon(points, smooth = True, fill=clr)    #create the background polygon and return refID

def instance_widget(ele_type, prnt_canv, widg_kwargs):
    """function to create a new element in the dash page editor. If only an opbject is created, the
    retrun value will be a tuple of the reference ID and `none` as the second value. If the created 
    widget has a "background pad" rectangle it will also return the ref ID of the background object.

    :param ele_type: the dash element type being created
    :type ele_type: Dict `DashEle_types`
    :param prnt_canv: parent canvas to make object on
    :type prnt_canv: `Tk.Canvas` class
    :param widg_kwargs: widget creation KWARGs - Will be converted here based on the named objects (for font, color, etc.)
    :type widg_kwargs: Dict {kwarg_name \: value}
    :returns: tuple of reference ID of the created object, and pad reference
    :rtype: `tk.canvas` reference
    """
    wigt_ref = None
    
    try:    #processing for widgets with background padding
        pad = widg_kwargs.pop('pad', False)
        clr_bg = widg_kwargs.pop('clr_bg',None)
    except: pass
    
    #make objects
    if ele_type == DashEle_types['LBL_STAT']:
        wigt_ref = prnt_canv.create_text(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'), **widg_kwargs)
    elif ele_type == DashEle_types['LBL_DAT']:
        wigt_ref = prnt_canv.create_text(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'), **widg_kwargs)
    elif ele_type == DashEle_types['IND_BLT']: 
        wigt_ref = prnt_canv.create_oval(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'),widg_kwargs.pop('x1'), widg_kwargs.pop('y1'),**widg_kwargs)       #set result as oval
    elif ele_type == DashEle_types['IND_BAR']:
        wigt_ref = prnt_canv.create_rectangle(widg_kwargs.pop('x0'), widg_kwargs.pop('y0'),widg_kwargs.pop('x1'), widg_kwargs.pop('y1'),**widg_kwargs)  #set result as rectangle

    if pad == True:                     #if widget has background padding, then make it
        pad_ref = elePad_create(prnt_canv, wigt_ref, clr_bg)   
        return wigt_ref, pad_ref        #and return created widget reference and pad object reference
    else: return wigt_ref, None         #otherwise, only return created widget reference

def elePad_create(prnt_canv, prnt_wgt, pad_clr):
    """function supports dash element creation. If element has a "background pad" rectangle, this function
    is used to create it.

    :param prnt_canv: parent canvas to make object on
    :type prnt_canv: `Tk.Canvas` class
    :param prnt_wgt: parent object ID the background pad is placed behind
    :type prnt_wgt: dash element class reference
    :param pad_clr: fill color
    :type pad_clr: HEX string color value
    :returns: tuple of reference ID of the created object
    :rtype: `tk.canvas` reference
    """
    prntX0, prntY0, prntX1, prntY1 = prnt_canv.bbox(prnt_wgt)           #find the size of the parent widget
    padX0=prntX0-pad_margin; padX1=prntX1+pad_margin                    #calculate X0, x1 for background pad object
    padY0=prntY0; padY1=prntY1                                          #calcualte Y0, Y1 for background pad object
    pad_ref_id = draw_rectangle(prnt_canv, padX0, padY0, padX1, padY1, pad_clr)    #create the background pad rectangle
    prnt_canv.tag_lower(pad_ref_id, prnt_wgt)                           #place the background pad below the parent widget
    return pad_ref_id   #return the background pad ID

def elePad_delete(prnt_canv, pad_ID):
    """function deletes a background pad object. When deleting, None is returned so the parent
    element object control class has its reference updated appropriately

    :param prnt_canv: parent canvas to make object on
    :type prnt_canv: `Tk.Canvas` class
    :param pad_ID: element reference ID
    :type pad_ID: `tk.canvas` reference
    :returns: `None` value
    """

    prnt_canv.delete(pad_ID)
    return None

def xmlGen_str(obj):
    """Function returns a string of any passed object unless (None) which returns a blank string. Particularly
    helpful when creating XML files and placing objects as strings.
    
    :param obj: object to typecast using str(obj)
    :type obj: any type that can be typecast to string
    :returns: string
    :rtype: `string`
    """
    rtn_str = ''
    if obj is not None: rtn_str = str(obj)

    return rtn_str

def updPages(master_ref):
    """Function loops through the page(s) in the instanced page dict in the master window. This dict contains the
    defined editor pages. For each page, it's individual "update_page" function is called. This is typically
    helpful when a core definition like a named color ref is updated and all objects that reference the named
    core definition need to be updated. Think of it like a "refesh" based on the current values in the configuration
    dictionaries.
    
    :param master_ref: reference back to the main/master window
    :type master_ref: `tk.window` ref
    """
    #TODO: should this be in the "dash_control" class?
    for page in master_ref.cfg_pages.values(): page.update_page()   #cycle through all pages and update

def addImg(canv, image, x=0, y=0):
    """Function loops through the page(s) in the instanced page dict in the master window. This dict contains the
    defined editor pages. For each page, it's individual "update_page" function is called. This is typically
    helpful when a core definition like a named color ref is updated and all objects that reference the named
    core definition need to be updated. Think of it like a "refesh" based on the current values in the configuration
    dictionaries.
    
    :param canv: parent canvas to make object on
    :type canv: `Tk.Canvas` class
    :param image: absolute filepath to image
    :type image: string
    :param x: x0 position of the image, upper-left corner (default=0)
    :type x: `int`
    :param y: y0 position of the image, upper-left corner (default=0)
    :type y: `int`
    :returns: PhotoImage reference
    :rtype: `tk.PhotoImage` int
    """
    tkImg = tk.PhotoImage(master=canv, file=image)                  #create tk photoImage
    canv.create_image(x, y, image = tkImg, anchor=tk.NW)            #place image
    return tkImg    #return tk image for ref

def upd_definition_refs(master_ref, obj_name, ref_dict):
    """function updates the named reference dicts in the various editor core items like fonts, colors, images, etc
    when a dash config is updated. As a reminder the various reference dicts are used to help navigate 
    if a particular definition is used elsewhere. This is important when attempting to delete the base defintion.
    
    For example, if a color is used in a static label, the external reference dict in the `colors` instance 
    will not allow the deleltion of that color since it has an external dependency

    :param master_ref: reference back to the main/master window
    :type master_ref: `tk.window` ref
    :param obj_name: object name that uses the reference
    :type obj_name: `string`
    :param ref_dict: dict to add/update to the reference dictionary.
    :type ref_dict: `dictionary` object, any length
    """
    try: can_ext_refs = {}; can_ext_refs['CAN_CH'] = ref_dict.pop('CAN_CH')  #pop off CAN external refs
    except: pass

    theme_ext_refs = ref_dict                                           #remaining are all theme related
    master_ref.cfg_theme.upd_ext_refs(obj_name, theme_ext_refs)         #update theme external refs
    master_ref.cfg_CAN.upd_ext_refs(obj_name, can_ext_refs)             #update CAN channels external refs

def del_definition_refs(master_ref, obj_name):
    """function deletes any references in the external refs associated with the object name passed
    As a reminder the various reference dicts are used to help navigate 
    if a particular definition is used elsewhere. This is important when attempting to delete the base defintion.
    
    For example, if a color is used in a static label, the external reference dict in the `colors` instance 
    will not allow the deleltion of that color since it has an external dependency

    :param master_ref: reference back to the main/master window
    :type master_ref: `tk.window` ref
    :param obj_name: object name that uses the reference (that is being removed)
    :type obj_name: `string`
    """
    master_ref.cfg_theme.del_ext_refs(obj_name)
    master_ref.cfg_CAN.del_ext_refs(obj_name)

def file_save_dialogue(file_dialoge_kwargs):
    """function opens the file picker dialogue to prompt the user for a place to save 
    a file. Dialogue is configurable based on the passed kwargs. Function takes a dict 
    of kwargs for the tkinter `save as` dialogue
    
    :param file_dialoge_kwargs: dict of kwargs for saveas dialogue
    :type file_dialoge_kwargs: `kwargs` for `filedialog.asksaveasfile`
    :returns: two strings with file directory and name
    :rtype: file_directory_full_path, file_name
    """
    
    filepath = filedialog.asksaveasfile(**file_dialoge_kwargs)  #prompt to get the location and name
    
    if filepath:
        dir = os.path.dirname(filepath.name) + '/'              #get file directory
        name = os.path.basename(filepath.name)                  #get file name
        return dir, name                                        #return result
    else:
        return None, None

def file_open_dialogue(file_dialoge_kwargs):
    """function opens the file picker dialogue to prompt the user for a file to
    open. Dialogue is configurable based on the passed kwargs. Function takes a dict 
    of kwargs for the tkinter `ask open` dialogue
    
    :param file_dialoge_kwargs: dict of kwargs for oepn file dialogue
    :type file_dialoge_kwargs: `kwargs` for `filedialog.askopenfilename`
    :returns: two strings with file directory and name
    :rtype: file_directory_full_path, file_name
    """
    
    filepath = filedialog.askopenfilename(**file_dialoge_kwargs)    #prompt to get the location and name
    
    if filepath:
        dir = os.path.dirname(filepath) + '/'                       #get file directory
        name = os.path.basename(filepath)                           #get file name
        return dir, name                                            #return result
    else:
        return None, None

def file_dir_dialogue(file_dialoge_kwargs):
    """function opens the file picker dialogue to prompt the user to select a directory.
    Dialogue is configurable based on the passed kwargs. Function takes a dict of kwargs 
    for the tkinter `ask directory` dialogue.
    
    :param file_dialoge_kwargs: dict of kwargs for saveas dialogue
    :type file_dialoge_kwargs: `kwargs` for `filedialog.asksaveasfile`
    :returns: two strings with file directory and name
    :rtype: file_directory_full_path, file_name
    """
    
    filepath = filedialog.askdirectory(**file_dialoge_kwargs)   #prompt to get the location and name
    
    if filepath:
        dir = os.path.dirname(filepath) + '/'                   #get file directory
        name = os.path.basename(filepath)                       #get file name
        return dir, name                                        #return result
    else:
        return None, None

#---------------------configuration classes used in multiple files---------------------
class dash_config:
    """Configuration class for core dash options (HW configuration). Examples of contained information
    includes screen resolution, backlight PWM value, and other "core" options."""
    def __init__(self):
        self.Res_x = None       #window x-resolution
        self.Res_y = None       #window y-resolution
        self.Refresh = None     #refresh rate - default of approx 15Hz in ms
        self.Baklite = None     #backlight brightness - default full bright
    
    def set_dflt_cfg(self):
        """function sets the default values for the editor config"""
        self.Res_x = int_str(dash_xSz)
        self.Res_y = int_str(dash_ySz)
        self.Refresh = int_str(refrsh_rt)
        self.Baklite = int_str(deflt_backlite)

    def len(self):
        """function counts the number of set attributes and returns how many are set. Intended to emulate
        other python len() functions like len(my_dict) or len(my_tuple). An attribute is considered "set"
        if the value is not None.
        
        :returns: num set attributes
        :rtype: `int`
        """

        tmp_count = 0                                   #temp count of any filled fields
        for attr_value in self.__dict__.items():        #loop through defined attributes and see if they are set
            if attr_value[1] is not None: tmp_count += 1   #increment count if they are set

        return tmp_count

    def clear(self):
        """function clears out all class attributes and sets to None"""
        for attr in self.__dict__.keys():   #loop through defined attributes
            setattr(self, attr, None)       #and set to None

    def upd_cfg(self, kwargs):
        """ function sets attributes based on the passed KWARGs. All KWARGs have default values
        for typical display values. If kwarg is not passed, the value is not updated

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        if 'RES_X' in kwargs: self.Res_x = int_str(kwargs.get('RES_X'))
        if 'RES_Y' in kwargs: self.Res_y = int_str(kwargs.get('RES_Y'))
        if 'REFRESH' in kwargs: self.Refresh = int_str(kwargs.get('REFRESH'))
        if 'BAKLITE' in kwargs: self.Baklite = int_str(kwargs.get('BAKLITE'))
    
    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        for att, val in self.__dict__.items():  #loop through all attributes
            if val is None or val == '': tmp_err_list.update({att:'Value is required for core config and is not properly defined'})

        return tmp_err_list

class dash_theme:
    '''Configuration class for theme configurations items like fonts, colors, images, etc.'''
    def __init__(self):
        #-----local Vars
        self.fonts = {}         #dictionary for named font data. Format is {name : font_class}
        self.colors = {}        #dictionary for color data. Format is {name : 'color val'} 
        self.images = {}        #dict for images. Format is {name : 'img_filepath'}

        self.alert_FG=None      #named color for FG (text) when alert color-changing is enabled
        self.alert_warn=None    #warning named color for BG when alert color-changing is enabled
        self.alert_dngr=None    #danger named color for BG when alert color-changing is enabled

        #-----external reference dicts: contains where/which named elements that reference theme objects
        self.fonts_ext_ref = {}
        self.colors_ext_ref = {}
        self.images_ext_ref = {}

    def set_dflt_cfg(self):
        """function sets the default values for the editor config"""
        dflt_alert_clrs = {'Alert_FG':'#000000',
                           'Alert_Warn':'#FFFF00',
                           'Alert_Dngr':'#FF0000'}    #define default alert colors
        self.set_colors(dflt_alert_clrs)                #add default alert colors to theme
        alrt_clrs_cfg = {key: key for key in dflt_alert_clrs.keys()}    #convert color defs to names for use in config
        self.set_alert_colors(alrt_clrs_cfg)                            #set the config values for the colors

    def len(self):
        """function counts the number of set attributes and returns how many are set. Intended to emulate
        other python len() functions like len(my_dict) or len(my_tuple). An attribute is considered "set"
        if the value is not None.
        
        :returns: num set attributes
        :rtype: `int`
        """
        tmp_count = 0       #temp count of any filled fields
        tmp_count += len(self.fonts)
        tmp_count += len(self.colors)
        tmp_count += len(self.images)

        return tmp_count

    def clear(self):
        """function clears out all class attributes and sets to None"""
        self.fonts.clear()
        self.colors.clear()
        self.images.clear()

    def set_colors(self, passed_colors):
        """function sets/updates the defined theme color(s) based on the passed dict.
        
        :param passed_colors: dict of color(s) to update the theme with
        :type passed_colors: `dictionary` {color_name:#HEX_VAL}
        """
        self.colors.update(passed_colors)               #update theme colors

    def set_fonts(self, passed_fonts):
        """function sets/updates the defined theme font(s) based on the passed dict.
        
        :param passed_fonts: dict of font(s) to update the theme with
        :type passed_fonts: custom defined `font` class {font_name:`font class`}
        """
        for f in passed_fonts:                          #cycle through all passed fonts
            self.fonts.update({f.font_name:f})          #update theme font data

    def set_imgs(self, passed_img):
        """function sets/updates the defined theme images(s) based on the passed dict.
        
        :param passed_img: dict of images(s) to update the theme with
        :type passed_img: `dictionary` {img_name:`absolute_filepath`}
        """
        for k,v in passed_img.items():
            self.images.update({k : v})                 #update theme image data

    def set_alert_colors(self, passed_colors):
        """function sets the colors used in limit warnings (like the warning and/or danger limits). Function
        also updates external color refs for the assigned colors.
        
        :param passed_colors: dict of color key values to update
        :type passed_colors: `dictionary` {alert_kwarg : theme_color_name}
        """
        #--convert passed color names to uppercase. Allows for use with XML and editor attributes
        passed_colors = {k.upper(): v for k, v in passed_colors.items()}

        #--update theme values
        self.alert_FG=passed_colors.get('ALERT_FG', None)
        self.alert_warn=passed_colors.get('ALERT_WARN', None)
        self.alert_dngr=passed_colors.get('ALERT_DNGR', None)
        
        #--update the external refs
        self.upd_ext_refs('alert_FG', {'COLORS':self.alert_FG})
        self.upd_ext_refs('alert_WARN', {'COLORS':self.alert_warn})
        self.upd_ext_refs('alert_DNGR', {'COLORS':self.alert_dngr})

    def upd_ext_refs(self, ele_name, ext_refs):
        """function updates the external theme refs for theme objects. As a reminder, these are the
        external named objects that use one of the defined theme values. For example, if a static label
        uses a color named "FRGND", then the colors_ext_ref dict should have that static label's name 
        included associated with color "FRGND". The self.colors_ext_ref entry would look like {`label_name`:`FRGND`}
        NOTE: the actual tkinter reference isn't needed for these objects. The user-assigned name is actually
        much more helpful when generating error messages.

        :param ele_name: element name using the external reference
        :type ele_name: `string`
        :param ext_refs: dict of theme references to update
        :type ext_refs: `dictionary` {theme_object:theme_object_ref_name}  
        """
        if ext_refs is not None:
            for k, v in ext_refs.items():   #cycle through the passed dict of used refs
                if k == 'COLORS': self.colors_ext_ref.update({ele_name: v})     #update colors external refs
                elif k == 'FONTS': self.fonts_ext_ref.update({ele_name: v})     #update fonts external refs
                elif k == 'IMAGES': self.images_ext_ref.update({ele_name: v})   #update images external refs

    def del_ext_refs(self, ele_name):
        """function removes the named element from any external ref dicts. Typically performed when deleting
        an object in the editor
        
        :param ele_name: element name using the external reference
        :type ele_name: `string`
        """
        self.colors_ext_ref.pop(ele_name,None)
        self.fonts_ext_ref.pop(ele_name,None)
        self.images_ext_ref.pop(ele_name,None)

    def chk_ref_colors(self, clr_name):
        """function checks the external color references dict and returns a list of the named objects that
        reference that color. If color is not referenced a blank tuple is returned
        
        :param clr_name: theme definition - named color
        :type clr_name: `string`
        """
        clr_ref_names = ()      #temp ref for the list of elements that reference a color name
        for k, v in self.colors_ext_ref.items():        #cycle through all the external refs
            if clr_name in v: clr_ref_names += (k,)     #if an external ref uses the color, append to the output
        return clr_ref_names    #return the list of elements that use the named color
    
    def chk_ref_fonts(self, fnt_name):
        """function checks the external font references dict and returns a list of the named objects that
        reference that font. If font is not referenced a blank tuple is returned
        
        :param fnt_name: theme definition - named font
        :type fnt_name: `string`
        """
        fnt_ref_names = ()      #temp ref for the list of elements that reference a font name
        for k, v in self.fonts_ext_ref.items():         #cycle through all the external refs
            if fnt_name in v: fnt_ref_names += (k,)     #if an external ref uses the font, append to the output
        return fnt_ref_names    #return the list of elements that use the named font
    
    def chk_ref_imgs(self, img_name):
        """function checks the external font references dict and returns a list of the named objects that
        reference that font. If font is not referenced a blank tuple is returned
        
        :param img_name: theme definition - named image
        :type img_name: `string`
        """
        img_ref_names = ()      #temp ref for the list of elements that reference an image name
        for k, v in self.images_ext_ref.items():        #cycle through all the external refs
            if img_name in v: img_ref_names += (k,)     #if an external ref uses the image, append to the output
        return img_ref_names    #return the list of elements that use the named image

    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors
        for k,v, in self.colors.items():
            valid_color_pattern = r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"    #string to match hex color codes
            if not bool(rgx.match(valid_color_pattern, v)):                 #check if color hex code is valid or not
                tmp_err_list.update({k:'Defined hex color code "' + v + '" is not valid'})   #color is not valid, append to error list
        for k,v in self.fonts.items():          #cycle through all fonts
            if v.XML_dashCFG_checkErrs():
                tmp_err_list.update({k:'Error in defining font, please check definition'})
        for k,v in self.images.items():         #cycle through all images
            if not os.path.isfile(v):   #if can't find image, then include an error in the list
                tmp_err_list.update({k:'Unable to locate image file at configured path'})
        
        if not self.chk_exist_colors(self.alert_FG):
            tmp_err_list.update({'Theme definition for "Alert_FG_color"':'Named color "' + self.alert_FG + '" not defined in theme'})
        if not self.chk_exist_colors(self.alert_warn):
            tmp_err_list.update({'Theme definition for "Alert_WARN_color"':'Named color "' + self.alert_warn + '" not defined in theme'})
        if not self.chk_exist_colors(self.alert_dngr):
            tmp_err_list.update({'Theme definition for "Alert_DANGER_color"':'Named color "' + self.alert_dngr + '" not defined in theme'})

        return tmp_err_list #return any errors

    def chk_exist_colors(self, clr_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if clr_name is None: return False
        elif clr_name in self.colors: return True
        else: return False        

    def chk_exist_fonts(self, fnt_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if fnt_name is None: return False
        elif fnt_name in self.fonts: return True
        else: return False   

    def chk_exist_imgs(self, img_name):
        """function checks if color is defined in theme dictionary. Returns true if it is"""
        if img_name is None: return False
        elif img_name in self.images: return True
        else: return False   

class dash_font:
    def __init__(self, font_name, **kwargs):
        """Configuration class for theme fonts"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.font_name = font_name
        self.typeface = kwargs.get('TYPEFACE', 'Helvetica') #font typeface
        self.point = int_str(kwargs.get('POINT', 36))       #font point size
        self.bold = bool_str(kwargs.get('BOLD', False))     #font is bolded
        self.italic = bool_str(kwargs.get('ITALIC', False)) #font is italicized
        self.undrline = bool_str(kwargs.get('UNDERLINE', False)) #font is underlined
        self.pad = int_str(kwargs.get('PAD', 5))            #padding around text (if padded)

        #--pre-build the font tuple for easy access elsewhere in the program
        self.fnt_tup = None                                 #assembled font tuple
        self.build_font_tpl()                               #build font tuple

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('typeface', 'point', 'pad')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = ('fnt_tup')

    def build_font_tpl(self):
        """function builds an appropriate font tuple that is typical of the format
        used in various tkinter inputs. The tupple is then stored in a class attribute."""
        #tuple format is (family, size, weight, slant)
        self.fnt_tup = (self.typeface,
                        str(self.point),
                        ('bold' if self.bold else 'normal'),
                        ('italic' if self.bold else 'roman'))

    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        errs = False
        fnt_dict = {'family': self.fnt_tup[0],
                         'size': self.fnt_tup[1],
                         'weight':self.fnt_tup[2],
                         'slant':self.fnt_tup[3]}   #build font option dict
        try: myfont = tkFont.Font(**fnt_dict)       #try to define font object using options
        except: errs = True                         #if unable to, then return that there is an error
        return errs

class CAN_core:
    def __init__(self, **kwargs):
        """The core CAN class that contains all the functions for handling
        CAN bus communication. Additionally includes the functions for parsing
        the XML configuration file that contains the CAN configurations

        :param base_PID: CAN PID of the device itself
        :type base_PID: integer
        :param CANfilter_en: enable RX CAN filter based on defined CAN channels
        :type CANfilter_en: boolean
        :param data_ch: dictionary for display chan channels
        :type data_ch: {ch_NAME \: `CAN_ch`}
        :param CAN_rx_raw: dictionary of raw RX'd data.
        :type CAN_rx_raw: {PID \: [CAN FRAME]}
        :param periodic_RemReq: dictionary of periodic remote requests
        :type periodic_RemReq: {ch_NAME \: task}
        :param CAN_pri: reference for instanced CAN bus object
        :type CAN_pri: `can.interface.Bus`
        :param CAN_rxNotifier:
            CAN RX notifier object assigned to `self.CAN_msg_rx` to handle processing of any
            RX'd CAN messages
        :type CAN_rxNotifier: `CAN_core` class method
        """
        self.base_PID = None    #CAN PID of the dash itself
        self.rx_filter = None   #enable RX CAN filter based on defined CAN channels
        self.data_ch = {}       #dictionary for display chan channels. Format is {ch_NAME : class[CAN_ch]}

        #-----external reference dicts: contains where/which named elements that reference CAN channel objects
        self.CAN_CH_ext_ref = {}
    
    def set_dflt_cfg(self):
        """function sets the default values for the editor config"""
        self.base_PID = sys_CAN_base_PID
        self.rx_filter = False

    def upd_cfg(self, **kwargs):
        """ function sets attributes based on the passed KWARGs. All KWARGs have default values
        for typical display values. If kwarg is not passed, the value is not updated

        :param kwargs: dict of class inputs
        :type kwargs: any type that can be typecast to string
        """
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        if 'BASE_PID' in kwargs: self.base_PID = kwargs.get('BASE_PID')
        if 'RX_FILTER' in kwargs: self.rx_filter = bool_str(kwargs.get('RX_FILTER'))

    def len(self):
        """function counts the number of set attributes and returns how many are set. Intended to emulate
        other python len() functions like len(my_dict) or len(my_tuple). An attribute is considered "set"
        if the value is not None.
        
        :returns: num set attributes
        :rtype: `int`
        """
        tmp_count = 0   #temp count of any filled fields
        if self.base_PID is not None: tmp_count += 1
        if self.rx_filter is True: tmp_count += 1
        tmp_count += len(self.data_ch)
        return tmp_count
    
    def clear(self):
        """function clears out all class attributes and sets to None"""
        self.data_ch.clear()
        self.base_PID = None
        self.rx_filter = None
    
    def set_CAN_ch(self, passed_ch):
        """function updates the data_ch dictionary of stored chan channles with the passed `CAN_ch` class object.
        This is typically used when updating configs but also is useful when first storing/defining new configs.

        :param passed_ch: can channel data class
        :type passed_ch: `CAN_ch` class
        """
        for ch in passed_ch:
            self.data_ch.update({ch.name : ch})             #add or update CANch data
    
    def upd_ext_refs(self, ele_name, ext_refs):
        """function updates the external theme refs for theme objects. As a reminder, these are the
        external named objects that use one of the defined theme values. For example, if a data label
        uses a CAN channel named "RPM", then the CAN_CH_ext_ref dict should have that data label's name 
        included associated with CAN_ch "RPM". The self.CAN_CH_ext_ref entry would look like {`label_name`:`RPM`}
        NOTE: the actual tkinter reference isn't needed for these objects. The user-assigned name is actually
        much more helpful when generating error messages.

        :param ele_name: element name using the external reference
        :type ele_name: `string`
        :param ext_refs: dict of theme references to update
        :type ext_refs: `dictionary` {theme_object:theme_object_ref_name}  
        """
        if ext_refs is not None:
            for k, v in ext_refs.items():
                if k == 'CAN_CH': self.CAN_CH_ext_ref.update({ele_name:v})  #update CAN_ch external refs

    def del_ext_refs(self, ele_name):
        """function removes the named element from any external ref dicts. Typically performed when deleting
        an object in the editor
        
        :param ele_name: element name using the external reference
        :type ele_name: `string`
        """
        self.CAN_CH_ext_ref.pop(ele_name,None)

    def chk_ref_CANch(self, ch_name):
        """function checks the external CAN channel references dict and returns a list of the named objects that
        reference that CAN channel. If a CAN channel is not referenced, a blank tuple is returned

        :param clr_name: theme definition - named color
        :type clr_name: `string`
        """
        ch_ref_names = ()      #temp ref for the list of elements that reference a CAN channel name
        for k, v in self.CAN_CH_ext_ref.items():        #cycle through all the external refs
            if ch_name in v: ch_ref_names += (k,)       #if an external ref uses the CAN channel, append to the output
        return ch_ref_names    #return the list of elements that use the named CAN channel
    
    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        if self.base_PID is None or self.base_PID == '': tmp_err_list.update({'Base_PID':'No base PID is defined and is required'})
        if self.rx_filter is None or self.rx_filter == '': tmp_err_list.update({'RX_Filter':'CAN RX message filter can be set to true or false but is undefined'})

        for v in self.data_ch.values():                     #cycle through all CAN channels
            tmp_err_list.update(v.XML_dashCFG_checkErrs())  #and add any errors

        return tmp_err_list

    def chk_exist_CANch(self, ch_name):
        """function checks if CAN data channel is currently defined
        
        :param ch_name: defined name for can channel
        :type ch_name: `string`
        :returns: can channel name is defined
        :rtype: `boolean` - TRUE if channel is defined
        """
        if ch_name is None: return False
        elif ch_name in self.data_ch: return True
        else: return False   

class CAN_ch:
    def __init__(self, **kwargs):
        """The CAN data channel class that contains parameters for processing inputs from a CAN PID"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}      #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        #-----control params
        self.name = kwargs.get('NAME', None)                    #channel name
        self.PID = kwargs.get('PID', 0x00)                      #CAN data PID
        self.ext = bool_str(kwargs.get('EXT', False))           #extended CAN frame
        self.dlc = int_str(kwargs.get('DLC', 8))                #expected number of frames

        #-----remote request
        self.rem_req = bool_str(kwargs.get('REM_REQ', False))   #PID requires remote request
        self.req_freq = int_str(kwargs.get('REQ_FREQ', None))   #frequency for request - in ms

        #-----math conversion and value
        #NOTE: the frame offset for the 0-index isn't needed here or when generating the config. that's handled at the dash
        self.frames = list_str(kwargs.get('FRAMES', 8), 0)      #list of frames used to calculating decimal value
        self.scalar = int_str(kwargs.get('SCALAR', 1))          #scalar to apply after multiplying
        self.offset = int_str(kwargs.get('OFFSET', 0))          #decimal offset

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('PID', 'ext', 'dlc', 'rem_req', 'req_freq', 'frames', 'scalar', 'offset')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors
        for attr, val in self.__dict__.items():
            if attr in self.fields_editorCFG:
                if (attr != 'req_freq') and ((val is None) or val == ''):
                    tmp_err_list.update({self.name +'-'+ attr:'Required value for CAN data channel is undefined'})
                elif attr == 'req_freq' and (self.rem_req == True) and ((val is None) or val == ''):
                    tmp_err_list.update({self.name +'-'+ attr:'Remote request is enabled but no frequency is defined'})
        return tmp_err_list #return error list

class dash_page:
    '''Configuration class to store page elements and the canvas reference object to edit'''
    def __init__(self, **kwargs):
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.name = kwargs.get('NAME', 0)                   #frame name
        self.level = kwargs.get('LEVEL', 0)                 #frame level
        self.parent = kwargs.get('PARENT', 'MASTER')        #named parent frame - default base
        self.type = kwargs.get('TYPE', 'GAGUE')             #frame type
        self.bg_clr = kwargs.get('BG_CLR', None)            #named color for background (see theme class)
        self.bg_img = kwargs.get('BG_IMG', None)            #named image for background (see theme class)
        self.width = kwargs.get('WIDTH', dash_xSz)
        self.height = kwargs.get('HEIGHT', dash_ySz)
        if self.width is None: self.width = dash_xSz
        if self.height is None: self.height = dash_ySz

        self.Lbl_stc = {}   #dict of static labels. Format is {'Name' : Label_Static_Class}
        self.Lbl_dat = {}   #dict of data labels. Format is {'Name' : Label_Data_Class}
        self.Ind_blt = {}   #dict of bullet indicators. Format is {'Name' : Ind_Bullet_Class}
        self.Ind_bar = {}   #dict of bar indicators. Format is {'Name' : Ind_Bar_Class}

        #--local vars
        self.canvObj = None     #canvas object for reference
        self.master_ref = None  #reference back to the master window > needed for theme and font transformations

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('level', 'parent', 'type', 'bg_clr', 'bg_img', 'width', 'height')
        
        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def buildPages_canv(self):
        """Function creates the canvas object for the page editor. When creating the canvas object
        where dash elements are placed, it's reference is also stored locally in a class attribute
        for future use when adding new elements.

        If the current page configuration includes a background image and color, they are also
        assigned at creation.
        """
        #--shorthand refs to various config paths - primarily for reading code and var length
        thm = self.master_ref.cfg_theme             #defined themes
        cfg = self.master_ref.cfg_core              #defined core params

        frm_x = self.width or cfg.Res_x             #frame size - default to full disply size if None is defined
        frm_y = self.height or cfg.Res_y            #frame size - default to full disply size if None is defined
        frm_bg_clr = thm.colors.get(self.bg_clr)    #frame background color
        editr_frm = self.master_ref.frm_DashDisplay #master editor frame that all canvas objects are displayed in

        self.canvObj = tk.Canvas(master=editr_frm, 
                                 width=frm_x, 
                                 height=frm_y,
                                 borderwidth=0,
                                 highlightthickness=0,
                                 bg=frm_bg_clr)              #create canvas for elements
        
        frm_bg_img = self.master_ref.cfg_theme.images.get(self.bg_img)  #get frame background image path
        if frm_bg_img is not None:
            img = addImg(self.canvObj, frm_bg_img)  #add background image
            self.canvObj.bg_img = img               #add/update image to canvas element dict to prevent trash collection
        
        self.upd_page_def_refs()                    #update external refs
    
    def update_page(self):
        """function updates the various editor canvas object(s) using their own (class specific) update
        function so their visual display matches their curent configuraiton data.
        
        Additionally, function updates the external_ref dicts for theme references related to the page
        attributes (IE background color, background image, etc.)"""
        
        for elm in self.Lbl_stc.values(): elm.upd_editor_obj()  #update all static labels
        for elm in self.Lbl_dat.values(): elm.upd_editor_obj()  #update all data labels
        for elm in self.Ind_blt.values(): elm.upd_editor_obj()  #update all bullet indicators
        for elm in self.Ind_bar.values(): elm.upd_editor_obj()  #update all bar indicators
        self.upd_page_def_refs()                                #update any page refs

    def upd_config(self, kwargs):
        """function updates configuration values based on the passed kwargs
        
        :param kwargs: page attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)
    
    def update_eleCfg(self, passed_eles):
        """function updates the contained dash element dictionaries based on the dict of passed element(s).
        The passed dict can consiste of elements of various types and assignment to the appropriate
        definition is handled here.
        
        :param passed_eles: page editor widgets to add or update
        :type passed_eles: `dict` formatted {element_name:`element class`} - Example of an element class instance would be `Label_Static`
        """
        for k, v in passed_eles.items():
            match v:
                case Label_Static():
                    self.Lbl_stc.update({k:v})   #add or update static label
                case Label_Data():
                    self.Lbl_dat.update({k:v})   #add or update data label
                case Indicator_Bullet():
                    self.Ind_blt.update({k:v})   #add or update bullet indicator
                case Indicator_Bar():
                    self.Ind_bar.update({k:v})   #add or update bar indicator

    def get_eleCfg(self, ele_type, ele_name):
        """function returns the dash element configuration based on the passed type and name.
        
        :param ele_type: page editor element type
        :type ele_type: defined by `DashEle_types`
        :param ele_name: element's defined name
        :type ele_name: `string`
        :returns: page element configuration
        :rtype: `element_class` - Example of an object class instance would be `Label_Static`
        """
        ele_cfg = None #element config reference
        if ele_type == DashEle_types['LBL_STAT']: ele_cfg = self.Lbl_stc[ele_name]
        elif ele_type == DashEle_types['LBL_DAT']: ele_cfg = self.Lbl_dat[ele_name]
        elif ele_type == DashEle_types['IND_BLT']: ele_cfg = self.Ind_blt[ele_name]
        elif ele_type == DashEle_types['IND_BAR']: ele_cfg = self.Ind_bar[ele_name]

        return ele_cfg

    def upd_page_def_refs(self):
        """function builds the reference dict to pass off to external references. For example, if the
        page uses colors named "FG" and "BG" the output ref_dict would be {'COLORS':(FG,BG)}. This
        will then ensure the instanced `color` theme class .external_refs dict is updated with the
        value of {page_name:color_name}"""
        colors = (self.bg_clr,)         #colors used for page
        images = (self.bg_img,)         #images used for page
        ref_dict = {'COLORS':colors,
                    'IMAGES':images}    #dict of the used references. Format is {'ref_type':(tup of named ref values)}
        upd_definition_refs(self.master_ref, self.name, ref_dict)   #update the core references
    
    def del_element(self, ele_cfg):
        """function deletes a passed element from the page. Additionally, when deleting the page element
        the external references related to that element are also removed.
        
        :param ele_cfg: passed element configuration
        :type ele_cfg: `element_class` - Example of an object class instance would be `Label_Static`
        """

        obj_name = ele_cfg.name                         #object name
        obj_objId = ele_cfg.objID                       #object refID
        obj_padID = getattr(ele_cfg, 'padID', None)     #object background pad ID
        obj_canvRef = ele_cfg.editor_canvObj            #canvas of the placed widget

        obj_canvRef.delete(obj_objId)                           #delete object from canv
        if obj_padID is not None: obj_canvRef.delete(obj_padID) #delete BG pad if defined
        del_definition_refs(self.master_ref, obj_name)          #delete external refs associated with the element
        match ele_cfg:                                          #match to appropriate type and delete from config dict
            case Label_Static(): self.Lbl_stc.pop(obj_name)
            case Label_Data(): self.Lbl_dat.pop(obj_name)
            case Indicator_Bullet(): self.Ind_blt.pop(obj_name)
            case Indicator_Bar(): self.Ind_bar.pop(obj_name)
    
    def del_page_ext_refs(self):
        """function deletes all external refs for page elements, in preparation for deleting a page. Additionally
        cleans up any page related external references (like background color and image)"""

        del_definition_refs(self.master_ref, self.name) #page references
        for stat in self.Lbl_stc.keys(): del_definition_refs(self.master_ref, stat) #static labels
        for dat in self.Lbl_stc.keys(): del_definition_refs(self.master_ref, dat) #data labels
        for blt in self.Lbl_stc.keys(): del_definition_refs(self.master_ref, blt) #bullet indicators
        for bar in self.Lbl_stc.keys(): del_definition_refs(self.master_ref, bar) #bar indicators
    
    def XML_dashCFG_checkErrs(self):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors
        
        #--check core page properties
        if self.bg_clr is None: tmp_err_list.update({self.name +'-BG_Color':'Color not defined'})
        else:
            if not self.master_ref.cfg_theme.chk_exist_colors(self.bg_clr):
                tmp_err_list.update({self.name +'-BG_Color':'Named color "' + self.bg_clr + '" not defined in theme'})
        if self.bg_img is not None:
            if not self.master_ref.cfg_theme.chk_exist_imgs(self.bg_img):
                tmp_err_list.update({self.name +'-BG_Image':'Named image "' + self.bg_img + '" not defined in theme'})
        if self.width is None: tmp_err_list.update({self.name +'-Width':'Required value is undefined'})
        if self.height is None: tmp_err_list.update({self.name +'-Height':'Required value is undefined'})

        #--cycle through all the various page elements
        for v in self.Lbl_stc.values(): tmp_err_list.update(v.XML_dashCFG_checkErrs(self.name))
        for v in self.Lbl_dat.values(): tmp_err_list.update(v.XML_dashCFG_checkErrs(self.name))
        for v in self.Ind_blt.values(): tmp_err_list.update(v.XML_dashCFG_checkErrs(self.name))
        for v in self.Ind_bar.values(): tmp_err_list.update(v.XML_dashCFG_checkErrs(self.name))

        return tmp_err_list #return error list

class Label_Static:
    '''Configuration class for static label types'''
    def __init__(self, **kwargs):
        """widget creation args"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.text = kwargs.get('TEXT', None)                #label text
        self.x0 = int_str(kwargs.get('X0', 0))              #position - X0
        self.y0 = int_str(kwargs.get('Y0', 0))              #position - Y0
        self.fill = kwargs.get('FILL', False)               #foreground (fill) color

        """configuration args"""
        self.name = kwargs.get('NAME', None)                #label name
        self.font = kwargs.get('FONT', None)                #Named font for label (see themes class)
        self.pad = bool_str(kwargs.get('PAD', False))       #text is padded
        self.clr_bg = kwargs.get('CLR_BG', False)           #foreground color

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations

        #-----local vars
        self.objID = None           #self canvas object reference ID
        self.padID = None           #background padding object reference ID
        self.editor_canvObj =None   #canvas ref where the editor object is placed -> used for editor updates
        self.wgtCtl = None          #bindings for editor control

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('text', 'x0', 'y0', 'fill', 'font', 'pad', 'clr_bg')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)                    #update config
    
    def editor_upd_config(self, passed_args):
        """function updates the visual state and stored configuration of a dash element based on
        the passed arguments. This is typically used when changing the element via the editor.
        
        :param passed_args: element attributes to update
        :type passed_args: `dict` formatted {kwarg_name:value}
        """
        #condition coords: needed for manual editor updating
        x=passed_args.get('x0'); y=passed_args.get('y0')
        if x=='' or x==None: passed_args.update({'x0':0})
        if y=='' or y==None: passed_args.update({'y0':0})
        xn = passed_args.get('x0',0); yn = passed_args.get('y0',0)  #updated coords
        dx = xn - self.x0; dy = yn - self.y0                        #calculate ammount moved
        self.upd_config(passed_args)                                #update class configuration data
        self.upd_editor_obj(dx, dy)                                 #update editor canvas object
        self.upd_ele_def_refs()                                     #update core references (like fonts, colors, etc)
    
    def upd_editor_obj(self, dx=0, dy=0):
        """function updates the canvas object that is in the dash editor. Also handles moving
        and object via the "delta" or change in position arguments. The remainder of the element
        properties are taken from the elemtn config.
        
        :param dx: (optional) change in x position - Default 0
        :type dx: `int` in pixels
        :param dy: (optional) change in y position - Default 0
        :type dy: `int` in pixels
        """
        temp_kwargs = self.get_edtr_wgt_kwargs(False)               #get widget kwargs from config args - NO PAD kwargs
        temp_kwargs.pop('x0'); temp_kwargs.pop('y0')                #coords handled separately - pop off
        self.editor_canvObj.itemconfigure(self.objID, temp_kwargs)  #update canvas object props
        self.editor_canvObj.move(self.objID, dx, dy)                #update primary element position
        self.upd_pad_obj()                                          #update background pad object AFTER any primary object updates

    def upd_pad_obj(self):
        """function updates the background pad object, if set. This includes moving the position when a dash
        element is moved/updated as well as any color changes.
        
        Note, that when changing position, the choice to delete and re-building the canvas element (vs just
        updating it's properties) was made because when deleting/re-making any change in size of the parent 
        object is automatically accounted for. The background pad oject is programatically generated based on
        the size of the parent object. Deleting+re-making allows an easier re-scaling on font change or value
        change and then also inherently adjusts for position and all the "expected" changes as well.
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        try: pad_clr = thm_clrs[self.clr_bg]    #try to get pad color
        except:  pad_clr = None                 #if default or invalid color, then set to none

        #--check if the pad has been enabled/disabled
        if self.pad==False and self.padID is not None:              #if pad option was un-checked
            self.padID = elePad_delete(self.editor_canvObj, self.padID)     #then delete pad object
        elif self.pad==True and self.padID is None:                 #if pad objection was checked
            if pad_clr is None: pass    #do nothing if no color is defined
            else:                       #there is a color defined
                self.padID = elePad_create(self.editor_canvObj, self.objID, pad_clr)    #then create the pad object - with the specified color
        elif self.pad==True and self.padID is not None:             #if there is a valid background pad
            self.padID = elePad_delete(self.editor_canvObj, self.padID)             #then delete pad object
            self.padID = elePad_create(self.editor_canvObj, self.objID, pad_clr)    #and rebuild
        
        self.wgtCtl.upd_refs()  #update control bindings after changes have been made
    
    def get_edtr_wgt_kwargs(self, inc_pad=True):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        thm_fnts = self.master_ref.cfg_theme.fonts
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'text': self.text,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'font': thm_fnts[self.font].fnt_tup,  #transform from font name to tuple
                      'anchor':tk.NW}

        if inc_pad == True:                     #include pad kwags with output
            try: color = thm_clrs[self.clr_bg]  #if a valid color is defined, go get it
            except: color = None                    #otherwise assign "None"
            out_kwargs.update({'pad':self.pad,
                               'clr_bg': color})
                    
        return out_kwargs   #retun the complete kwarg dict

    def upd_ele_def_refs(self):
        """function builds the reference dict to update the external refs for core definitions. For example,
        if the dash element uses colors named "FG" and "BG" the generated ref_dict would be {'COLORS':(FG,BG)}.
        After creating the ref dict, the external references are updated. In the above example, the "colors"
        theme defition would have its `external_refs` dict updated to include the entry for this named element
        against it's used colors.
        """
        colors = (self.fill, self.clr_bg)   #colors used for element
        fonts = (self.font,)                #fonts used for element
        ref_dict = {'COLORS':colors,
                    'FONTS':fonts}          #dict of the used references. Format is {'ref_type':(tup of named ref values)}
        upd_definition_refs(self.master_ref, self.name, ref_dict)   #update the core references  

    def XML_dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if ((attr == 'text') or (attr == 'x0') or (attr == 'y0')):
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page static label is undefined'})
                elif attr == 'font':
                    if not self.master_ref.cfg_theme.chk_exist_fonts(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-label_font':'Named font "' + val + '" not defined in theme'})
                elif attr == 'fill':
                    if not self.master_ref.cfg_theme.chk_exist_colors(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-fill_color':'Named color "' + val + '" not defined in theme'})
                elif attr == 'pad':
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page static label is undefined'})
                    if val == True and not self.master_ref.cfg_theme.chk_exist_colors(self.clr_bg):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-pad_color':'Named color "' + self.clr_bg + '" not defined in theme'})

        return tmp_err_list

class Label_Data:
    '''Configuration class for data label types'''
    def __init__(self, **kwargs):
        """widget creation args"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}  #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = int_str(kwargs.get('X0', 0))              #position - X0
        self.y0 = int_str(kwargs.get('Y0', 0))              #position - Y0
        self.fill = kwargs.get('CLR_FG', kwargs.get('FILL', False)) #foreground (fill) color
        self.font = kwargs.get('FONT', None)                #Named font for label (see themes class)
        self.max_val = kwargs.get('MAX_VAL', None)          #label text for max value - makes it easier to see/adjust in editor

        """configuration args"""
        self.name = kwargs.get('NAME', None)                #label name
        self.data_ch = kwargs.get('DATA_CH', None)          #Named data channel (see CAN class)
        self.sigdig = kwargs.get('SIGDIG', 0)               #number of significant digits
        self.pad = bool_str(kwargs.get('PAD', False))       #text is padded
        self.clr_bg = kwargs.get('CLR_BG', False)           #foreground color
        self.warn_en = bool_str(kwargs.get('WARN_EN', None))#warning is enabled
        self.lim_DngrLo = int_str(kwargs.get('LIM_DNGRLO', None))  #danger low limit
        self.lim_WarnLo = int_str(kwargs.get('LIM_WARNLO', None))  #warning low limit
        self.lim_WarnHi = int_str(kwargs.get('LIM_WARNHI', None))  #warning high limit
        self.lim_DngrHi = int_str(kwargs.get('LIM_DNGRHI', None))  #danger high limit

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations

        #-----local vars
        self.objID = None           #self canvas object reference ID
        self.padID = None           #background padding object reference ID
        self.editor_canvObj =None   #canvas ref where the editor object is placed -> used for editor updates
        self.wgtCtl = None          #bindings for editor control

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'fill', 'font', 'max_val', 'data_ch', 'sigdig', 'pad', 'clr_bg', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = ('x0', 'y0', 'fill', 'font', 'data_ch', 'sigdig', 'pad', 'clr_bg', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)
    
    def editor_upd_config(self, passed_args):
        """function updates the visual state and stored configuration of a dash element based on
        the passed arguments. This is typically used when changing the element via the editor.
        
        :param passed_args: element attributes to update
        :type passed_args: `dict` formatted {kwarg_name:value}
        """
        #condition coords: needed for manual editor updating
        x=passed_args.get('x0'); y=passed_args.get('y0')
        if x=='' or x==None: passed_args.update({'x0':0})
        if y=='' or y==None: passed_args.update({'y0':0})
        xn = passed_args.get('x0',0); yn = passed_args.get('y0',0)  #updated coords
        dx = xn - self.x0; dy = yn - self.y0                        #calculate ammount moved
        self.upd_config(passed_args)                                #update class configuration data
        self.upd_editor_obj(dx, dy)                                 #update editor canvas object
        self.upd_ele_def_refs()                                     #update core references (like fonts, colors, etc)
    
    def upd_editor_obj(self, dx=0, dy=0):
        """function updates the canvas object that is in the dash editor. Also handles moving
        and object via the "delta" or change in position arguments. The remainder of the element
        properties are taken from the elemtn config.
        
        :param dx: (optional) change in x position - Default 0
        :type dx: `int` in pixels
        :param dy: (optional) change in y position - Default 0
        :type dy: `int` in pixels
        """
        temp_kwargs = self.get_edtr_wgt_kwargs(False)               #get widget kwargs from config args - NO PAD kwargs
        temp_kwargs.pop('x0'); temp_kwargs.pop('y0')                #coords handled separately - pop off
        self.editor_canvObj.itemconfigure(self.objID, temp_kwargs)  #update canvas object props
        self.editor_canvObj.move(self.objID, dx, dy)                #update primary element position
        self.upd_pad_obj()                                          #update background pad object AFTER any primary object updates

    def upd_pad_obj(self):
        """function updates the background pad object, if set. This includes moving the position when a dash
        element is moved/updated as well as any color changes.
        
        Note, that when changing position, the choice to delete and re-building the canvas element (vs just
        updating it's properties) was made because when deleting/re-making any change in size of the parent 
        object is automatically accounted for. The background pad oject is programatically generated based on
        the size of the parent object. Deleting+re-making allows an easier re-scaling on font change or value
        change and then also inherently adjusts for position and all the "expected" changes as well.
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        try: pad_clr = thm_clrs[self.clr_bg]    #try to get pad color
        except:  pad_clr = None                 #if default or invalid color, then set to none

        #--check if the pad has been enabled/disabled
        if self.pad==False and self.padID is not None:              #if pad option was un-checked
            self.padID = elePad_delete(self.editor_canvObj, self.padID)     #then delete pad object
        elif self.pad==True and self.padID is None:                 #if pad objection was checked
            if pad_clr is None: pass    #do nothing if no color is defined
            else:                       #there is a color defined
                self.padID = elePad_create(self.editor_canvObj, self.objID, pad_clr)    #then create the pad object - with the specified color
        elif self.pad==True and self.padID is not None:             #if there is a valid background pad
            '''Instead of just updating the color and position, deleting and re-building also accounts
                for the size change of a parent object. This allows re-scaling on font change or value
                change and then also inherently adjusts for position and all that good stuff too.'''
            self.padID = elePad_delete(self.editor_canvObj, self.padID)             #then delete pad object
            self.padID = elePad_create(self.editor_canvObj, self.objID, pad_clr)    #and rebuild
            
        self.wgtCtl.upd_refs()  #update control bindings after changes have been made

    def get_edtr_wgt_kwargs(self, inc_pad=True):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        thm_fnts = self.master_ref.cfg_theme.fonts
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'text': self.max_val,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'font': thm_fnts[self.font].fnt_tup,  #transform from font name to tuple
                      'anchor':tk.NW}

        if inc_pad == True:                     #include pad kwags with output
            try: color = thm_clrs[self.clr_bg]  #if a valid color is defined, go get it
            except: color = None                    #otherwise assign "None"
            out_kwargs.update({'pad':self.pad,
                               'clr_bg': color})
        
        return out_kwargs   #retun the complete kwarg dict

    def upd_ele_def_refs(self):
        """function builds the reference dict to update the external refs for core definitions. For example,
        if the dash element uses colors named "FG" and "BG" the generated ref_dict would be {'COLORS':(FG,BG)}.
        After creating the ref dict, the external references are updated. In the above example, the "colors"
        theme defition would have its `external_refs` dict updated to include the entry for this named element
        against it's used colors.
        """
        colors = (self.fill, self.clr_bg)   #colors used for element
        fonts = (self.font,)                #fonts used for element
        can_chs = (self.data_ch,)           #CAN channels used for element
        ref_dict = {'COLORS':colors,
                    'FONTS':fonts,
                    'CAN_CH':can_chs}       #dict of the used references. Format is {'ref_type':(tup of named ref values)}
        upd_definition_refs(self.master_ref, self.name, ref_dict)   #update the core references  

    def XML_dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'sigdig'):
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page data label is undefined'})
                elif attr == 'font':
                    if not self.master_ref.cfg_theme.chk_exist_fonts(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-label_font':'Named font "' + val + '" not defined in theme'})
                elif attr == 'fill':
                    if not self.master_ref.cfg_theme.chk_exist_colors(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-fill_color':'Named color "' + val + '" not defined in theme'})
                elif attr == 'data_ch':
                    if not self.master_ref.cfg_CAN.chk_exist_CANch(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-CAN_ch':'Named CAN channel "' + val + '" not defined in theme'})
                elif attr == 'pad':
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page data label is undefined'})
                    if val == True and not self.master_ref.cfg_theme.chk_exist_colors(self.clr_bg):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-pad_color':'Named color "' + self.clr_bg + '" not defined in theme'})
                elif attr == 'warn_en':
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page data label is undefined'})
                    if val == True:
                        if self.lim_DngrLo is None or self.lim_DngrLo == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Danger_Lo':'Warning color changing enabled and limit is not defined'})
                        if self.lim_WarnLo is None or self.lim_WarnLo == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Warn_Lo':'Warning color changing enabled and limit is not defined'})
                        if self.lim_WarnHi is None or self.lim_WarnHi == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Warn_Hi':'Warning color changing enabled and limit is not defined'})
                        if self.lim_DngrHi is None or self.lim_DngrHi == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Danger_Hi':'Warning color changing enabled and limit is not defined'})

        return tmp_err_list

class Indicator_Bullet:
    '''Configuration class for bullet indicator types'''
    def __init__(self, **kwargs):
        """widget creation args"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}      #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = int_str(kwargs.get('X0', 0))                  #position - X0
        self.y0 = int_str(kwargs.get('Y0', 0))                  #position - Y0
        self.size = int_str(kwargs.get('SIZE', None))           #bullet indicator size
        self.lim_lo = int_str(kwargs.get('LIM_LO', None))       #lo limit
        self.lim_hi = int_str(kwargs.get('LIM_HI', None))       #hi limit
        
        """configuration args"""
        self.name = kwargs.get('NAME', None)                    #label name
        self.data_ch = kwargs.get('DATA_CH', None)              #Named linked CAN channel (see CAN class)
        self.clr_lo = kwargs.get('CLR_LO', None)                #foreground (fill) color - lo limit
        self.clr_hi = kwargs.get('CLR_HI', None)                #foreground (fill) color - hi limit
        self.outln = kwargs.get('OUTLN', None)                  #named outline color (see theme class)

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations

        #-----local vars
        self.objID = None           #canvas object reference ID - once created
        self.editor_canvObj =None   #canvas ref where the editor object is placed -> used for editor updates
        self.wgtCtl = None          #bindings for editor control

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'size', 'data_ch', 'lim_lo', 'lim_hi', 'clr_lo', 'clr_hi', 'outln')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)
    
    def editor_upd_config(self, passed_args):
        """function updates the visual state and stored configuration of a dash element based on
        the passed arguments. This is typically used when changing the element via the editor.
        
        :param passed_args: element attributes to update
        :type passed_args: `dict` formatted {kwarg_name:value}
        """
        #condition coords: needed for manual editor updating
        x=passed_args.get('x0'); y=passed_args.get('y0'); sz = passed_args.get('size')
        if x=='' or x==None: passed_args.update({'x0':0})
        if y=='' or y==None: passed_args.update({'y0':0})
        if sz=='' or sz==None: passed_args.update({'size':0})

        self.upd_config(passed_args)                #update configuration data
        self.upd_editor_obj()                       #update editor canvas object
        self.upd_ele_def_refs()                     #update core references (like fonts, colors, etc)
    
    def upd_editor_obj(self):
        """function updates the canvas object that is in the dash editor. Also handles moving
        and object via the "delta" or change in position arguments. The remainder of the element
        properties are taken from the elemtn config.
        
        :param dx: (optional) change in x position - Default 0
        :type dx: `int` in pixels
        :param dy: (optional) change in y position - Default 0
        :type dy: `int` in pixels
        """
        temp_kwargs = self.get_edtr_wgt_kwargs()    #get widget kwargs from config args
        x0 = temp_kwargs.pop('x0'); y0 = temp_kwargs.pop('y0')      #pop off coords/size
        x1 = temp_kwargs.pop('x1'); y1 = temp_kwargs.pop('y1')
        self.editor_canvObj.itemconfigure(self.objID, temp_kwargs)  #update canvas object props
        self.editor_canvObj.coords(self.objID, x0, y0, x1, y1)      #update position/size

    def get_edtr_wgt_kwargs(self):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'x1': self.x0 + self.size,
                      'y1': self.y0 + self.size,
                      'fill': thm_clrs[self.clr_lo],    #transform from keyword to color HEX code
                      'outline': thm_clrs[self.outln]}  #transform from keyword to color HEX code
        
        return out_kwargs   #retun the complete kwarg dict
    
    def upd_ele_def_refs(self):
        """function builds the reference dict to update the external refs for core definitions. For example,
        if the dash element uses colors named "FG" and "BG" the generated ref_dict would be {'COLORS':(FG,BG)}.
        After creating the ref dict, the external references are updated. In the above example, the "colors"
        theme defition would have its `external_refs` dict updated to include the entry for this named element
        against it's used colors.
        """
        colors = (self.clr_hi, self.clr_lo, self.outln)     #colors used for element
        can_chs = (self.data_ch,)                           #CAN channels used for element
        ref_dict = {'COLORS':colors,
                    'CAN_CH':can_chs}       #dict of the used references. Format is {'ref_type':(tup of named ref values)}
        upd_definition_refs(self.master_ref, self.name, ref_dict)   #update the core references  

    def XML_dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'size') or (attr =='lim_lo') or (attr == 'lim_hi'):
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page bullet indicator is undefined'})
                elif attr == 'font':
                    if not self.master_ref.cfg_theme.chk_exist_fonts(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-label_font':'Named font "' + val + '" not defined in theme'})
                elif (attr == 'clr_lo') or (attr == 'clr_hi') or (attr == 'outln'):
                    if not self.master_ref.cfg_theme.chk_exist_colors(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-fill_color':'Named color "' + val + '" not defined in theme'})
                elif attr == 'data_ch':
                    if not self.master_ref.cfg_CAN.chk_exist_CANch(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-CAN_ch':'Named CAN channel "' + val + '" not defined in theme'})

        return tmp_err_list

class Indicator_Bar:
    '''Configuration class for bar indicator types'''
    def __init__(self, **kwargs):
        """widget creation args"""
        kwargs = {k.upper(): v for k, v in kwargs.items()}      #convert kwarg names to uppercase. Allows for use with XML and editor attributes
        self.x0 = int_str(kwargs.get('X0', 0))                  #position - X0
        self.y0 = int_str(kwargs.get('Y0', 0))                  #position - Y0
        self.width = int_str(kwargs.get('WIDTH', None))         #bar width
        self.height = int_str(kwargs.get('HEIGHT', None))       #bar height
        self.fill = kwargs.get('FILL', None)                    #foreground (fill) color
        self.outln = kwargs.get('OUTLN', None)                  #named outline color (see theme class)

        """configuration args"""
        self.name = kwargs.get('NAME', None)                    #label name
        self.data_ch = kwargs.get('DATA_CH', None)              #Named linked CAN channel (see CAN class)
        self.ordr = kwargs.get('ORDR', 'FG')                    #layer order (FG or BG)
        self.scale_lo = int_str(kwargs.get('SCALE_LO', None))   #lower bound of scale
        self.scale_hi = int_str(kwargs.get('SCALE_HI', None))   #upper bound of scale
        self.warn_en = bool_str(kwargs.get('WARN_EN', None))    #warning is enabled
        self.lim_DngrLo = int_str(kwargs.get('LIM_DNGRLO', None))  #danger low limit
        self.lim_WarnLo = int_str(kwargs.get('LIM_WARNLO', None))  #warning low limit
        self.lim_WarnHi = int_str(kwargs.get('LIM_WARNHI', None))  #warning high limit
        self.lim_DngrHi = int_str(kwargs.get('LIM_DNGRHI', None))  #danger high limit

        #-----ref vars
        self.master_ref = None      #reference back to the master window > needed for theme and font transformations

        #-----local vars
        self.objID = None           #canvas object reference ID - once created
        self.editor_canvObj =None   #canvas ref where the editor object is placed -> used for editor updates
        self.wgtCtl = None          #bindings for editor control

        #--create tupple for class attributes used to save editor XML file
        self.fields_editorCFG = ('x0', 'y0', 'width', 'height', 'fill', 'data_ch', 'outln', 'ordr', 'scale_lo', 'scale_hi', 'warn_en', 'lim_DngrLo', 'lim_WarnLo', 'lim_WarnHi', 'lim_DngrHi')

        #--create tupple for class attributes used to generate dash config file
        self.fields_dashCFG = self.fields_editorCFG
    
    def upd_config(self, kwargs):
        """function updates element configuration values based on the passed kwargs. This is
        typically used when instancing a new element.
        
        :param kwargs: element attributes to update
        :type kwargs: `dict` formatted {kwarg_name:value}
        """
        self.__dict__.update(kwargs)
    
    def editor_upd_config(self, passed_args):
        """function updates the visual state and stored configuration of a dash element based on
        the passed arguments. This is typically used when changing the element via the editor.
        
        :param passed_args: element attributes to update
        :type passed_args: `dict` formatted {kwarg_name:value}
        """
        #condition coords: needed for manual editor updating
        x=passed_args.get('x0'); y=passed_args.get('y0')
        if x=='' or x==None: passed_args.update({'x0':0})
        if y=='' or y==None: passed_args.update({'y0':0})

        w=passed_args.get('width'); h=passed_args.get('height')
        if w=='' or w==None: passed_args.update({'width':0})
        if h=='' or h==None: passed_args.update({'height':0})

        self.upd_config(passed_args)                #update configuration data
        self.upd_editor_obj()                       #update editor canvas object
        self.upd_ele_def_refs()                     #update core references (like fonts, colors, etc)
    
    def upd_editor_obj(self):
        """function updates the canvas object that is in the dash editor. Also handles moving
        and object via the "delta" or change in position arguments. The remainder of the element
        properties are taken from the elemtn config.
        
        :param dx: (optional) change in x position - Default 0
        :type dx: `int` in pixels
        :param dy: (optional) change in y position - Default 0
        :type dy: `int` in pixels
        """
        temp_kwargs = self.get_edtr_wgt_kwargs()    #get widget kwargs from config args
        x0 = temp_kwargs.pop('x0'); y0 = temp_kwargs.pop('y0')      #pop off coords/size
        x1 = temp_kwargs.pop('x1'); y1 = temp_kwargs.pop('y1')
        self.editor_canvObj.itemconfigure(self.objID, temp_kwargs)  #update canvas object props
        self.editor_canvObj.coords(self.objID, x0, y0, x1, y1)      #update position/size

    def get_edtr_wgt_kwargs(self):
        """function gets the kwargs required to create or update the editor canvas object. Returns a dict of
        parameters that's typically used to pass to tkinter functions. Optionally can include the background
        pad argument (not always used).
        
        :param inc_pad: (optional) include "background pad" arg in returned dict - Default true
        :type inc_pad: `bool` - true to include pad parameter
        :returns: dict of element kwargs
        :rtype: `dictionary` {element_kwarg_name:value}
        """
        #--shorthand refs for theme items
        thm_clrs = self.master_ref.cfg_theme.colors
        
        #--build dict with all kwargs needed to create or update editor widget
        out_kwargs = {'x0': self.x0,
                      'y0': self.y0,
                      'x1': self.x0 + self.width,
                      'y1': self.y0 + self.height,
                      'fill': thm_clrs[self.fill],          #transform from keyword to color HEX code
                      'outline': thm_clrs[self.outln]}    #transform from keyword to color HEX code
        
        return out_kwargs   #retun the complete kwarg dict
    
    def upd_ele_def_refs(self):
        """function builds the reference dict to update the external refs for core definitions. For example,
        if the dash element uses colors named "FG" and "BG" the generated ref_dict would be {'COLORS':(FG,BG)}.
        After creating the ref dict, the external references are updated. In the above example, the "colors"
        theme defition would have its `external_refs` dict updated to include the entry for this named element
        against it's used colors.
        """
        colors = (self.fill, self.outln)    #colors used for element
        can_chs = (self.data_ch,)           #CAN channels used for element
        ref_dict = {'COLORS':colors,
                    'CAN_CH':can_chs}       #dict of the used references. Format is {'ref_type':(tup of named ref values)}
        upd_definition_refs(self.master_ref, self.name, ref_dict)   #update the core references  

    def XML_dashCFG_checkErrs(self, pg_name):
        """function checks the required class attributes to see if they are set and if the set value is
        a correct format and/or reference. If it is not set, or the value is not correct for the configuration,
        then the attribute name, and an error message are added to the temporary error dict. Once complete
        this error dict is passed to the custom warning window message to indicate where in a dash configuration
        there may be issues.
        
        :param pg_name: the dash page which the element is contained on - makes for a better error message fi needed
        :type pg_name: `string`
        :returns: dict of attributes with errors
        :rtype: `dictionary` {attribute_name:"error message"}
        """
        tmp_err_list = {}   #temp dict for compiling errors

        for attr, val in self.__dict__.items():
            if attr in self.fields_dashCFG:
                if (attr == 'x0') or (attr == 'y0') or (attr == 'width') or (attr == 'height') or (attr =='ind_on') or (attr == 'ind_off') or (attr == 'ordr') or (attr == 'scale_lo') or (attr == 'scale_hi'):
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page bar indicator is undefined'})
                elif attr == 'font':
                    if not self.master_ref.cfg_theme.chk_exist_fonts(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-label_font':'Named font "' + val + '" not defined in theme'})
                elif (attr == 'fill') or (attr == 'outln'):
                    if not self.master_ref.cfg_theme.chk_exist_colors(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-fill_color':'Named color "' + val + '" not defined in theme'})
                elif attr == 'data_ch':
                    if not self.master_ref.cfg_CAN.chk_exist_CANch(val):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-CAN_ch':'Named CAN channel "' + val + '" not defined in theme'})
                elif attr == 'pad':
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page bar indicator is undefined'})
                    if val == True and not self.master_ref.cfg_theme.chk_exist_colors(self.clr_bg):
                        tmp_err_list.update({pg_name +'-'+ self.name +'-pad_color':'Named color "' + self.clr_bg + '" not defined in theme'})
                elif attr == 'warn_en':
                    if (val is None) or val == '':
                        tmp_err_list.update({pg_name +'-'+ self.name +'-'+ attr:'Required value for page bar indicator is undefined'})
                    if val == True:
                        if self.lim_DngrLo is None or self.lim_DngrLo == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Danger_Lo':'Warning color changing enabled and limit is not defined'})
                        if self.lim_WarnLo is None or self.lim_WarnLo == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Warn_Lo':'Warning color changing enabled and limit is not defined'})
                        if self.lim_WarnHi is None or self.lim_WarnHi == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Warn_Hi':'Warning color changing enabled and limit is not defined'})
                        if self.lim_DngrHi is None or self.lim_DngrHi == '':
                            tmp_err_list.update({pg_name +'-'+ self.name +'-Limit_Danger_Hi':'Warning color changing enabled and limit is not defined'})

        return tmp_err_list

#---------------------additional common classes---------------------
class wndw_notify(tk.Toplevel):
    '''custom notification window class. Fixed size window that wraps text and can handle longer messages.
    Based on passed kwargs can be one of several types. Meant to cover instances where the built-in tk 
    notification window types are not sufficient (like in the case of long messages)'''
    def __init__(self, parent, kwargs):
        super().__init__(parent)        #init as a sub-window of the parent

        #---core window options
        self.grab_set()                 #force focus on this window
        self.resizable(False,False)     #not resizable

        #---frames for grouping widgets
        self.frm_icon = tk.Frame(self); self.frm_icon.grid(row=0, column=0, padx=(20,10))           #frame space for icon
        self.frm_text = tk.Frame(self); self.frm_text.grid(row=0, column=1, padx=(0,20))            #frame space for the user text
        self.frm_ctl = tk.Frame(self); self.frm_ctl.grid(row=1, column=0, columnspan=2, pady=10)    #frame space for control buttons
        self.grid_columnconfigure(1, weight=1)  #assign the extra weight to column 1 (message text space)
        
        #---local vars for window elements
        self.type = kwargs.get('type', Popup_types['INFO']) #message display type
        txt_title = kwargs.get('title','Message')           #title bar text
        txt_msg = kwargs.get('message',None)                #message text
        self.result = None                                  #result of the user selection

        #---common elements
        #-display icon
        self.ico = tk.Label(self.frm_icon)
        self.ico.grid(row=0, column=0, sticky=tk.NSEW)
        #-dispaly text
        self.message_text = tk.Label(self.frm_text, text=txt_msg, wraplength=sys_wrap_len)
        self.message_text.grid(row=0,column=0)
        #-title bar
        self.title(txt_title)
        
        self.wndw_init()    #initialize window elements
        self.bell()         #popup/wanring notification sound
        self.wait_window()  #wait in this window until destroyed

    def wndw_init(self):
        """function initializes the correct window elements"""
        if self.type == Popup_types['INFO']: self.init_info()
        elif self.type == Popup_types['WARN']: self.init_warn()
        elif self.type == Popup_types['ERROR']: self.init_err()
        elif self.type == Popup_types['YESNO']: self.init_yesno()
        elif self.type == Popup_types['OKCNCL']: self.init_okcancel()
        else: self.init_info()

    def init_info(self):
        self.ico.config(image="::tk::icons::information")
        btn_ok = tk.Button(self.frm_ctl, text="OK", command=self.click_ack)
        btn_ok.grid(row=0,column=0)
        self.protocol("WM_DELETE_WINDOW", self.click_ack)   # Handle window close button
        
    def init_warn(self):
        self.ico.config(image="::tk::icons::warning")
        btn_ok = tk.Button(self.frm_ctl, text="OK", command=self.click_ack)
        btn_ok.grid(row=0,column=0)
        self.protocol("WM_DELETE_WINDOW", self.click_ack)   # Handle window close button

    def init_err(self):
        self.ico.config(image="::tk::icons::error")
        btn_ok = tk.Button(self.frm_ctl, text="OK", command=self.click_ack)
        btn_ok.grid(row=0,column=0)
        self.protocol("WM_DELETE_WINDOW", self.click_ack)   # Handle window close button

    def init_yesno(self):
        self.ico.config(image="::tk::icons::question")
        btn_ok = tk.Button(self.frm_ctl, text="YES", command=self.click_truthy)
        btn_ok.grid(row=0,column=0,padx=(0,20))
        btn_cncl = tk.Button(self.frm_ctl, text="NO", command=self.click_falsy)
        btn_cncl.grid(row=0,column=1)
        self.protocol("WM_DELETE_WINDOW", self.click_falsy) # Handle window close button : treat as falsy

    def init_okcancel(self):
        self.ico.config(image="::tk::icons::information")
        btn_ok = tk.Button(self.frm_ctl, text="OK", command=self.click_truthy)
        btn_ok.grid(row=0,column=0,padx=(0,20))
        btn_cncl = tk.Button(self.frm_ctl, text="CANCEL", command=self.click_falsy)
        btn_cncl.grid(row=0,column=1)
        self.protocol("WM_DELETE_WINDOW", self.click_falsy) # Handle window close button : treat as falsy

    def click_truthy(self):
        """function for any of the truthy responses like yes, etc"""
        self.result=True
        self.destroy()

    def click_falsy(self):
        """function for any of the falsy responses like No, cancel, etc"""
        self.result=False
        self.destroy()

    def click_ack(self):
        """function for any of the non-return responses like OK; just an acknowledge"""
        #default result is None, so no need to set here
        self.destroy()

class font_notify(tk.Toplevel):
    '''custom notification window class, specifically for the font check. is a re-purpose of the
    "wndw_notify" pop-up. Specifically, so that the inline links to the font archive and how-to
    webpages could be easily inserted. This is a one-trick pony, that's all.
    
    Maybe could figure out how to modify the existing custom notification but like....eh this was
    less work.'''
    def __init__(self, parent, missing_fonts):
        super().__init__(parent)                #init as a sub-window of the parent
       
        #---local vars for window elements
        self.txt_title = tk.StringVar()         #title bar text
        self.txt_msg = tk.StringVar()           #message text

        #---build window
        self.init_common()                      #load common elements
        #-display message based on if fonts are missing or not
        if len(missing_fonts) >0: self.init_missingFonts(missing_fonts)
        else: self.init_ok()
        self.title(self.txt_title.get())        #update title bar
        self.bell()                             #add popup/wanring notification sound
        self.wait_window()                      #wait in this window until destroyed

    def init_missingFonts(self, missing_fonts):
        """function builds the required messages and additional links/interfaces for when
        fonts are missing
        
        :param missing_fonts: list of missing fonts
        :type missing_fonts: [font_name, (n_font_name)]
        """
        rslt_msg = "Required fonts were not found. Please install the following fonts to ensure proper opration of the PyDash Editor:\n\n"
        for indx, f in enumerate(missing_fonts):
            rslt_msg += '['+ f + ']'   #build error message string - add fonts
            if indx != len(missing_fonts)-1: rslt_msg += ', '
        rslt_msg += '\n'

        archive_msg = 'An archive of the required fonts for PyDash can be found at the adjacent link'
        self.archive_text = tk.Label(self.frm_text, text=archive_msg, wraplen=font_msg_wrap_len)
        self.archive_text.grid(row=1,column=0)
        archive_link = tk.Label(self.frm_text, text='Required Font Archive', font=font_norm1_hyper, fg='blue', cursor="hand2")
        archive_link.grid(row=1, column=1, sticky=tk.W)
        archive_link.bind('<Button-1>', lambda event: self.open_Weblink(help_fontZip_GITlink, event))

        MS_install_msg = 'Additional information on how to install fonts on a Windows OS can be found at the adjacent link'
        self.MS_install_text = tk.Label(self.frm_text, text=MS_install_msg, wraplen=font_msg_wrap_len)
        self.MS_install_text.grid(row=2,column=0)
        MS_install_link = tk.Label(self.frm_text, text='MS how-to install fonts', font=font_norm1_hyper, fg='blue', cursor="hand2")
        MS_install_link.grid(row=2, column=1, sticky=tk.W)
        MS_install_link.bind('<Button-1>', lambda event: self.open_Weblink(help_MS_fontInstall_link, event))

        self.txt_msg.set(rslt_msg)              #update stringvar for message
        self.txt_title.set("Missing Fonts")     #update stringvar for window title

    def init_ok(self):
        """function builds the required messages and additional links/interfaces for when
        all fonts are found
        """
        rslt_msg = "Success! All fonts are installed!"

        self.txt_msg.set(rslt_msg)              #update stringvar for message
        self.txt_title.set("Success")           #update stringvar for window title

    def init_common(self):
        """function loads and displays the common message elements"""
        #---core window options
        self.grab_set()                 #force focus on this window
        self.resizable(False,False)     #not resizable

        #---frames for grouping widgets
        self.frm_icon = tk.Frame(self); self.frm_icon.grid(row=0, column=0, padx=(20,10))               #frame space for icon
        self.frm_text = tk.Frame(self); self.frm_text.grid(row=0, column=1, padx=(0,20), pady=(20,0))   #frame space for the user text
        self.frm_ctl = tk.Frame(self); self.frm_ctl.grid(row=1, column=0, columnspan=2, pady=(10,20))   #frame space for control buttons
        self.grid_columnconfigure(1, weight=1)  #assign the extra weight to column 1 (message text space)

        #-display icon
        self.ico = tk.Label(self.frm_icon)
        self.ico.grid(row=0, column=0, sticky=tk.NSEW)
        self.ico.config(image="::tk::icons::information")   #information icon
        #-dispaly text
        self.message_text = tk.Label(self.frm_text, textvariable=self.txt_msg, wraplength=sys_wrap_len)
        self.message_text.grid(row=0,column=0, columnspan=2)

        #-user interface options
        btn_ok = tk.Button(self.frm_ctl, text="OK", command=self.on_close)  #populate the OK window
        btn_ok.grid(row=0,column=0)
        self.protocol("WM_DELETE_WINDOW", self.on_close)                    # Handle window close button

    def on_close(self):
        """function is called when the close or exit buttons are selected. No action is taken."""
        self.destroy()
    
    def open_Weblink(self, link, event):
        """function handles opening a URL at the passed path
        
        :param link: the web URL to navigate to
        :type link: `string`
        :param evnt: (not used) the event information about the triggering event.
        :type evnt: `Event` tkinter object
        """
        wb.open_new_tab(link)

def sysCheck_fonts(master_ref):
    """function checks the current system fonts and informs the user if any required fonts for the
    PyDash builder to operate are missing
    
    :param master_ref: reference back to the main/master window
    :type master_ref: `tk.window` ref
    """

    avail_sys_fonts = list(tkFont.families())           #populate list of system fonts
    missing_fonts = []                                  #temp list of missing fonts
    
    for PyDash_font in PyDash_fonts:                    #loop through all required fonts
        if PyDash_font not in avail_sys_fonts:          #if they are not installed on the system
            missing_fonts.append(PyDash_font)           #add to list

    font_msg = font_notify(master_ref, missing_fonts)   #display appropriate message
        