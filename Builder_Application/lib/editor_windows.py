"""
File:       editor_windows.py
Function:   This file contains the various tkinter class definitions for secondary windows
            in the application. This is most prominent in the various menu items for editing
            the configuration definitions, but also includes things like the toplevel window
            that is displayed when adding a new widget, and other similar "new windows" that
            suppliment the primary application window
"""

from .sys import *
from .com_defs import dash_font, CAN_ch     #needed for adding fonts, CANchannels
from .com_defs import dash_page             #needed for Dash Pages
from .com_defs import DashEle_types         #needed for element processing
from .com_defs import Ele_Order             #needed for element ordering in editor
from .com_defs import Move_Page             #needed for page manipulation
from .com_defs import updPages              #needed to update pages on config changes
from .com_defs import strvar_str            #needed for the properties display and (none) stringvars
from .com_defs import tup_str               #needed for deletion error messages
from .com_defs import elePad_create         #needed for danger/warning color window
from tkinter import Text, Scrollbar         #needed for help file
from .com_defs import Label_Static, Label_Data, Indicator_Bullet, Indicator_Bar     #needed for handling properties
from .com_defs import file_open_dialogue

class wndw_Colors(tk.Toplevel):
    '''Editor window for theme colors'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Theme Colors")      #title bar
        self.resizable(False,False)     #fixed size
        self.master_ref = master

        #---references to main objects
        self.colors_ref = master.cfg_theme.colors       #reference to master theme colors dict

        self.config_window()
        self.lstbx_colors_upd()         #update defined colors
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_alt = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0)
        self.frm_alt.grid(row=0, column=1, sticky=tk.N)

        #---preview display
        self.frm_preview = tk.Frame(self, highlightthickness=0)
        self.frm_preview.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)
        self.frm_preview.rowconfigure(1, weight=1)
        self.frm_preview.columnconfigure(0, weight=1)
        lbl_preview_title = tk.Label(self.frm_preview, text="Color Preview", font=font_hdr2)
        lbl_preview_title.grid(row=0, column=0, padx=10, pady=(10,0))
        self.dmy_img = tk.PhotoImage(width=1, height=1)  #dummy image so the button size can be set in pixels
        self.obj_preview=tk.Button(self.frm_preview, image=self.dmy_img, compound='center', width=40, height=40, state=tk.DISABLED)
        self.obj_preview.grid(row=1, column=0, padx=10, pady=10)

        lbl_lstbox_colors = tk.Label(self.frm_main, text="Defined Colors", font=font_hdr2)
        lbl_lstbox_colors.grid(row=0, column=0, padx=10, pady=(10,0))
        self.lstbx_colors = tk.Listbox(self.frm_main)
        self.lstbx_colors.grid(row=1, column=0, padx=10, pady=10)
        self.lstbx_colors.bind("<<ListboxSelect>>", self.upd_preview)    #bind listbox selection to update preview on selection

        btn_clrAdd=tk.Button(self.frm_alt,text="Add Color", command=self.color_add)
        btn_clrAdd.grid(row=0, column=0, padx=10, pady=(50,0))
        btn_clrEdit=tk.Button(self.frm_alt,text="Edit Color", command=self.color_edit)
        btn_clrEdit.grid(row=1, column=0, padx=10, pady=(10,0))
        btn_clrDel=tk.Button(self.frm_alt,text="Delete Color", command=self.color_del)
        btn_clrDel.grid(row=2, column=0, padx=10, pady=10)

    def upd_preview(self, event):
        """function called when listbox item is clicked to update the preview
        
        :param evnt: the event information about the triggering event.
        :type evnt: `Event` tkinter object
        """
        selected_clr = event.widget.curselection()                 #get the selected color
        if selected_clr:
            sel_clr = list(self.colors_ref.keys())[selected_clr[0]]     #selected color key
            sel_clr_val = self.colors_ref.get(sel_clr)                  #selected color value
            self.obj_preview.configure(bg=sel_clr_val)                  #update the preview object

    def lstbx_colors_upd(self):
        """function updates the listbox that shows the defined configurations"""
        self.lstbx_colors.delete(0,tk.END)                      #clear any existing entries
        
        if (self.colors_ref is None): pass                      #no values to populate
        else:
            for key in self.colors_ref.keys():
                self.lstbx_colors.insert(tk.END, key)           #populate with current list
    
    def color_add(self):
        """function calls the configuration editor window for creating a new element, no config is passed"""
        self.color_modify(None)

    def color_edit(self):
        """function calls the configuration editor window for editing an existing element"""
        if(len(self.lstbx_colors.curselection()) == 0):
            messagebox.showwarning("Warning", "No Color Selected. Please select a color to edit.")
        else:
            sel_index = self.lstbx_colors.curselection()        #selected value, tupple
            sel_clr = list(self.colors_ref.keys())[sel_index[0]]     #selected color key
            sel_clr_dict = {sel_clr: self.colors_ref.get(sel_clr)}   #selected color dict
            self.color_modify(sel_clr_dict)

    def color_modify(self, sel_color):
        """function opens the configuration editor window for editing definitions. After the config
        has been modified in another window, it also updates the core definitions and also updates 
        any instanced elements that reference the definition. For example, if an existing color is
        modified, the elements in the dash editor that reference (the modified color def) will be
        updated to display the new color.
        
        :param sel_color: a passed color definition to update
        :type sel_color: `dash_color` definition
        """

        new_color = self.color_props(self, sel_color)
        self.grab_set() #force re-focus on current window
            
        if(new_color.result is not None):               #if a record was created or modified
            self.colors_ref.update(new_color.result)    #add/update dict
            self.lstbx_colors_upd()                     #update listbox
            updPages(self.master_ref)                   #update all pages with edited property

    def color_del(self):
        """function removes the configuration definition. Additionally, before removing, the external
        references of the configuration to be removed are checked. If an editor element references
        the configuration, a warning is displayed and it is not removed."""

        if(len(self.lstbx_colors.curselection()) == 0):
            messagebox.showwarning("Warning", "No Color Selected. Please select a color to delete.")
        else:
            sel_index = self.lstbx_colors.curselection()                        #selected value, tupple
            sel_clr = list(self.colors_ref.keys())[sel_index[0]]                #selected color key
            color_ext_refs = self.master_ref.cfg_theme.chk_ref_colors(sel_clr)  #check if color is used somewhere
            if len(color_ext_refs) == 0:                #if no refs are returned, then not used
                self.colors_ref.pop(sel_clr)                #remove selected color from dict       
                self.lstbx_colors_upd()                     #update listbox
            else:
                msg_str = "Cannot delete! Color is referenced in the following named elements:\n"
                msg_str += tup_str(color_ext_refs)
                messagebox.showwarning("Warning", msg_str)

    class color_props(tk.Toplevel):
        """toplevel window for modifing font configuration definitions. When instancing, if no configuration
        information is passed, all fields are left blank. If a configuration is passed, the available entry fields
        are populated with the passed values for modification."""
        def __init__(self, master, passed_color):
            super().__init__(master)
            self.grab_set()                     #force focus
            self.title("Color Values")          #title bar
            self.resizable(False,False)         #fixed size
            self.result = {}                    #var to hold updated color

            self.color_name = tk.StringVar()    #stringvar for color name
            self.RGB = tk.StringVar()           #stringvar for color RGB code hex
            
            #---Entry widgets
            #-color name
            lbl_color_name = tk.Label(self, text="Color Name", font=font_hdr2)
            lbl_color_name.grid(row=0, column=0, padx=10, pady=(10,0))
            entry_color_name = tk.Entry(self, width=30, textvariable=self.color_name)
            entry_color_name.grid(row=0, column=1, padx=10, pady=(10,0))

            #-color preview
            self.btn_color=tk.Button(self, width=2, state=tk.DISABLED)              #button for visual color display
            self.btn_color.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
            self.color_hex = tk.Label(self, font=font_hdr2, textvariable=self.RGB)  #color hex code
            self.color_hex.grid(row=1, column=1, padx=10, pady=10)

            #-color selector
            btn_selcolor=tk.Button(self,text="Choose Color", command=self.choose_color)
            btn_selcolor.grid(row=1, column=0, padx=10, pady=10)

            #---control buttons
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_cntl.grid(row=4, column=0, columnspan=2)
            btn_save=tk.Button(self.frm_cntl,text="Save Color", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

            #---update fields if editing an existing entry
            if passed_color is not None:    #if was passed a color, then populate fields
                entry_color_name.configure(state=tk.DISABLED)           #disable the reference name input
                self.color_name.set(next(iter(passed_color.keys())))
                self.RGB.set(passed_color[self.color_name.get()])
                self.btn_color.config(bg=self.RGB.get())                #update color indicator to match

            self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle window close button
            self.wait_window()  #wait in this window until destroyed
        
        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the configuraiton definition. Additionally, when saving, required fields for the
            definition are checked to ensure they are populated/valid. If they are invalid, then a warning
            is displayed and the configuration is not allowed to be saved."""

            if self.missing_req_fields() :
                messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
            else:
                self.result = {self.color_name.get(): self.RGB.get()} #set new color value
                self.destroy()

        def on_close(self): #make no changes
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

        def missing_req_fields(self):
            """function checks to ensure that all required fields for the configuration defintion are populated.
            
            :returns: required fields are missing status
            :rtype: `bool` - true if required fields are missing
            """
            #--create tuple of required fields
            req_fields = (self.color_name.get() or None,)
            req_fields += (self.RGB.get() or None,)

            if None in req_fields: return True  #if at least one required field is missing, return true
            else: return False

        def choose_color(self):
            """function displays the color chooser dialog for defining the RGB hex values of a color"""
            sel_color = colorchooser.askcolor(title="Select a color")
            if sel_color[1]:
                self.RGB.set(sel_color[1].upper())          #set RGB hex value
                self.btn_color.config(bg=self.RGB.get())    #update color indicator to match

class wndw_AlertColors(tk.Toplevel):
    """Editor window for setting/adjusting the alert colors"""
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Alert Colors")      #title bar
        self.resizable(False,False)     #fixed size
        self.master_ref = master

        #---working vars for colors. Dicts contain the named color and the value
        self.alert_FG={}      #named color for FG (text) when alert color-changing is enabled
        self.alert_warn={}    #warning named color for BG when alert color-changing is enabled
        self.alert_dngr={}    #danger named color for BG when alert color-changing is enabled
    
        #---references to main objects
        self.theme_ref = master.cfg_theme   #reference to master theme instance

        self.load_settings()    #load values or set defaults
        self.config_window()    #build display frame
        self.upd_preview()      #update view with initial values
        self.wait_window()      #wait in this window until destroyed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        #--frame layout
        self.frm_main = tk.Frame(self, highlightthickness=0)    #main frame with labels and buttons
        self.frm_prvw = tk.Frame(self, highlightthickness=0)    #preview element frame
        self.frm_cntl = tk.Frame(self, highlightthickness=0)    #control button frame
        self.frm_main.grid(row=0, column=0)
        self.frm_prvw.grid(row=0, column=1, padx=(20,10))
        self.frm_cntl.grid(row=1, column=0, columnspan=2, pady=(10,0))
        
        #--main frame elements
        lbl_alert_FG = tk.Label(self.frm_main, text="Text Color:", font=font_hdr2)
        lbl_alert_FG.grid(row=0, column=0, padx=(10,0), pady=(10,0), sticky=tk.E)
        lbl_warn = tk.Label(self.frm_main, text="Warning Color:", font=font_hdr2)
        lbl_warn.grid(row=1, column=0, padx=(10,0), pady=(10,0), sticky=tk.E)
        lbl_dngr = tk.Label(self.frm_main, text="Danger Color:", font=font_hdr2)
        lbl_dngr.grid(row=2, column=0, padx=(10,0), pady=10, sticky=tk.E)

        #--color selector/view buttons
        self.dmy_img = tk.PhotoImage(width=1, height=1)  #dummy image so the button size can be set in pixels
        self.fg_btn=tk.Button(self.frm_main, image=self.dmy_img, compound='center', width=40, height=40, command=lambda: self.pick_color('alert_FG'))
        self.fg_btn.grid(row=0, column=1, padx=(0,10), pady=(10,0))
        self.warn_btn=tk.Button(self.frm_main, image=self.dmy_img, compound='center', width=40, height=40, command=lambda: self.pick_color('alert_warn'))
        self.warn_btn.grid(row=1, column=1, padx=(0,10), pady=(10,0))
        self.dngr_btn=tk.Button(self.frm_main, image=self.dmy_img, compound='center', width=40, height=40, command=lambda: self.pick_color('alert_dngr'))
        self.dngr_btn.grid(row=2, column=1, padx=(0,10), pady=(10,0))

        #--preview frame elements
        lbl_preview = tk.Label(self.frm_prvw, text="Preview", font=font_hdr2)
        lbl_preview.grid(row=0, column=0, padx=10, pady=10, sticky=tk.EW)
        self.canv_prvw = tk.Canvas(self.frm_prvw, width=200, height=200, borderwidth=0, highlightthickness=0)  #canvas for preview text
        self.canv_prvw.grid(row=1, column=0)
        self.lbl_prvw_warn = self.canv_prvw.create_text(100,50, text="Warning", font=font_hdr1, fill=self.alert_FG.get('val'))
        self.lbl_prvw_dngr = self.canv_prvw.create_text(100,110, text="Danger", font=font_hdr1, fill=self.alert_FG.get('val'))
        self.prvw_warn_pad = elePad_create(self.canv_prvw, self.lbl_prvw_warn, self.alert_warn.get('val'))
        self.prvw_dngr_pad = elePad_create(self.canv_prvw, self.lbl_prvw_dngr, self.alert_dngr.get('val'))
        
        #--control frame elements
        btn_save=tk.Button(self.frm_cntl,text="Save", command=self.on_save)
        btn_save.grid(row=0, column=0, padx=10, pady=10)
        btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
        btn_cancel.grid(row=0, column=1, padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)    #Handle window close button
    
    def build_tmp_color_dict(self, clr_name):
        """function builds a temporary dict of the color name and its value. Effectively a 
        "color return" picker based on the passed name
        
        :param clr_name: color definition name
        :type clr_name: `string`
        :returns: dict of the color name and hex value
        :rtype: `dictionary` in format {color_def_name:#HEX_VAL} 
        """
        hex_val = self.master_ref.cfg_theme.colors.get(clr_name)
        tmp_clr_dict = {'name':clr_name,'val':hex_val}
        return tmp_clr_dict

    def pick_color(self, attrb_name):
        """function displays a top-level popup containing the currently defined theme colors to select
        from. It also updates the preview after a color is selected for the associated warning theme object."""
        new_clr = self.theme_color_picker(self)     #display a pop-up with the available theme colors
        self.grab_set()                             #force re-focus on current window
        if new_clr.result is not None:              #if a color was chosen, build the result dict
            upd_clr = self.build_tmp_color_dict(new_clr.result)
            setattr(self, attrb_name, upd_clr)
        self.upd_preview()                          #update the buttons and preview text

    def load_settings(self):
        """function loads the existing warning color config or sets them to defaults"""
        #--get values from main theme config if not defined, assign defaults
        if not self.theme_ref.colors.get(self.theme_ref.alert_FG, None):    #if the master theme value is not defined, then use a default color for display
            self.alert_FG.clear(); self.alert_FG.update({'name':'deflt_FG','val':clr_dflt_FG})
        else: self.alert_FG = self.build_tmp_color_dict(self.theme_ref.alert_FG)    #otherwise, retrieve the defined color
        if not self.theme_ref.colors.get(self.theme_ref.alert_warn):
            self.alert_warn.clear(); self.alert_warn.update({'name':'deflt_WARN','val':clr_dflt_WARN})
        else:self.alert_warn = self.build_tmp_color_dict(self.theme_ref.alert_warn)
        if not self.theme_ref.colors.get(self.theme_ref.alert_dngr):
            self.alert_dngr.clear(); self.alert_dngr.update({'name':'deflt_DNGR','val':clr_dflt_DNGR})
        else: self.alert_dngr = self.build_tmp_color_dict(self.theme_ref.alert_dngr)

    def upd_preview(self):
        """function updates the preview window with the currently set warning/danger colors"""
        #--update preview/select buttons
        self.fg_btn.configure(bg=self.alert_FG.get('val'))
        self.warn_btn.configure(bg=self.alert_warn.get('val'))
        self.dngr_btn.configure(bg=self.alert_dngr.get('val'))

        #--update preview text
        self.canv_prvw.itemconfig(self.lbl_prvw_warn, fill=self.alert_FG.get('val'))
        self.canv_prvw.itemconfig(self.lbl_prvw_dngr, fill=self.alert_FG.get('val'))
        self.canv_prvw.itemconfig(self.prvw_warn_pad, fill=self.alert_warn.get('val'))
        self.canv_prvw.itemconfig(self.prvw_dngr_pad, fill=self.alert_dngr.get('val'))

    def on_save(self):
        """function sets the alert colors in the theme definition on save."""
        #--update the theme config
        self.theme_ref.set_alert_colors({'alert_FG':self.alert_FG.get('name'),
                                         'alert_warn':self.alert_warn.get('name'),
                                         'alert_dngr':self.alert_dngr.get('name')})
        self.destroy()

    def on_close(self): #make no changes
        """function is called when the close or exit buttons are selected. No configuraiton is saved."""
        self.destroy()
    
    class theme_color_picker(tk.Toplevel):
        """top-level window class for choosing from defined colors"""
        def __init__(self, master):
            super().__init__(master)
            self.grab_set()                     #force focus
            self.title("Color Values")          #title bar
            self.resizable(False,False)         #fixed size
            self.result = None                  #var to hold updated color
            self.prnt_window = master           #ref back to the parent window
            self.colors_ref = self.prnt_window.master_ref.cfg_theme.colors #shorthand reference to theme colors

            self.init_window()                  #build window
            self.lstbx_colors_upd()             #update colors listbox
            self.wait_window()                  #wait in this window until destroyed

        def init_window(self):
            """function builds the various window elements"""
            #--main frames for elements
            self.frm_main = tk.Frame(self, highlightthickness=0)
            self.frm_alt = tk.Frame(self, highlightthickness=0)
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_main.grid(row=0, column=0)
            self.frm_alt.grid(row=0, column=1, sticky=tk.N)
            self.frm_cntl.grid(row=1, column=0, columnspan=2)

            #--color preview
            self.dmy_img = tk.PhotoImage(width=1, height=1)  #dummy image so the button size can be set in pixels
            self.obj_preview=tk.Button(self.frm_alt, image=self.dmy_img, compound='center', width=40, height=40, state=tk.DISABLED)
            self.obj_preview.grid(row=1, column=0, padx=10, pady=10)

            #--available colors
            lbl_lstbox_colors = tk.Label(self.frm_main, text="Pick a Color", font=font_hdr2)
            lbl_lstbox_colors.grid(row=0, column=0, padx=10, pady=(10,0))
            self.lstbx_colors = tk.Listbox(self.frm_main)
            self.lstbx_colors.grid(row=1, column=0, padx=10, pady=10)
            self.lstbx_colors.bind("<<ListboxSelect>>", self.upd_preview)    #bind listbox selection to update preview on selection
            
            #--control frame elements
            btn_save=tk.Button(self.frm_cntl,text="Save", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=10)
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=10)

            self.protocol("WM_DELETE_WINDOW", self.on_close)    #Handle window close button

        def upd_preview(self, event):
            """function updates the color preview box when a new color from the list is selected"""
            selected_clr = event.widget.curselection()                      #get the selected color index
            if selected_clr:
                sel_clr = list(self.colors_ref.keys())[selected_clr[0]]     #selected color key
                sel_clr_val = self.colors_ref.get(sel_clr)                  #selected color value
                self.obj_preview.configure(bg=sel_clr_val)                  #update the preview object

        def lstbx_colors_upd(self):
            """function populates the listbox of available colors based on the current theme definition"""
            self.lstbx_colors.delete(0,tk.END)                      #clear any existing entries
            for key in self.colors_ref.keys():
                self.lstbx_colors.insert(tk.END, key)               #populate with current list
        
        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the selected color in the alert definition"""
            selected_clr = self.lstbx_colors.curselection()             #get the selected color index
            self.result = list(self.colors_ref.keys())[selected_clr[0]] #selected color key
            self.destroy()

        def on_close(self): #make no changes
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

class wndw_Fonts(tk.Toplevel):
    '''Editor window for theme fonts'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Theme Fonts")       #title bar
        self.resizable(False,False)     #fixed size
        self.master_ref = master        #set reference to parent object

        #---references to main objects
        self.fonts_ref = master.cfg_theme.fonts     #reference to master theme fonts data dict

        self.config_window()
        self.lstbx_fonts_upd()          #update defined fonts
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0, sticky=tk.NS)
        self.frm_alt = tk.Frame(self, highlightthickness=0)
        self.frm_alt.grid(row=0, column=1, sticky=tk.NS)

        #---preview display
        self.frm_preview = tk.Frame(self, highlightthickness=0)
        self.frm_preview.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)
        self.frm_preview.rowconfigure(1, weight=1)
        self.frm_preview.columnconfigure(0, weight=1)
        lbl_preview_title = tk.Label(self.frm_preview, text="Font Preview", font=font_hdr2)
        lbl_preview_title.grid(row=0, column=0, padx=10, pady=(10,0))
        self.obj_preview = tk.Label(self.frm_preview, text=text_example, font=font_hdr2)
        self.obj_preview.grid(row=1, column=0, padx=(10,20), pady=10, sticky=tk.NSEW)

        #---management widgets
        lbl_lstbox_fonts = tk.Label(self.frm_main, text="Defined Fonts", font=font_hdr2)
        lbl_lstbox_fonts.grid(row=0, column=0, padx=10, pady=(10,0))
        self.lstbx_fonts = tk.Listbox(self.frm_main, width=20)
        self.lstbx_fonts.grid(row=1, column=0, padx=10, pady=10)
        self.lstbx_fonts.bind("<<ListboxSelect>>", self.upd_preview)    #bind listbox selection to update preview on selection

        btn_fontAdd=tk.Button(self.frm_alt,text="Add Font", command=self.font_add)
        btn_fontAdd.grid(row=0, column=0, padx=10, pady=(50,0))
        btn_fontEdit=tk.Button(self.frm_alt,text="Edit Font", command=self.font_edit)
        btn_fontEdit.grid(row=1, column=0, padx=10, pady=(10,0))
        btn_fontDel=tk.Button(self.frm_alt,text="Delete Font", command=self.font_del)
        btn_fontDel.grid(row=2, column=0, padx=10, pady=10)

    def upd_preview(self, event):
        """function called when a listbox item is clicked to update the preview"""
        selected_font = event.widget.curselection()                 #get the selected font
        if selected_font:
            sel_font = list(self.fonts_ref.keys())[selected_font[0]]    #and its actual key name
            preview_font = self.fonts_ref.get(sel_font)                 #to retrieve the selected font class object
            preview_font_tuple = preview_font.fnt_tup                   #and retrieve the font tuple
            self.obj_preview.configure(font=preview_font_tuple)         #update the preview object

    def lstbx_fonts_upd(self):
        """function populates the listbox of available config definitions based on the current theme values"""
        self.lstbx_fonts.delete(0,tk.END)           #clear any existing entries
        for key in self.fonts_ref.keys():
            self.lstbx_fonts.insert(tk.END, key)    #populate with current list

    def font_add(self):
        """function calls the config modification window for a new entry."""
        self.font_modify(None)

    def font_edit(self):
        """function calls the config modification window for an existing entry."""
        if(len(self.lstbx_fonts.curselection()) == 0):
            messagebox.showwarning("Warning", "No Font Selected. Please select a font to edit.")
        else:
            sel_index = self.lstbx_fonts.curselection()             #selected value, tupple
            sel_font = list(self.fonts_ref.keys())[sel_index[0]]    #selected font key
            self.font_modify(self.fonts_ref.get(sel_font))          #selected font

    def font_del(self):
        """function removes the configuration definition. Additionally, before removing, the external
        references of the configuration to be removed are checked. If an editor element references
        the configuration, a warning is displayed and it is not removed."""

        if(len(self.lstbx_fonts.curselection()) == 0):
            messagebox.showwarning("Warning", "No Font Selected. Please select a font to delete.")
        else:
            sel_index = self.lstbx_fonts.curselection()             #selected value, tupple
            sel_font = list(self.fonts_ref.keys())[sel_index[0]]    #selected font key
            fnt_ext_refs = self.master_ref.cfg_theme.chk_ref_fonts(sel_font)  #check if font is used somewhere
            if len(fnt_ext_refs) == 0:                #if no refs are returned, then not used
                self.fonts_ref.pop(sel_font)                            #remove selected font from dict       
                self.lstbx_fonts_upd()                                  #update listbox
            else:
                msg_str = "Cannot delete! Font is referenced in the following named elements:\n"
                msg_str += tup_str(fnt_ext_refs)
                messagebox.showwarning("Warning", msg_str)

    def font_modify(self, sel_font):
        """function opens the configuration editor window for editing definitions. After the config
        has been modified in another window, it also updates the core definitions and also updates 
        any instanced elements that reference the definition. For example, if an existing color is
        modified, the elements in the dash editor that reference (the modified color def) will be
        updated to display the new color.
        
        :param sel_font: a passed font definition to update
        :type sel_font: `dash_font` definition
        """
        new_font = self.font_props(self, sel_font)
        self.grab_set() #force re-focus on current window  
        if(new_font.result is not None):                        #if a record was added or modified
            self.fonts_ref.update({new_font.result.font_name : new_font.result})    #add/update font
            self.lstbx_fonts_upd()                              #update listbox
            updPages(self.master_ref)                           #update all pages with edited property

    class font_props(tk.Toplevel):
        """toplevel window for modifing font configuration definitions. When instancing, if no configuration
        information is passed, all fields are left blank. If a configuration is passed, the available entry fields
        are populated with the passed values for modification."""
        def __init__(self, master, passed_font):
            super().__init__(master)
            self.grab_set()                     #force focus
            self.title("Font Values")           #title bar
            self.resizable(False,False)         #fixed size
            self.result = None                  #var to hold updated font

            #--working vars to store properties
            self.font_name = tk.StringVar()     #stringvar for font name
            self.font_sz = tk.StringVar()       #stringvar for font size
            self.font_type = tk.StringVar()     #stringvar for font typeface
            self.bold_var = tk.BooleanVar()     #boolvar for bold
            self.ital_var = tk.BooleanVar()     #boolvar for italicized
            self.uline_var = tk.BooleanVar()    #boolvar for underline
            self.pad_var = tk.StringVar()       #stringvar for padding around font

            #---Entry labels
            lbl_font_name = tk.Label(self, text="Font Name", font=font_hdr2)
            lbl_font_name.grid(row=0, column=0, padx=10, pady=(10,0))
            lbl_font_sz = tk.Label(self, text="Size (Pt)", font=font_hdr2)
            lbl_font_sz.grid(row=1, column=0, padx=10, pady=(10,0))
            lbl_font_type = tk.Label(self, text="Typeface", font=font_hdr2)
            lbl_font_type.grid(row=2, column=0, padx=10, pady=10)
            lbl_pad = tk.Label(self, text="Padding", font=font_hdr2)
            lbl_pad.grid(row=6, column=0, padx=10, pady=10)

            #---Entry fields
            entry_font_name = tk.Entry(self, width=30, textvariable=self.font_name)
            entry_font_name.grid(row=0, column=1, padx=10, pady=(10,0))
            entry_font_sz = tk.Entry(self, width=30, textvariable=self.font_sz)
            entry_font_sz.grid(row=1, column=1, padx=10, pady=(10,0))
            cbo_sysFont = ttk.Combobox(self, textvariable=self.font_type ,values=PyDash_fonts, font=font_hdr2)
            cbo_sysFont.set("Select Font")
            cbo_sysFont.grid(row=2, column=1, padx=10, pady=10, sticky=tk.EW)
            chk_bold = tk.Checkbutton(self, text="Bolded", font=font_hdr2, variable=self.bold_var, onvalue=True, offvalue=False)
            chk_bold.grid(row=3, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
            chk_ital = tk.Checkbutton(self, text="Italicized", font=font_hdr2, variable=self.ital_var, onvalue=True, offvalue=False)
            chk_ital.grid(row=4, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
            chk_uline = tk.Checkbutton(self, text="Underlined", font=font_hdr2, variable=self.uline_var, onvalue=True, offvalue=False)
            chk_uline.grid(row=5, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
            entry_pad = tk.Entry(self, width=30, textvariable=self.pad_var)
            entry_pad.grid(row=6, column=1, padx=10, pady=10)

            #---control buttons
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_cntl.grid(row=7, column=0, columnspan=2)
            btn_save=tk.Button(self.frm_cntl,text="Save Font", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

            #---update fields if editing an existing entry
            if passed_font is not None:    #if was passed a font, then populate fields
                entry_font_name.configure(state=tk.DISABLED)           #disable the reference name input
                self.font_name.set(passed_font.font_name)
                self.font_type.set(passed_font.typeface)
                self.font_sz.set(passed_font.point)
                self.bold_var.set(passed_font.bold)
                self.ital_var.set(passed_font.italic)
                self.uline_var.set(passed_font.undrline)
                self.pad_var.set(passed_font.pad)

            self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle window close button
            self.wait_window()  #wait in this window until destroyed

        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the configuraiton definition. Additionally, when saving, required fields for the
            definition are checked to ensure they are populated/valid. If they are invalid, then a warning
            is displayed and the configuration is not allowed to be saved."""

            if self.missing_req_fields() :
                messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
            else:
                #--assembly font kwargs
                font_kwargs = {'TYPEFACE' : self.font_type.get(),
                               'POINT' : int(self.font_sz.get()),
                               'BOLD' : self.bold_var.get(),
                               'ITALIC' : self.ital_var.get(),
                               'UNDERLINE' : self.uline_var.get(), 
                               'PAD' : int(self.pad_var.get() or 0)}
                
                self.result = dash_font(self.font_name.get(), **font_kwargs) #define font from entered values

                self.destroy()

        def on_close(self):
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

        def missing_req_fields(self):
            """function checks to ensure that all required fields for the configuration defintion are populated.
            
            :returns: required fields are missing status
            :rtype: `bool` - true if required fields are missing
            """

            #--create tuple of required fields
            req_fields = (self.font_name.get() or None,)
            req_fields += (self.font_sz.get() or None,)
            req_fields += (None if self.font_type.get() == 'Select Font' else self.font_type.get(),)

            if None in req_fields: return True  #if at least one required field is missing, return true
            else: return False

class wndw_Imgs(tk.Toplevel):
    '''Editor window for theme images'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Theme Images")      #title bar
        self.resizable(False,False)     #fixed size
        self.prvw_X = 250; self.prvw_Y = int(self.prvw_X/dash_resRatio) #some local vars to set the preview size

        #---references to main objects
        self.master_ref = master                    #reference to the main window
        self.imgs_ref = master.cfg_theme.images     #reference to master theme images dict

        self.config_window()
        self.lstbx_imgs_upd()           #update defined images
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_alt = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0)
        self.frm_alt.grid(row=0, column=1, sticky=tk.N)

        #---preview display
        self.frm_preview = tk.Frame(self, highlightthickness=0)
        self.frm_preview.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)
        self.frm_preview.rowconfigure(1, weight=1)
        self.frm_preview.columnconfigure(0, weight=1)
        lbl_preview_title = tk.Label(self.frm_preview, text="Image Preview", font=font_hdr2)
        lbl_preview_title.grid(row=0, column=0, padx=10, pady=(10,0))
        self.prvw_img_blank = tk.PhotoImage(width=self.prvw_X, height=self.prvw_Y)     #blank dummy image so the button size can be set in pixels
        self.obj_preview=tk.Button(self.frm_preview, image=self.prvw_img_blank, compound='center', state=tk.DISABLED, background='#FFFFFF')
        self.obj_preview.grid(row=1, column=0, padx=10, pady=10)

        lbl_lstbox_imgs = tk.Label(self.frm_main, text="Defined Images", font=font_hdr2)
        lbl_lstbox_imgs.grid(row=0, column=0, padx=10, pady=(10,0))
        self.lstbx_imgs = tk.Listbox(self.frm_main)
        self.lstbx_imgs.grid(row=1, column=0, padx=10, pady=10)
        self.lstbx_imgs.bind("<<ListboxSelect>>", self.upd_preview)    #bind listbox selection to update preview on selection

        btn_clrAdd=tk.Button(self.frm_alt,text="Add Image", command=self.img_add)
        btn_clrAdd.grid(row=0, column=0, padx=10, pady=(50,0))
        btn_clrEdit=tk.Button(self.frm_alt,text="Edit Image", command=self.img_edit)
        btn_clrEdit.grid(row=1, column=0, padx=10, pady=(10,0))
        btn_clrDel=tk.Button(self.frm_alt,text="Delete Image", command=self.img_del)
        btn_clrDel.grid(row=2, column=0, padx=10, pady=10)

    def upd_preview(self, event):
        """function called when a listbox item is clicked to update the preview"""
        selected_image = event.widget.curselection()                #get the selected image
        if selected_image:
            sel_img = list(self.imgs_ref.keys())[selected_image[0]] #selected image key
            sel_img_path = self.imgs_ref.get(sel_img)               #selected image path
            if os.path.isfile(sel_img_path):                            #if its a valid image
                prvw_img_native = Image.open(sel_img_path)                  #get image at path
                native_x, native_y = prvw_img_native.size                   #get the native image size
                resize_ratio = native_y/self.prvw_Y                         #get the resize ratio
                resize_x = int(native_x/resize_ratio); resize_y = int(native_y/resize_ratio)        #get the reisized dims
                prvw_img = prvw_img_native.resize((resize_x, resize_y),Image.Resampling.LANCZOS)    #resize the image to preview size
                self.prvw_img_tk = ImageTk.PhotoImage(prvw_img)                  #re-format for use in button
                self.obj_preview.configure(image=self.prvw_img_tk)               #finally update preview object
            else: self.obj_preview.configure(image=self.prvw_img_blank) #else, blank the preview if not a valid image file
    
    def lstbx_imgs_upd(self):
        """function populates the listbox of available config definitions based on the current theme values"""
        self.lstbx_imgs.delete(0,tk.END)                        #clear any existing entries
        if (self.imgs_ref is None): pass                        #no values to populate
        else:
            for key in self.imgs_ref.keys():
                self.lstbx_imgs.insert(tk.END, key)  #populate with current list
    
    def img_add(self):
        """function calls the config modification window for a new entry."""
        self.img_modify(None)

    def img_edit(self):
        """function calls the config modification window for an existing entry."""
        if(len(self.lstbx_imgs.curselection()) == 0):
            messagebox.showwarning("Warning", "No Image Selected. Please select an image to edit.")
        else:
            sel_index = self.lstbx_imgs.curselection()              #selected value, tupple
            sel_img = list(self.imgs_ref.keys())[sel_index[0]]      #selected image key
            sel_img_dict = {sel_img: self.imgs_ref.get(sel_img)}    #selected image path
            self.img_modify(sel_img_dict)

    def img_modify(self, sel_img):
        """function calls the config modification toplevel window"""
        new_img = self.img_props(self, sel_img)
        self.grab_set() #force re-focus on current window
            
        if(new_img.result is not None):                 #if a record was created or modified
            self.imgs_ref.update(new_img.result)        #add/update dict
            self.lstbx_imgs_upd()                       #update listbox
            updPages(self.master_ref)                   #update all pages with edited property

    def img_del(self):
        """function removes the configuration definition. Additionally, before removing, the external
        references of the configuration to be removed are checked. If an editor element references
        the configuration, a warning is displayed and it is not removed."""

        if(len(self.lstbx_imgs.curselection()) == 0):
            messagebox.showwarning("Warning", "No Image Selected. Please select an image to delete.")
        else:
            sel_index = self.lstbx_imgs.curselection()          #selected value, tupple
            sel_img = list(self.imgs_ref.keys())[sel_index[0]]  #selected color key
            img_ext_refs = self.master_ref.cfg_theme.chk_ref_imgs(sel_img)  #check if image is used somewhere
            if len(img_ext_refs) == 0:                #if no refs are returned, then not used
                self.imgs_ref.pop(sel_img)                          #remove selected color from dict       
                self.lstbx_imgs_upd()                               #update listbox
            else:
                msg_str = "Cannot delete! Image is referenced in the following named elements:\n"
                msg_str += tup_str(img_ext_refs)
                messagebox.showwarning("Warning", msg_str)

    class img_props(tk.Toplevel):
        """toplevel window for modifing font configuration definitions. When instancing, if no configuration
        information is passed, all fields are left blank. If a configuration is passed, the available entry fields
        are populated with the passed values for modification."""
        def __init__(self, master, passed_img):
            super().__init__(master)
            self.grab_set()                     #force focus
            self.title("Image Values")          #title bar
            self.resizable(False,False)         #fixed size
            self.master_ref = master.master_ref #main window ref
            self.passed_img = passed_img        #passed image information
            self.result = {}                    #var to hold updated image
            self.img_name = tk.StringVar()      #stringvar for image name
            self.img_path = tk.StringVar()      #stringvar for image path

            #---refname
            lbl_img_name = tk.Label(self, text="Image Name", font=font_hdr2)
            lbl_img_name.grid(row=0, column=0, padx=10, pady=(10,0))
            self.entry_img_name = tk.Entry(self, width=30, textvariable=self.img_name)
            self.entry_img_name.grid(row=0, column=1, padx=10, pady=(10,0))

            #---image selector
            btn_sel_img=tk.Button(self,text="Choose Image", command=self.choose_img)
            btn_sel_img.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

            #---control buttons
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_cntl.grid(row=2, column=0, columnspan=2)
            btn_save=tk.Button(self.frm_cntl,text="Save Image", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))
            
            #--check image to edit
            if self.load_passed_info():         #image loaded or was re-selected
                self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle window close button
                self.wait_window()  #wait in this window until destroyed
            else:                               #no image loaded, so close
                self.on_close()
        
        def choose_img(self):
            """function displays the filebrowser window for users to navigate to and select a file"""
            new_imgpath = self.img_browse()                 #open filebrowser to find image
            if new_imgpath: self.img_path.set(new_imgpath)  #if new image was selected, update image path

        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the configuraiton definition. Additionally, when saving, required fields for the
            definition are checked to ensure they are populated/valid. If they are invalid, then a warning
            is displayed and the configuration is not allowed to be saved."""

            if self.missing_req_fields() :
                messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
            else:
                self.result = {self.img_name.get(): self.img_path.get()} #set new image value
                self.destroy()

        def on_close(self):
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

        def missing_req_fields(self):
            """function checks to ensure that all required fields for the configuration defintion are populated.
            
            :returns: required fields are missing status
            :rtype: `bool` - true if required fields are missing
            """

            #--create tuple of required fields
            req_fields = (self.img_name.get() or None,)
            req_fields += (self.img_path.get() or None,)

            if None in req_fields: return True  #if at least one required field is missing, return true
            else: return False

        def load_passed_info(self):
            """function is called when populating the configuration edit top window to load an image. This process has
            some additional checks, when related to external references with a filepath. If no passed information is
            available (new theme image definition) then no further action is taken. If an image path is passed, the
            validity of that path (both the path structure and if that iamge exists at the given path) is checked.
            If an image was not able to be found at the given path, then a status of FALSE is returned. Additionally,
            in the event that the image was not found (at the passed path) users are also prompted to nvaigate to where
            the image is located.
            
            :returns: status if image was loaded or file exists
            :rtype: `bool` - True if image was loaded or exists
            """
            img_loaded = False      #return var if image was loaded or exists

            if self.passed_img is not None:                 #if was passed information, then check if exists
                self.entry_img_name.configure(state=tk.DISABLED)           #disable the reference name input
                img_path = list(self.passed_img.values())[0]#get the path from the passed dict
                img_exists = self.img_chk_path(img_path)    #see if can actually find the image
                
                if not img_exists:                          #image doesn't exist, so can't edit
                    new_sel = self.img_prompt_new(img_path) #but ask if user wants to find it

                if img_exists or new_sel:                   #image exists or new one was selected, so populate editor fields
                    self.img_name.set(next(iter(self.passed_img.keys())))
                    self.img_path.set(self.passed_img[self.img_name.get()])
                    img_loaded = True
                else:
                    self.msg_invalid_img(img_path)          #no new image selected or could not find existing
            return img_loaded
        
        def img_prompt_new(self, img_path):
            """function is called when users are prompted to re-select the image filepath (likely because it was unable
            to be found at the previous path). Users are however first prompted if they would like to try and find the image.
            If they do not, the passed image path falls back to its default value of `None` and the calling function is 
            notified via the return value that no new path was chosen. If users select a new image, the passed image path
            for the configuration editor is updated and the calling function is notified that a new value was chosen.
            
            :param img_path: the filepath where an image was attempted to be found
            :type img_path: `string`
            :returns: new image selected status
            :rtype: `bool` - true if a new image filepathpath was selected
            """
            new_image = False       #return var if new image was chosen
            browse_result = messagebox.askokcancel("Warning", f"Unable to find file at {img_path}\nDo you want to browse for it?")
            if browse_result:
                img_refname = list(self.passed_img.keys())[0]       #get the path from the passed dict
                new_imgpath = self.img_browse(img_refname)          #open filebrowser to find image
                if new_imgpath:                                     #new image path was selected
                    img_name = list(self.passed_img.keys())[0]          #get the name from the passed dict
                    self.passed_img.update({img_name:new_imgpath})      #update the passed dict image path
                    new_image = True
            return new_image

        def img_browse(self, img_refname=None):
            """function displays the file browser dialog to select an image
            
            :param img_refname: (optional) the defined name of the image - used to decorate the file chooser dialoge
            :type img_refname: `string`
            :returns: image filepath
            :rtype: `string`
            """
            if img_refname is None: title_str = f'Select Image Path'
            else: title_str = f'Select Image Path for {img_refname}'

            dialogue_opts = { 'defaultextension':'.png',
                              'initialdir':self.master_ref.editr_cntl.configFile_dir,
                              'filetypes':[('PNG','*.png'), ('All Files','*.*')],
                              'title':title_str
                            }                                       #set the dialogue options
            file_dir, file_name = file_open_dialogue(dialogue_opts) #get the location and file to open
            
            return file_dir+file_name
        
        def img_chk_path(self, img_path):
            """function checks to see if the file exists at a given path
            
            :param img_path: the filepath where an image was attempted to be found
            :type img_path: `string`
            :returns: file exists at passed path
            :rtype: `bool` - true if the file was able to be found
            """
            if os.path.isfile(img_path): return True
            else: return False

        def msg_invalid_img(self, img_path):
            """function handles the cases when an image was not able to be found at the specified path. After
            notifying the user, the configuration editor window is closed. Note that this is the "last step" in
            multiple prompts for users to select a new path or update the definition and truly is the case where
            they just wish to delete the definition.
            
            :param img_path: the filepath where an image was attempted to be found
            :type img_path: `string`
            """
            messagebox.showwarning("Warning", f"Please either delete image in editor or restore image at \n{img_path}.")
            self.on_close()

class wndw_Core(tk.Toplevel):
    '''Editor window for core config options'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Core Config")       #title bar
        self.resizable(False,False)     #fixed size

        #---references to main objects
        self.core_ref = master.cfg_core #reference to core config object

        #---local vars for updating values
        self.PWM = tk.StringVar()       #stringvar for PWM value
        self.resX = tk.StringVar()      #stringvar for x-resolution value
        self.resY = tk.StringVar()      #stringvar for y-resolution value
        self.refrsh = tk.StringVar()    #stringvar for refresh rate value

        self.config_window()
        self.load_settings()            #load current config values
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0)

        #X resolution
        lbl_xres = tk.Label(self.frm_main, text="X-resolution", font=font_hdr2)
        lbl_xres.grid(row=0, column=0, padx=10, pady=10)
        entry_xres = tk.Entry(self.frm_main, width=30, textvariable=self.resX, state="disabled")
        entry_xres.grid(row=0, column=1, padx=10, pady=10)

        #Y resolution
        lbl_yres = tk.Label(self.frm_main, text="Y-resolution", font=font_hdr2)
        lbl_yres.grid(row=1, column=0, padx=10, pady=10)
        entry_yres = tk.Entry(self.frm_main, width=30, textvariable=self.resY, state="disabled")
        entry_yres.grid(row=1, column=1, padx=10, pady=10)

        #backlight PWM
        lbl_pwm = tk.Label(self.frm_main, text="Backlight PWM", font=font_hdr2)
        lbl_pwm.grid(row=2, column=0, padx=10, pady=10)
        entry_pwm = tk.Entry(self.frm_main, width=30, textvariable=self.PWM)
        entry_pwm.grid(row=2, column=1, padx=10, pady=10)

        #refresh rate
        lbl_ref = tk.Label(self.frm_main, text="Refresh in ms", font=font_hdr2)
        lbl_ref.grid(row=3, column=0, padx=10, pady=10)
        entry_ref = tk.Entry(self.frm_main, width=30, textvariable=self.refrsh, state="disabled")
        entry_ref.grid(row=3, column=1, padx=10, pady=10)

        #---control buttons
        self.frm_cntl = tk.Frame(self, highlightthickness=0)
        self.frm_cntl.grid(row=7, column=0, columnspan=2)
        btn_save=tk.Button(self.frm_cntl,text="Save Settings", command=self.on_save)
        btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
        btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
        btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

    def load_settings(self):
        """function loads the currently defined information into the editor window"""
        self.resX.set(self.core_ref.Res_x or dash_xSz)
        self.resY.set(self.core_ref.Res_y or dash_ySz)
        self.PWM.set(self.core_ref.Baklite or 100)
        self.refrsh.set(self.core_ref.Refresh or refrsh_rt)

    def on_save(self):
        """function sets the alert colors in the theme definition on save."""
        if self.missing_req_fields() :                      #missing required fields, show warning
            messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
        else:                                               #otherwise update config
            self.core_ref.Res_x = self.resX.get()
            self.core_ref.Res_y = self.resY.get()
            self.core_ref.Baklite = self.PWM.get()
            self.core_ref.Refresh = self.refrsh.get()
            self.destroy()

    def on_close(self): #make no changes
        """function is called when the close or exit buttons are selected. No configuraiton is saved."""
        self.destroy()

    def missing_req_fields(self):
        """function checks to ensure that all required fields for the configuration defintion are populated.
            
        :returns: required fields are missing status
        :rtype: `bool` - true if required fields are missing
        """
        #--create tuple of required fields
        req_fields = (self.PWM.get() or None,)

        if None in req_fields: return True  #if at least one required field is missing, return true
        else: return False

class wndw_CANcore(tk.Toplevel):
    '''Editor window for CAN core options'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("CAN Core Config")   #title bar
        self.resizable(False,False)     #fixed size

        #---references to main objects
        self.CAN_ref = master.cfg_CAN   #reference to core CAN object

        #---local vars for updating values
        self.PID_var = tk.StringVar()       #stringvar for base PID value
        self.rxFilter_var = tk.BooleanVar() #boolvar for enabling RX filter

        self.config_window()
        self.load_settings()            #load current config values
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0)

        #Base PID
        lbl_PID = tk.Label(self.frm_main, text="Base PID", font=font_hdr2)
        lbl_PID.grid(row=0, column=0, padx=10, pady=10)
        entry_PID = tk.Entry(self.frm_main, width=10, textvariable=self.PID_var)
        entry_PID.grid(row=0, column=1, padx=10, pady=10)

        #CAN RX filter enable
        chk_bold = tk.Checkbutton(self, text="Enable RX filter", font=font_hdr2, variable=self.rxFilter_var, onvalue=True, offvalue=False)
        chk_bold.grid(row=1, column=0 ,columnspan=2, padx=10, pady=(0,10), sticky=tk.W)

        #---control buttons
        self.frm_cntl = tk.Frame(self, highlightthickness=0)
        self.frm_cntl.grid(row=7, column=0, columnspan=2)
        btn_save=tk.Button(self.frm_cntl,text="Save Settings", command=self.on_save)
        btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
        btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
        btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

    def load_settings(self):
        """function loads the currently defined information into the editor window"""
        self.PID_var.set(self.CAN_ref.base_PID or sys_CAN_base_PID)
        self.rxFilter_var.set(self.CAN_ref.rx_filter or False)

    def on_save(self):
        """function sets the alert colors in the theme definition on save."""
        if self.missing_req_fields() :                      #missing required fields, show warning
            messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
        else:                                               #otherwise update config
            self.CAN_ref.base_PID = self.PID_var.get()
            self.CAN_ref.rx_filter = self.rxFilter_var.get()
            self.destroy()

    def on_close(self):
        """function is called when the close or exit buttons are selected. No configuraiton is saved."""
        self.destroy()

    def missing_req_fields(self):
        """function checks to ensure that all required fields for the configuration defintion are populated.
            
        :returns: required fields are missing status
        :rtype: `bool` - true if required fields are missing
        """
        #--create tuple of required fields
        req_fields = (self.PID_var.get() or None,)

        if None in req_fields: return True  #if at least one required field is missing, return true
        else: return False

class wndw_CANch(tk.Toplevel):
    '''Editor window for CAN channels'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("CAN data Channels") #title bar
        self.resizable(False,False)     #fixed size
        
        #---references to main objects
        self.CAN_ref = master.cfg_CAN   #reference to core CAN object

        self.config_window()
        self.lstbx_ch_upd()             #update defined CAN channels
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_alt = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0, sticky=tk.EW)
        self.frm_alt.grid(row=0, column=1, sticky=tk.N)

        lbl_lstbox_ch = tk.Label(self.frm_main, text="CAN Channels", font=font_hdr2)
        lbl_lstbox_ch.grid(row=0, column=0, padx=10, pady=(10,0))
        self.lstbx_ch = tk.Listbox(self.frm_main, width=25)
        self.lstbx_ch.grid(row=1, column=0, padx=10, pady=10)
        btn_chAdd=tk.Button(self.frm_alt,text="Add Channel", command=self.ch_add)
        btn_chAdd.grid(row=0, column=0, padx=10, pady=(50,0))
        btn_chEdit=tk.Button(self.frm_alt,text="Edit Channel", command=self.ch_edit)
        btn_chEdit.grid(row=1, column=0, padx=10, pady=(10,0))
        btn_chDel=tk.Button(self.frm_alt,text="Delete Channel", command=self.ch_del)
        btn_chDel.grid(row=2, column=0, padx=10, pady=10)

    def lstbx_ch_upd(self):
        """function populates the listbox of available config definitions based on the current theme values"""
        self.lstbx_ch.delete(0,tk.END)                          #clear any existing entries
        for key, val in self.CAN_ref.data_ch.items():
            self.lstbx_ch.insert(tk.END, f"{key}:{val.PID}")    #populate with current list

    def ch_add(self):
        """function calls the config modification window for a new entry."""
        self.ch_modify(None)

    def ch_edit(self):
        """function calls the config modification window for an existing entry."""
        if(len(self.lstbx_ch.curselection()) == 0):
            messagebox.showwarning("Warning", "No CAN channel Selected. Please select a channel to edit.")
        else:
            sel_index = self.lstbx_ch.curselection()                    #selected value
            sel_ch = list(self.CAN_ref.data_ch.keys())[sel_index[0]]    #selected key
            self.ch_modify(self.CAN_ref.data_ch.get(sel_ch))            #selected channel

    def ch_del(self):
        """function removes the configuration definition. Additionally, before removing, the external
        references of the configuration to be removed are checked. If an editor element references
        the configuration, a warning is displayed and it is not removed."""

        if(len(self.lstbx_ch.curselection()) == 0):
            messagebox.showwarning("Warning", "No channel Selected. Please select a channel to delete.")
        else:
            sel_index = self.lstbx_ch.curselection()         #selected value, tupple
            sel_ch = list(self.CAN_ref.data_ch.keys())[sel_index[0]]    #selected channel key
            ch_ext_refs = self.CAN_ref.chk_ref_CANch(sel_ch)            #check if CAN channel is used somewhere
            if len(ch_ext_refs) == 0:                           #if no refs are returned, then not used
                self.CAN_ref.data_ch.pop(sel_ch)                #remove selected channel from dict       
                self.lstbx_ch_upd()                             #update listbox
            else:
                msg_str = "Cannot delete! CAN channel is referenced in the following named elements:\n"
                msg_str += tup_str(ch_ext_refs)
                messagebox.showwarning("Warning", msg_str)

    def ch_modify(self, sel_ch):
        """function opens the configuration editor window for editing definitions. After the config
        has been modified in another window, it also updates the core definitions and also updates 
        any instanced elements that reference the definition. For example, if an existing color is
        modified, the elements in the dash editor that reference (the modified color def) will be
        updated to display the new color.
        
        :param sel_ch: a passed can channel definition to update
        :type sel_ch: `CAN_ch` definition
        """
        new_CANch = self.CANch_props(self, sel_ch)
        self.grab_set() #force re-focus on current window
            
        if(new_CANch.result is not None):                        #if a record was added or modified
            self.CAN_ref.data_ch.update(new_CANch.result)       #add/update can channel
            self.lstbx_ch_upd()                                 #update listbox

    class CANch_props(tk.Toplevel):
        """toplevel window for modifing CAN channel configuration definitions. When instancing, if no configuration
        information is passed, all fields are left blank. If a configuration is passed, the available entry fields
        are populated with the passed values for modification."""
        def __init__(self, master, passed_ch):
            super().__init__(master)
            self.grab_set()                     #force focus
            self.title("CAN channel Values")    #title bar
            self.resizable(False,False)         #fixed size
            self.result = None                  #var to hold updated font

            #--working vars to store properties
            self.name_var = tk.StringVar()
            self.PID_var = tk.StringVar()
            self.ext_var = tk.BooleanVar()
            self.dlc_var = tk.StringVar()
            self.RTR_var = tk.BooleanVar()
            self.RTRfreq_var = tk.StringVar()
            self.calc_frames_var = tk.StringVar()
            self.calc_scalar_var = tk.StringVar()
            self.calc_offset_var = tk.StringVar()

            #--field entry widgets
            self.frm_main = tk.Frame(self, highlightthickness=0)
            self.frm_main.grid(row=0, column=0)

            #-name
            lbl_name = tk.Label(self.frm_main, text="Channel Name", font=font_hdr2)
            lbl_name.grid(row=0, column=0, padx=10, pady=(10,0))
            entry_name = tk.Entry(self.frm_main, width=20, textvariable=self.name_var)
            entry_name.grid(row=0, column=1, padx=10, pady=(10,0))

            #-PID
            lbl_PID = tk.Label(self.frm_main, text="PID (in HEX)", font=font_hdr2)
            lbl_PID.grid(row=1, column=0, padx=10, pady=(10,0))
            entry_PID = tk.Entry(self.frm_main, width=20, textvariable=self.PID_var)
            entry_PID.grid(row=1, column=1, padx=10, pady=(10,0))

            #-Extended frame
            chk_bold = tk.Checkbutton(self.frm_main, text="Extended Frame", font=font_hdr2, variable=self.ext_var, onvalue=True, offvalue=False)
            chk_bold.grid(row=2, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

            #-DLC
            lbl_DLC = tk.Label(self.frm_main, text="DLC (expected frames)", font=font_hdr2)
            lbl_DLC.grid(row=3, column=0, padx=10, pady=10)
            entry_DLC = tk.Entry(self.frm_main, width=20, textvariable=self.dlc_var)
            entry_DLC.grid(row=3, column=1, padx=10, pady=10)

            #separator line
            ttk.Separator(self.frm_main, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, padx=10, sticky=tk.EW)

            #-Remote Req
            chk_RTR = tk.Checkbutton(self.frm_main, text="RTR (Remote Req)", font=font_hdr2, variable=self.RTR_var, onvalue=True, offvalue=False, command=self.RTR_en)
            chk_RTR.grid(row=5, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

            #-Remote Req Freq
            lbl_RTRfreq = tk.Label(self.frm_main, text="RTR Frequency (in ms)", font=font_hdr2)
            lbl_RTRfreq.grid(row=6, column=0, padx=10, pady=10)
            self.entry_RTRfreq = tk.Entry(self.frm_main, width=20, textvariable=self.RTRfreq_var)
            self.entry_RTRfreq.grid(row=6, column=1, padx=10, pady=10)

            #separator line
            ttk.Separator(self.frm_main, orient=tk.HORIZONTAL).grid(row=7, column=0, columnspan=2, padx=10, sticky=tk.EW)

            #-Calc Frames
            lbl_frames = tk.Label(self.frm_main, text="Target Frames", font=font_hdr2)
            lbl_frames.grid(row=8, column=0, padx=10, pady=(10,0))
            entry_frames = tk.Entry(self.frm_main, width=20, textvariable=self.calc_frames_var)
            entry_frames.grid(row=8, column=1, padx=10, pady=(10,0))

            #-Calc scalar
            lbl_scalar = tk.Label(self.frm_main, text="Calc Scalar", font=font_hdr2)
            lbl_scalar.grid(row=9, column=0, padx=10, pady=(10,0))
            entry_scalar = tk.Entry(self.frm_main, width=20, textvariable=self.calc_scalar_var)
            entry_scalar.grid(row=9, column=1, padx=10, pady=(10,0))

            #-Calc Offset
            lbl_ofst = tk.Label(self.frm_main, text="Calc Offset", font=font_hdr2)
            lbl_ofst.grid(row=10, column=0, padx=10, pady=10)
            entry_ofst = tk.Entry(self.frm_main, width=20, textvariable=self.calc_offset_var)
            entry_ofst.grid(row=10, column=1, padx=10, pady=10)

            #---control buttons
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_cntl.grid(row=1, column=0)
            btn_save=tk.Button(self.frm_cntl,text="Save Channel", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

            #---update fields if editing an existing entry
            if passed_ch is not None:    #if was passed a CAN channel, then populate fields
                entry_name.configure(state=tk.DISABLED)           #disable the reference name input
                self.name_var.set(passed_ch.name)
                self.PID_var.set(passed_ch.PID)
                self.ext_var.set(passed_ch.ext or False)
                self.dlc_var.set(passed_ch.dlc)
                self.RTR_var.set(passed_ch.rem_req or False)
                self.RTRfreq_var.set(passed_ch.req_freq or '')
                self.frm_mains_tup = ','.join(str(i) for i in passed_ch.frames)
                self.calc_frames_var.set(self.frm_mains_tup)
                self.calc_scalar_var.set(passed_ch.scalar or '')
                self.calc_offset_var.set(passed_ch.offset or '')

            self.RTR_en()   #enable or disable RTR freq field based on the check box
            self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle window close button
            self.wait_window()  #wait in this window until destroyed

        def RTR_en(self):
            """function handles auxiliary field setting when the RTR (remote request) field is enabled or disabled.
            If RTR is disabled, any related fields should be disabled and set to blank. If RTR is enabled, it should
            enable related fields."""

            if self.RTR_var.get():      #RTR is enabled: allow entry to fields
                self.entry_RTRfreq.config(state='normal')
            else:                       #RTR is disabled: don't allow field entry, clear any entries
                self.entry_RTRfreq.config(state='disabled'); self.RTRfreq_var.set('')

        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the configuraiton definition. Additionally, when saving, required fields for the
            definition are checked to ensure they are populated/valid. If they are invalid, then a warning
            is displayed and the configuration is not allowed to be saved."""

            if self.missing_req_fields() :
                messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
            else:
                #--assembly CAN channel kwargs
                ch_kwargs = {'NAME':self.name_var.get(),
                             'CAN_PID':self.PID_var.get(),
                             'EXT':self.ext_var.get(),
                             'DLC':self.dlc_var.get(),
                             'REM_REQ':self.RTR_var.get(),
                             'REQ_FREQ':self.RTRfreq_var.get(),
                             'FRAMES':self.calc_frames_var.get(),
                             'SCALAR':self.calc_scalar_var.get(),
                             'DEC_OFST':self.calc_offset_var.get()}
                
                self.result = {ch_kwargs.get('NAME'): CAN_ch(**ch_kwargs)} #define CAN channel from entered values
                self.destroy()

        def on_close(self): #make no changes
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

        def missing_req_fields(self):
            """function checks to ensure that all required fields for the configuration defintion are populated.
            
            :returns: required fields are missing status
            :rtype: `bool` - true if required fields are missing
            """
            #--create tuple of required fields
            req_fields = (self.name_var.get() or None,)
            req_fields += (self.PID_var.get() or None,)
            req_fields += (self.dlc_var.get() or None,)
            req_fields += (self.calc_frames_var.get() or None,)

            if self.RTR_var.get():  #if RTR is required, then a frequency must be set
                req_fields += (self.RTRfreq_var.get() or None,)

            if None in req_fields: return True  #if at least one required field is missing, return true
            else: return False

class wndw_Pages(tk.Toplevel):
    """editor window for dash pages"""
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Dash Pages")        #title bar
        self.resizable(False,False)     #fixed size

        ##---references to main objects
        self.master_ref = master            #reference to main window
        self.pages_ref = master.cfg_pages   #reference to core pages object

        self.config_window()
        self.lstbx_pages_upd()          #update defined pages
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_alt = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0)
        self.frm_alt.grid(row=0, column=1, sticky=tk.N)

        lbl_lstbox_pages = tk.Label(self.frm_main, text="Defined Dash Pages", font=font_hdr2)
        lbl_lstbox_pages.grid(row=0, column=0, padx=10, pady=(10,0))
        self.lstbx_pages = tk.Listbox(self.frm_main)
        self.lstbx_pages.grid(row=1, column=0, padx=10, pady=10)

        btn_pgAdd=tk.Button(self.frm_alt,text="Add Page", command=self.page_add)
        btn_pgAdd.grid(row=0, column=0, padx=10, pady=(50,0))
        btn_pgEdit=tk.Button(self.frm_alt,text="Edit Page", command=self.page_edit)
        btn_pgEdit.grid(row=1, column=0, padx=10, pady=(10,0))
        btn_pgDel=tk.Button(self.frm_alt,text="Delete Page", command=self.page_del)
        btn_pgDel.grid(row=2, column=0, padx=10, pady=10)

        btn_pgEdit=tk.Button(self.frm_alt,text="Order ↑", command=self.page_orderUp)
        btn_pgEdit.grid(row=3, column=0, padx=10, pady=(20,0))
        btn_pgDel=tk.Button(self.frm_alt,text="Order ↓", command=self.page_orderDn)
        btn_pgDel.grid(row=4, column=0, padx=10, pady=(10,20))

    def lstbx_pages_upd(self):
        """function populates the listbox of available config definitions based on the current theme values"""
        self.lstbx_pages.delete(0,tk.END)               #clear any existing entries
        for key in self.pages_ref.keys():
            self.lstbx_pages.insert(tk.END, f"{key}")   #populate with current list
    
    def page_add(self):
        """function calls the config modification window for a new entry."""
        self.page_modify(None)

    def page_edit(self):
        """function calls the config modification window for an existing entry."""
        if(len(self.lstbx_pages.curselection()) == 0):
            messagebox.showwarning("Warning", "No Page Selected. Please select a page to edit.")
        else:
            sel_index = self.lstbx_pages.curselection()         #selected value, tupple
            sel_pg = list(self.pages_ref.keys())[sel_index[0]]  #selected page key
            self.page_modify(self.pages_ref.get(sel_pg))

    def page_modify(self, sel_page):
        """function opens the configuration editor window for editing definitions. After the config
        has been modified in another window, it also updates the core definitions and also updates 
        any instanced elements that reference the definition. For example, if an existing color is
        modified, the elements in the dash editor that reference (the modified color def) will be
        updated to display the new color.
        
        :param sel_page: a passed dash page definition to update
        :type sel_page: `dash_page` definition
        """

        new_pg = self.page_props(self, sel_page)
        self.grab_set() #force re-focus on current window
            
        if(new_pg.result is not None):
            self.pages_ref.update(new_pg.result)    #if a record was added/updated, add/update dict
        self.lstbx_pages_upd()                      #update listbox (needed for all updates in case of name change)
        self.master_ref.editr_cntl.cboFrames_upd()  #refresh the main pages combo box as well

    def page_del(self):
        """function removes the configuration definition. Additionally, before removing, the external
        references of the configuration to be removed are checked. If an editor element references
        the configuration, a warning is displayed and it is not removed."""

        if(len(self.lstbx_pages.curselection()) == 0):
            messagebox.showwarning("Warning", "No Page Selected. Please select a page to delete.")
        else:
            delete_result = messagebox.askokcancel("Warning", "This will delete the page configuration and cannot be undone. Do you want to proceed?")
            if delete_result:
                sel_index = self.lstbx_pages.curselection()         #selected value, tupple
                sel_pg = list(self.pages_ref.keys())[sel_index[0]]  #selected page key
                del_page = self.pages_ref.pop(sel_pg)               #remove selected page from dict
                del_page.del_page_ext_refs()                        #cleanup any "external refs" for page elements       
                self.lstbx_pages_upd()                              #update listbox
                self.master_ref.editr_cntl.CheckReset()             #udpate the main editor frame
                self.master_ref.editr_cntl.cboFrames_upd()          #refresh the main pages combo box as well

    def page_orderUp(self):
        """function handles the re-odering of pages in the list box. The currently select page is moved up in
        the order."""
        if(len(self.lstbx_pages.curselection()) == 0):
            messagebox.showwarning("Warning", "No Page Selected. Please select a page to change order.")
        else:
            self.re_order_pages(Move_Page['UP'])

    def page_orderDn(self):
        """function handles the re-odering of pages in the list box. The currently select page is moved down in
        the order."""
        if(len(self.lstbx_pages.curselection()) == 0):
            messagebox.showwarning("Warning", "No Page Selected. Please select a page to change order.")
        else:
            self.re_order_pages(Move_Page['DN'])
    
    def re_order_pages(self, move_dir):
        """function re-orders the defined configuration pages based on the passed direction. If the direction passed
        to move the selected page is "up" and it is already first in order, no move is performed. Similarly if the 
        direction passed to move the selected page is "down" and it is already last in order, no move is performed.
        
        :param move_dir: the direction to move the currently selected page
        :type move_dir: `Move_Page` dict definition
        """

        current_pages = list(self.pages_ref.keys())         #list of the pages
        sel_page_index = self.lstbx_pages.curselection()[0] #selected value, tupple
        num_pages = len(current_pages)                      #get total number of pages
        if (move_dir == Move_Page['UP'] and sel_page_index == 0):                   #if trying to move up and is already first
            messagebox.showwarning("Warning", "Page is already first in order")         #warning, no action
        elif(move_dir == Move_Page['DN'] and sel_page_index == (num_pages-1)):      #or if trying to move down and is already last
            messagebox.showwarning("Warning", "Page is already last in order")          #warning, no action
        else:
            new_page_order = current_pages.copy()               #make new page list
            pg_move = new_page_order.pop(sel_page_index)        #remove selected page from list
            if (move_dir == Move_Page['UP']): move_indx = sel_page_index - 1    #move up by one
            elif (move_dir == Move_Page['DN']): move_indx = sel_page_index + 1  #move down by one
            new_page_order.insert(move_indx,pg_move)            #generate new list of page keys
            upd_page_dict = {}                                  #temp dict for updated pages
            for key in new_page_order:
                upd_page_dict[key] = self.pages_ref[key]        #re-order pages
            self.pages_ref.clear(); self.pages_ref.update(upd_page_dict)    #clear and copy in re-ordred dict
            self.lstbx_pages_upd()                              #refresh pages listbox to show new order
            self.master_ref.editr_cntl.cboFrames_upd()          #refresh the main pages combo box as well

    class page_props(tk.Toplevel):
        """toplevel window for modifing dash page configuration definitions. When instancing, if no configuration
        information is passed, all fields are left blank. If a configuration is passed, the available entry fields
        are populated with the passed values for modification."""
        def __init__(self, prnt, passed_page):
            super().__init__(prnt)
            self.grab_set()                     #force focus
            self.title("Page Properties")       #title bar
            self.resizable(False,False)         #fixed size
            self.master_ref = prnt.master_ref   #main window ref
            self.result = {}                    #var to hold updated page. Format is {name : Page_Class}
            self.passed_page = passed_page      #ref to passed page

            #--some additional common references to make the code shorted and more readable
            self.master_colors = self.master_ref.cfg_theme.colors
            self.master_images = self.master_ref.cfg_theme.images
            
            #--working vars to store properties
            self.pg_name = tk.StringVar()       #stringvar for reference name
            self.bgClr = tk.StringVar()         #stringvar for background color
            self.bgImg = tk.StringVar()         #stringvar for background image
            self.pg_type = tk.StringVar()       #stringvar for page type
            self.pg_width = tk.StringVar()      #stringvar for page width
            self.pg_height = tk.StringVar()     #stringvar for page height
            self.pg_width.set(dash_xSz); self.pg_height.set(dash_ySz);  #For now width/height is non-configurable
            self.pg_type.set('GAUGE')   #for now, all windows are a gauge type
            
            #---entry frame
            self.frm_entry = tk.Frame(self, highlightthickness=0)
            self.frm_entry.grid(row=0, column=0)
            #---page name
            lbl_pg_name = tk.Label(self.frm_entry, text="Page Name", font=font_hdr2)
            lbl_pg_name.grid(row=0, column=0, padx=10, pady=(10,0))
            entry_pg_name = tk.Entry(self.frm_entry, width=30, textvariable=self.pg_name)
            entry_pg_name.grid(row=0, column=1, padx=10, pady=(10,0))

            #--page type
            lbl_type = tk.Label(self.frm_entry, text="Page Type", font=font_hdr2)
            lbl_type.grid(row=1, column=0, padx=10, pady=(10,0))
            cbo_type = ttk.Combobox(self.frm_entry, textvariable=self.pg_type, state=tk.DISABLED)
            cbo_type.grid(row=1, column=1, padx=10, pady=(10,0))

            #--page BG color
            lbl_bgClr = tk.Label(self.frm_entry, text="Background Color", font=font_hdr2)
            lbl_bgClr.grid(row=2, column=0, padx=10, pady=(10,0))
            cbo_bgClr = ttk.Combobox(self.frm_entry, textvariable=self.bgClr, values=list(self.master_colors.keys()))
            cbo_bgClr.set("Select Color")
            cbo_bgClr.grid(row=2, column=1, padx=10, pady=(10,0))

            #--page BG image
            lbl_bgImg = tk.Label(self.frm_entry, text="Background Image", font=font_hdr2)
            lbl_bgImg.grid(row=3, column=0, padx=10, pady=(10,0))
            img_list = ['None'] + list(self.master_images.keys()) #Add "None" option to BG image list
            cbo_bgImg = ttk.Combobox(self.frm_entry, textvariable=self.bgImg, values=img_list)
            cbo_bgImg.set('None')
            cbo_bgImg.grid(row=3, column=1, padx=10, pady=(10,0))

            #---width
            lbl_pg_width = tk.Label(self.frm_entry, text="Page Width", font=font_hdr2)
            lbl_pg_width.grid(row=4, column=0, padx=10, pady=(10,0))
            entry_pg_width = tk.Entry(self.frm_entry, width=30, textvariable=self.pg_width, state=tk.DISABLED)
            entry_pg_width.grid(row=4, column=1, padx=10, pady=(10,0))

            #---height
            lbl_pg_height = tk.Label(self.frm_entry, text="Page Height", font=font_hdr2)
            lbl_pg_height.grid(row=5, column=0, padx=10, pady=10)
            entry_pg_height = tk.Entry(self.frm_entry, width=30, textvariable=self.pg_height, state=tk.DISABLED)
            entry_pg_height.grid(row=5, column=1, padx=10, pady=10)

            #---control buttons
            self.frm_cntl = tk.Frame(self, highlightthickness=0)
            self.frm_cntl.grid(row=1, column=0)
            btn_save=tk.Button(self.frm_cntl,text="Save Page", command=self.on_save)
            btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
            btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_close)
            btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

            #---update fields if editing an existing entry
            if self.passed_page is not None:    #if was passed a page, then populate fields
                entry_pg_name.configure(state=tk.DISABLED)           #disable the reference name input
                self.pg_name.set(self.passed_page.name)
                self.bgClr.set(self.passed_page.bg_clr)
                self.bgImg.set(self.passed_page.bg_img)
                self.pg_type.set(self.passed_page.type)
                self.pg_width.set(self.passed_page.width)
                self.pg_height.set(self.passed_page.height)

            self.protocol("WM_DELETE_WINDOW", self.on_close) # Handle window close button
            self.wait_window()  #wait in this window until destroyed
        
        def on_save(self):
            """function is called when the configuration is saved, to set the result dictionary used
            to update the configuraiton definition. Additionally, when saving, required fields for the
            definition are checked to ensure they are populated/valid. If they are invalid, then a warning
            is displayed and the configuration is not allowed to be saved."""

            if self.missing_req_fields():
                messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
            else:
                #--assembly page kwargs
                pg_kwargs = {'name':self.pg_name.get(),
                             'type':self.pg_type.get(),
                             'bg_clr':self.bgClr.get(),
                             'bg_img':self.bgImg.get(),
                             'width':self.pg_width.get(),
                             'height':self.pg_height.get()}
                
                '''Note that the below will leave self.result as (None) if updating an existing page, which
                    then also means the dict update (in the parent pages window) won't be changed, which
                    is totally fine. Since there's a built-in "update config" function for the pageConfig 
                    class, it's easier to do here. This is a bit different than the flow of the other main 
                    classes but it works better due to the multiple children elements contained in it. The 
                    only other that may benefit from this is the "chan channel" class but that doesn't have 
                    any additional reference objects so its kind of a "meh" update to do there'''
                upd_page = None                             #temp ref for page result
                if self.passed_page is None:                #if creating a new page
                    upd_page = dash_page(**pg_kwargs)                        #create new page config
                    upd_page.master_ref = self.master_ref               #set the master reference for in-class functions
                    upd_page.buildPages_canv()                          #create a new canvas obj
                    self.result = {pg_kwargs.get('name') : upd_page}    #set result
                else:                                       #if updating an existing page
                    self.passed_page.upd_config(pg_kwargs)              #then just update the page config

                self.destroy()

        def on_close(self):
            """function is called when the close or exit buttons are selected. No configuraiton is saved."""
            self.destroy()

        def missing_req_fields(self):
            """function checks to ensure that all required fields for the configuration defintion are populated.
            
            :returns: required fields are missing status
            :rtype: `bool` - true if required fields are missing
            """
            #--create tuple of required fields
            req_fields = (self.pg_name.get() or None,)
            req_fields += (self.bgClr.get() or None,)
            req_fields += (self.pg_type.get() or None,)

            if None in req_fields: return True  #if at least one required field is missing, return true
            else: return False

class wndw_newWidget(tk.Toplevel):
    '''toplevel window to add new widget. When instanced, the generated fiels are based on the passed element type
    as defined by the `DashEle_types` dict value passed.'''
    def __init__(self, master, ele_typ):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("Add Widget")        #title bar
        self.resizable(False,False)     #fixed size
        self.master_ref = master        #set reference to parent object
        self.ele_typ = ele_typ          #passed widget type
        self.ref_canv = master.editr_cntl.current_canv    #current canvas to make the widget on

        #--some additional common references to make the code shorted and more readable
        self.master_fonts = self.master_ref.cfg_theme.fonts
        self.master_colors = self.master_ref.cfg_theme.colors
        self.master_CANch = self.master_ref.cfg_CAN.data_ch

        #--output information
        self.result_ele_kwargs = {}     #reult dict of element config information

        if self.ref_canv is None:       #see if there is an active canvas
            messagebox.showwarning("Warning", "No Page Selected; cannot add elements without a selected page. Please choose a page before adding a new element.")
            self.destroy()                  #if not, then go no further
        else:                           #otherwise proceed normally
            self.config_window()            #load window elements
            self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the configuration pop-up window"""
        self.frm_main = tk.Frame(self, highlightthickness=0)
        self.frm_main.grid(row=0, column=0, sticky=tk.EW)
        
        #---Make Widget fields
        if self.ele_typ == DashEle_types['LBL_STAT']: self.config_eles_lbl_stat()
        elif self.ele_typ == DashEle_types['LBL_DAT']: self.config_eles_lbl_dat()
        elif self.ele_typ == DashEle_types['IND_BLT']: self.config_eles_ind_blt()
        elif self.ele_typ == DashEle_types['IND_BAR']: self.config_eles_ind_bar()             

        #---save/control frame
        self.frm_cntl = tk.Frame(self, highlightthickness=0)
        self.frm_cntl.grid(row=1, column=0)
        btn_save=tk.Button(self.frm_cntl,text="Create Widget", command=self.on_create)
        btn_save.grid(row=0, column=0, padx=10, pady=(0,10))
        btn_cancel=tk.Button(self.frm_cntl,text="Cancel", command=self.on_cancel)
        btn_cancel.grid(row=0, column=1, padx=10, pady=(0,10))

    def on_create(self):
        """function handles the action for creating a new element. Additionally, when creating, the
        required fields for the new element definition are checked to ensure they are populated/valid. 
        If they are invalid, then a warning is displayed and the new element is not allowed to be created.
        """

        if self.missing_req_fields():
            messagebox.showwarning("Warning", "Required fields are missing, cannot save.")
        else:
            self.create_element()               #create element widget object
            self.destroy()                      #done creating widget, cloe toplevel window

    def on_cancel(self):
        """function is called when the close or exit buttons are selected. No configuraiton is saved."""
        self.destroy()

    '''----build the input elements
        #remember to assign "names" to input fields that will be the kwarg keys
        #remember "reqd" attribute will help ID fields that are required
        #remember "widg_kwarg" attribute will ID children objects used to build kwargs
        #remember "value" should be assigned to ALL widgets used for inputs
        #remember that ALL element types need a reference name
    '''
    def config_eles_lbl_stat(self):
        """function creates the required fields for a static label. Additionally creates the required variables
        and field requirement values to support element generation."""
        #--reference name
        ref_lbl = tk.Label(self.frm_main, text="Reference Name", font=font_hdr2)
        ref_lbl.grid(row=0, column=0, padx=10, pady=10)
        ref_entry = tk.Entry(self.frm_main, width=15); ref_entry.name='name'
        ref_entry.value = tk.StringVar(); ref_entry.config(textvariable=ref_entry.value) #create value attrb var and assign
        ref_entry.grid(row=0, column=1, padx=10, pady=(10,0))
        ref_entry.reqd = True #set as a required widget field
        
        #--font
        font_lbl = tk.Label(self.frm_main, text="Font", font=font_hdr2)
        font_lbl.grid(row=1, column=0, padx=10, pady=(10,0))
        cbo_font = ttk.Combobox(self.frm_main, values=list(self.master_fonts.keys())); cbo_font.name='font'
        cbo_font.set("Select Font")
        cbo_font.value = tk.StringVar(); cbo_font.config(textvariable=cbo_font.value) #create value attrb var and assign
        cbo_font.grid(row=1, column=1, padx=10, pady=(10,0))
        cbo_font.reqd = True #set as a required widget field

        #--clr_FG
        fg_lbl = tk.Label(self.frm_main, text="Text Color", font=font_hdr2)
        fg_lbl.grid(row=2, column=0, padx=10, pady=(10,0))
        cbo_fg = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_fg.name='fill'
        cbo_fg.set("Select Color")
        cbo_fg.value = tk.StringVar(); cbo_fg.config(textvariable=cbo_fg.value) #create value attrb var and assign
        cbo_fg.grid(row=2, column=1, padx=10, pady=(10,0))
        cbo_fg.reqd = True #set as a required widget field

        #--padded
        chk_pad = self.chk_pad = tk.Checkbutton(self.frm_main, text="Padded", font=font_hdr2, onvalue=True, offvalue=False, command=self.pad_en)
        chk_pad.name='pad'
        chk_pad.value = tk.BooleanVar(); chk_pad.config(variable=chk_pad.value) #create value attrb var and assign
        chk_pad.grid(row=3, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
        chk_pad.reqd = True #set as a required widget field

        #--clr_BG
        bg_lbl = tk.Label(self.frm_main, text="Background Color", font=font_hdr2)
        bg_lbl.grid(row=4, column=0, padx=10, pady=(10,0))
        cbo_bg = self.cbo_bg = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys()), state='disabled')
        cbo_bg.name='clr_bg'; cbo_bg.set("Select Color")
        cbo_bg.value = tk.StringVar(); cbo_bg.config(textvariable=cbo_bg.value) #create value attrb var and assign
        cbo_bg.grid(row=4, column=1, padx=10, pady=(10,0))
        cbo_bg.reqd = False #set as a NR widget field

        #--text to display
        txt_lbl = tk.Label(self.frm_main, text="Label Text", font=font_hdr2)
        txt_lbl.grid(row=5, column=0, padx=10, pady=10)
        txt_entry = tk.Entry(self.frm_main, width=30); txt_entry.name='text'
        txt_entry.value = tk.StringVar(); txt_entry.config(textvariable=txt_entry.value) #create value attrb var and assign
        txt_entry.grid(row=5, column=1, padx=10, pady=10)
        txt_entry.reqd = True #set as a required widget field

    def config_eles_lbl_dat(self):
        """function creates the required fields for a data label. Additionally creates the required variables
        and field requirement values to support element generation."""
        #--reference name
        ref_lbl = tk.Label(self.frm_main, text="Reference Name", font=font_hdr2)
        ref_lbl.grid(row=0, column=0, padx=10, pady=10)
        ref_entry = tk.Entry(self.frm_main, width=15); ref_entry.name='name'
        ref_entry.value = tk.StringVar(); ref_entry.config(textvariable=ref_entry.value) #create value attrb var and assign
        ref_entry.grid(row=0, column=1, padx=10, pady=(10,0))
        ref_entry.reqd = True #set as a required widget field
        
        #--font
        font_lbl = tk.Label(self.frm_main, text="Font", font=font_hdr2)
        font_lbl.grid(row=1, column=0, padx=10, pady=(10,0))
        cbo_font = ttk.Combobox(self.frm_main, values=list(self.master_fonts.keys())); cbo_font.name='font'
        cbo_font.set("Select Font")
        cbo_font.value = tk.StringVar(); cbo_font.config(textvariable=cbo_font.value) #create value attrb var and assign
        cbo_font.grid(row=1, column=1, padx=10, pady=(10,0))
        cbo_font.reqd = True #set as a required widget field

        #--clr_FG
        fg_lbl = tk.Label(self.frm_main, text="Text Color", font=font_hdr2)
        fg_lbl.grid(row=2, column=0, padx=10, pady=(10,0))
        cbo_fg = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_fg.name='fill'
        cbo_fg.set("Select Color")
        cbo_fg.value = tk.StringVar(); cbo_fg.config(textvariable=cbo_fg.value) #create value attrb var and assign
        cbo_fg.grid(row=2, column=1, padx=10, pady=(10,0))
        cbo_fg.reqd = True #set as a required widget field

        #--padded
        chk_pad = self.chk_pad = tk.Checkbutton(self.frm_main, text="Padded", font=font_hdr2, onvalue=True, offvalue=False, command=self.pad_en)
        chk_pad.name='pad'
        chk_pad.value=tk.BooleanVar(); chk_pad.config(variable=chk_pad.value) #create value attrb var and assign
        chk_pad.grid(row=3, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
        chk_pad.reqd = True #set as a required widget field

        #--clr_BG
        bg_lbl = tk.Label(self.frm_main, text="Background Color", font=font_hdr2)
        bg_lbl.grid(row=4, column=0, padx=10, pady=(10,0))
        cbo_bg = self.cbo_bg = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys()), state='disabled')
        cbo_bg.name='clr_bg'; cbo_bg.set("Select Color")
        cbo_bg.value = tk.StringVar(); cbo_bg.config(textvariable=cbo_bg.value) #create value attrb var and assign
        cbo_bg.grid(row=4, column=1, padx=10, pady=(10,0))
        cbo_bg.reqd = False #set as a NR widget field

        #--text to display - max value
        txt_lbl = tk.Label(self.frm_main, text="Max Value", font=font_hdr2)
        txt_lbl.grid(row=5, column=0, padx=10, pady=10)
        txt_entry = tk.Entry(self.frm_main, width=15); txt_entry.name='max_val'
        txt_entry.value = tk.StringVar(); txt_entry.config(textvariable=txt_entry.value) #create value attrb var and assign
        txt_entry.grid(row=5, column=1, padx=10, pady=(10,0))
        txt_entry.reqd = True #set as a required widget field

        #--CAN channel
        canCH_lbl = tk.Label(self.frm_main, text="CAN channel", font=font_hdr2)
        canCH_lbl.grid(row=6, column=0, padx=10, pady=(10,0))
        cbo_canCH = ttk.Combobox(self.frm_main, values=list(self.master_CANch.keys())); cbo_canCH.name='data_ch'
        cbo_canCH.set("Select CAN Channel")
        cbo_canCH.value = tk.StringVar(); cbo_canCH.config(textvariable=cbo_canCH.value) #create value attrb var and assign
        cbo_canCH.grid(row=6, column=1, padx=10, pady=(10,0))
        cbo_canCH.reqd = True #set as a required widget field

        #--number of significant digits
        lbl_sigdig = tk.Label(self.frm_main, text="Significant Digits", font=font_hdr2)
        lbl_sigdig.grid(row=7, column=0, padx=10, pady=(10,0))
        entry_sigdig = tk.Entry(self.frm_main, width=15); entry_sigdig.name='sigdig'
        entry_sigdig.value = tk.IntVar(); entry_sigdig.config(textvariable=entry_sigdig.value)
        entry_sigdig.grid(row=7, column=1, padx=10, pady=(10,0))
        entry_sigdig.reqd = True #set as a required widget field

        #--Change Color
        chk_warn=self.chk_warn=tk.Checkbutton(self.frm_main, text="Change Color", font=font_hdr2, onvalue=True, offvalue=False, command=self.limits_en)
        chk_warn.name='warn_en'
        chk_warn.value = tk.BooleanVar(); chk_warn.config(variable=chk_warn.value) #create value attrb var and assign
        chk_warn.grid(row=8, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
        chk_warn.reqd = True #set as a required widget field

        #--warning/danger limits
        dngrLO_lbl = tk.Label(self.frm_main, text="Low Danger Limit", font=font_hdr2)
        dngrLO_lbl.grid(row=9, column=0, padx=10, pady=10)
        dngrLO_entry = self.dngrLO_entry = tk.Entry(self.frm_main, width=15, state='disabled'); dngrLO_entry.name='lim_dngrlo'
        dngrLO_entry.value = tk.StringVar(); dngrLO_entry.config(textvariable=dngrLO_entry.value) #create value attrb var and assign
        dngrLO_entry.grid(row=9, column=1, padx=10, pady=(10,0))
        dngrLO_entry.reqd = False #set as a NR widget field
        
        warnLO_lbl = tk.Label(self.frm_main, text="Low Warning Limit", font=font_hdr2)
        warnLO_lbl.grid(row=10, column=0, padx=10, pady=10)
        warnLO_entry = self.warnLO_entry = tk.Entry(self.frm_main, width=15, state='disabled'); warnLO_entry.name='lim_warnlo'
        warnLO_entry.value = tk.StringVar(); warnLO_entry.config(textvariable=warnLO_entry.value) #create value attrb var and assign
        warnLO_entry.grid(row=10, column=1, padx=10, pady=(10,0))
        warnLO_entry.reqd = False #set as a NR widget field

        warnHI_lbl = tk.Label(self.frm_main, text="High Warning Limit", font=font_hdr2)
        warnHI_lbl.grid(row=11, column=0, padx=10, pady=10)
        warnHI_entry = self.warnHI_entry = tk.Entry(self.frm_main, width=15, state='disabled'); warnHI_entry.name='lim_warnhi'
        warnHI_entry.value = tk.StringVar(); warnHI_entry.config(textvariable=warnHI_entry.value) #create value attrb var and assign
        warnHI_entry.grid(row=11, column=1, padx=10, pady=(10,0))
        warnHI_entry.reqd = False #set as a NR widget field

        dngrHI_lbl = tk.Label(self.frm_main, text="High Danger Limit", font=font_hdr2)
        dngrHI_lbl.grid(row=12, column=0, padx=10, pady=10)
        dngrHI_entry = self.dngrHI_entry = tk.Entry(self.frm_main, width=15, state='disabled'); dngrHI_entry.name='lim_dngrhi'
        dngrHI_entry.value = tk.StringVar(); dngrHI_entry.config(textvariable=dngrHI_entry.value) #create value attrb var and assign
        dngrHI_entry.grid(row=12, column=1, padx=10, pady=10)
        dngrHI_entry.reqd = False #set as a NR widget field

    def config_eles_ind_blt(self):
        """function creates the required fields for a bullet indicator. Additionally creates the required variables
        and field requirement values to support element generation."""
        #--reference name
        ref_lbl = tk.Label(self.frm_main, text="Reference Name", font=font_hdr2)
        ref_lbl.grid(row=0, column=0, padx=10, pady=(10,0))
        ref_entry = tk.Entry(self.frm_main, width=15); ref_entry.name='name'
        ref_entry.value = tk.StringVar(); ref_entry.config(textvariable=ref_entry.value) #create value attrb var and assign
        ref_entry.grid(row=0, column=1, padx=10, pady=(10,0))
        ref_entry.reqd = True #set as a required widget field

        #--size
        sz_lbl = tk.Label(self.frm_main, text="Indicator Size", font=font_hdr2)
        sz_lbl.grid(row=1, column=0, padx=10, pady=(10,0))
        sz_entry = tk.Entry(self.frm_main, width=15); sz_entry.name='size'
        sz_entry.value = tk.IntVar(); sz_entry.config(textvariable=sz_entry.value) #create value attrb var and assign
        sz_entry.grid(row=1, column=1, padx=10, pady=(10,0))
        sz_entry.reqd = True #set as a required widget field

        #--CAN channel
        canCH_lbl = tk.Label(self.frm_main, text="CAN channel", font=font_hdr2)
        canCH_lbl.grid(row=2, column=0, padx=10, pady=(10,0))
        cbo_canCH = ttk.Combobox(self.frm_main, values=list(self.master_CANch.keys())); cbo_canCH.name='data_ch'
        cbo_canCH.set("Select CAN Channel")
        cbo_canCH.value = tk.StringVar(); cbo_canCH.config(textvariable=cbo_canCH.value) #create value attrb var and assign
        cbo_canCH.grid(row=2, column=1, padx=10, pady=(10,0))
        CAN_ch.reqd = True #set as a required widget field

        #--low limit
        lolim_lbl = tk.Label(self.frm_main, text="LO Limit", font=font_hdr2)
        lolim_lbl.grid(row=3, column=0, padx=10, pady=(10,0))
        lolim_entry = tk.Entry(self.frm_main, width=15); lolim_entry.name='lim_lo'
        lolim_entry.value = tk.StringVar(); lolim_entry.config(textvariable=lolim_entry.value) #create value attrb var and assign
        lolim_entry.grid(row=3, column=1, padx=10, pady=(10,0))
        lolim_entry.reqd = True #set as a required widget field

        #--High limit
        hilim_lbl = tk.Label(self.frm_main, text="HI Limit", font=font_hdr2)
        hilim_lbl.grid(row=4, column=0, padx=10, pady=(10,0))
        hilim_entry = tk.Entry(self.frm_main, width=15); hilim_entry.name='lim_hi'
        hilim_entry.value = tk.StringVar(); hilim_entry.config(textvariable=hilim_entry.value) #create value attrb var and assign
        hilim_entry.grid(row=4, column=1, padx=10, pady=(10,0))
        hilim_entry.reqd = True #set as a required widget field

        #--lo limit color
        loclr_lbl = tk.Label(self.frm_main, text="LO Lim Color", font=font_hdr2)
        loclr_lbl.grid(row=5, column=0, padx=10, pady=(10,0))
        cbo_loclr = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_loclr.name='clr_lo'
        cbo_loclr.set("Select Color")
        cbo_loclr.value = tk.StringVar(); cbo_loclr.config(textvariable=cbo_loclr.value) #create value attrb var and assign
        cbo_loclr.grid(row=5, column=1, padx=10, pady=(10,0))
        cbo_loclr.reqd = True #set as a required widget field

        #--hi limit color
        hiclr_lbl = tk.Label(self.frm_main, text="HI Lim Color", font=font_hdr2)
        hiclr_lbl.grid(row=6, column=0, padx=10, pady=(10,0))
        cbo_hiclr = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_hiclr.name='clr_hi'
        cbo_hiclr.set("Select Color")
        cbo_hiclr.value = tk.StringVar(); cbo_hiclr.config(textvariable=cbo_hiclr.value) #create value attrb var and assign
        cbo_hiclr.grid(row=6, column=1, padx=10, pady=(10,0))
        cbo_hiclr.reqd = True #set as a required widget field

        #--outline color
        otln_lbl = tk.Label(self.frm_main, text="Outline Color", font=font_hdr2)
        otln_lbl.grid(row=7, column=0, padx=10, pady=(10,0))
        cbo_otln = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_otln.name='outln'
        cbo_otln.set("Select Color")
        cbo_otln.value = tk.StringVar(); cbo_otln.config(textvariable=cbo_otln.value) #create value attrb var and assign
        cbo_otln.grid(row=7, column=1, padx=10, pady=(10,0))
        cbo_otln.reqd = True #set as a required widget field

    def config_eles_ind_bar(self):
        """function creates the required fields for a bar indicator. Additionally creates the required variables
        and field requirement values to support element generation."""
        #--reference name
        ref_lbl = tk.Label(self.frm_main, text="Reference Name", font=font_hdr2)
        ref_lbl.grid(row=0, column=0, padx=10, pady=10)
        ref_entry = tk.Entry(self.frm_main, width=15); ref_entry.name='name'
        ref_entry.value = tk.StringVar(); ref_entry.config(textvariable=ref_entry.value) #create value attrb var and assign
        ref_entry.grid(row=0, column=1, padx=10, pady=(10,0))
        ref_entry.reqd = True #set as a required widget field

        #--fill color
        fill_lbl = tk.Label(self.frm_main, text="Fill Color", font=font_hdr2)
        fill_lbl.grid(row=1, column=0, padx=10, pady=(10,0))
        cbo_fill = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_fill.name='fill'
        cbo_fill.set("Select Color")
        cbo_fill.value = tk.StringVar(); cbo_fill.config(textvariable=cbo_fill.value) #create value attrb var and assign
        cbo_fill.grid(row=1, column=1, padx=10, pady=(10,0))
        cbo_fill.reqd = True #set as a required widget field

        #--outline color
        otln_lbl = tk.Label(self.frm_main, text="Outline Color", font=font_hdr2)
        otln_lbl.grid(row=2, column=0, padx=10, pady=(10,0))
        cbo_otln = ttk.Combobox(self.frm_main, values=list(self.master_colors.keys())); cbo_otln.name='outln'
        cbo_otln.set("Select Color")
        cbo_otln.value = tk.StringVar(); cbo_otln.config(textvariable=cbo_otln.value) #create value attrb var and assign
        cbo_otln.grid(row=2, column=1, padx=10, pady=(10,0))
        cbo_otln.reqd = True #set as a required widget field

        #--CAN channel
        canCH_lbl = tk.Label(self.frm_main, text="CAN channel", font=font_hdr2)
        canCH_lbl.grid(row=3, column=0, padx=10, pady=(10,0))
        cbo_canCH = ttk.Combobox(self.frm_main, values=list(self.master_CANch.keys())); cbo_canCH.name='data_ch'
        cbo_canCH.set("Select CAN Channel")
        cbo_canCH.value = tk.StringVar(); cbo_canCH.config(textvariable=cbo_canCH.value) #create value attrb var and assign
        cbo_canCH.grid(row=3, column=1, padx=10, pady=(10,0))
        cbo_canCH.reqd = True #set as a required widget field

        #--width
        width_lbl = tk.Label(self.frm_main, text="Bar Width", font=font_hdr2)
        width_lbl.grid(row=4, column=0, padx=10, pady=(10,0))
        width_entry = tk.Entry(self.frm_main, width=15); width_entry.name='width'
        width_entry.value = tk.IntVar(); width_entry.config(textvariable=width_entry.value) #create value attrb var and assign
        width_entry.grid(row=4, column=1, padx=10, pady=(10,0))
        width_entry.reqd = True #set as a required widget field

        #--height
        height_lbl = tk.Label(self.frm_main, text="Bar Height", font=font_hdr2)
        height_lbl.grid(row=5, column=0, padx=10, pady=(10,0))
        height_entry = tk.Entry(self.frm_main, width=15); height_entry.name='height'
        height_entry.value = tk.IntVar(); height_entry.config(textvariable=height_entry.value) #create value attrb var and assign
        height_entry.grid(row=5, column=1, padx=10, pady=(10,0))
        height_entry.reqd = True #set as a required widget field

        #--minimum value (0 width)
        minval_lbl = tk.Label(self.frm_main, text="Min Value", font=font_hdr2)
        minval_lbl.grid(row=6, column=0, padx=10, pady=(10,0))
        minval_entry = tk.Entry(self.frm_main, width=15); minval_entry.name='scale_lo'
        minval_entry.value = tk.StringVar(); minval_entry.config(textvariable=minval_entry.value) #create value attrb var and assign
        minval_entry.grid(row=6, column=1, padx=10, pady=(10,0))
        minval_entry.reqd = True #set as a required widget field

        #--maximum value (max width)
        maxval_lbl = tk.Label(self.frm_main, text="Max Value", font=font_hdr2)
        maxval_lbl.grid(row=7, column=0, padx=10, pady=(10,0))
        maxval_entry = tk.Entry(self.frm_main, width=15); maxval_entry.name='scale_hi'
        maxval_entry.value = tk.StringVar(); maxval_entry.config(textvariable=maxval_entry.value) #create value attrb var and assign
        maxval_entry.grid(row=7, column=1, padx=10, pady=(10,0))
        maxval_entry.reqd = True #set as a required widget field

        #--Change Color
        chk_warn=self.chk_warn=tk.Checkbutton(self.frm_main, text="Change Color", font=font_hdr2, onvalue=True, offvalue=False, command=self.limits_en)
        chk_warn.name='warn_en'
        chk_warn.value = tk.BooleanVar(); chk_warn.config(variable=chk_warn.value) #create value attrb var and assign
        chk_warn.grid(row=8, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)
        chk_warn.reqd = True #set as a required widget field

        #--warning/danger limits
        dngrLO_lbl = tk.Label(self.frm_main, text="Low Danger Limit", font=font_hdr2)
        dngrLO_lbl.grid(row=9, column=0, padx=10, pady=(10,0))
        dngrLO_entry = self.dngrLO_entry = tk.Entry(self.frm_main, width=15, state='disabled'); dngrLO_entry.name='lim_dngrlo'
        dngrLO_entry.value = tk.StringVar(); dngrLO_entry.config(textvariable=dngrLO_entry.value) #create value attrb var and assign
        dngrLO_entry.grid(row=9, column=1, padx=10, pady=(10,0))
        dngrLO_entry.reqd = False #set as a required widget field

        warnLO_lbl = tk.Label(self.frm_main, text="Low Warning Limit", font=font_hdr2)
        warnLO_lbl.grid(row=10, column=0, padx=10, pady=(10,0))
        warnLO_entry = self.warnLO_entry = tk.Entry(self.frm_main, width=15, state='disabled'); warnLO_entry.name='lim_warnlo'
        warnLO_entry.value = tk.StringVar(); warnLO_entry.config(textvariable=warnLO_entry.value) #create value attrb var and assign
        warnLO_entry.grid(row=10, column=1, padx=10, pady=(10,0))
        warnLO_entry.reqd = False #set as a required widget field

        warnHI_lbl = tk.Label(self.frm_main, text="High Warning Limit", font=font_hdr2)
        warnHI_lbl.grid(row=11, column=0, padx=10, pady=(10,0))
        warnHI_entry = self.warnHI_entry = tk.Entry(self.frm_main, width=15, state='disabled'); warnHI_entry.name='lim_warnhi'
        warnHI_entry.value = tk.StringVar(); warnHI_entry.config(textvariable=warnHI_entry.value) #create value attrb var and assign
        warnHI_entry.grid(row=11, column=1, padx=10, pady=(10,0))
        warnHI_entry.reqd = False #set as a required widget field

        dngrHI_lbl = tk.Label(self.frm_main, text="High Danger Limit", font=font_hdr2)
        dngrHI_lbl.grid(row=12, column=0, padx=10, pady=10)
        dngrHI_entry = self.dngrHI_entry = tk.Entry(self.frm_main, width=15, state='disabled'); dngrHI_entry.name='lim_dngrhi'
        dngrHI_entry.value = tk.StringVar(); dngrHI_entry.config(textvariable=dngrHI_entry.value) #create value attrb var and assign
        dngrHI_entry.grid(row=12, column=1, padx=10, pady=10)
        dngrHI_entry.reqd = False #set as a required widget field

    def limits_en(self):
        """function handles auxiliary field setting when the "warning enable" field is enabled or disabled.
        If limits are disabled, any related fields should be disabled and set to blank. If limits are enabled, it should
        enable related fields."""

        if self.chk_warn.value.get():   #warn/danger is enabled: allow entry to fields and mark as required fields
            self.dngrLO_entry.config(state='normal'); self.dngrLO_entry.reqd = True
            self.warnLO_entry.config(state='normal'); self.warnLO_entry.reqd = True
            self.warnHI_entry.config(state='normal'); self.warnHI_entry.reqd = True
            self.dngrHI_entry.config(state='normal'); self.dngrHI_entry.reqd = True
        else:                           #warn/danger is disabled: don't allow field entry, clear any entries
            self.dngrLO_entry.config(state='disabled'); self.dngrLO_entry.value.set('')
            self.warnLO_entry.config(state='disabled'); self.warnLO_entry.value.set('')
            self.warnHI_entry.config(state='disabled'); self.warnHI_entry.value.set('')
            self.dngrHI_entry.config(state='disabled'); self.dngrHI_entry.value.set('')
            #and mark as NR inputs
            self.dngrLO_entry.reqd = False; self.warnLO_entry.reqd = False
            self.warnHI_entry.reqd = False; self.dngrHI_entry.reqd = False

    def pad_en(self):
        """function handles auxiliary field setting when the "background pad" field is enabled or disabled.
        If padding is disabled, any related fields should be disabled and set to blank. If padding is enabled, it should
        enable related fields."""

        if self.chk_pad.value.get():            #background pad is enabled
            self.cbo_bg.config(state='normal')      #allow selection of a color
            self.cbo_bg.reqd = True                 #set BG color to a required field
            self.cbo_bg.value.set("Select Color")   #set a default value of the combobox
        else:                                   #background pad is disabled
            self.cbo_bg.config(state='disabled')    #disable color selection
            self.cbo_bg.reqd = False                #set BG color to a NR field
            self.cbo_bg.value.set('')               #and clear out the current value

    def missing_req_fields(self):
        """function checks to ensure that all required fields for the configuration defintion are populated.
        
        :returns: required fields are missing status
        :rtype: `bool` - true if required fields are missing
        """
        req_fields = () #temp tupple for required fields
        for widg in self.frm_main.winfo_children():         #cycle through the entry frame widgets
            if getattr(widg, 'reqd',False):                 #if frame widget has a 'requried' attached AND its TRUE, then it's a required element
                val = widg.value.get()    #temp value for the required input field
                if val is None or val=='': req_fields += (None,)    #if its an unallowed value, append None to check tuple
                else: req_fields += (val,)
        
        if None in req_fields: return True  #if at least one required field is missing, return true
        else: return False
    
    def create_element(self):
        """function cycles through all user entry widgets and builds the widget kwarg dict required
        to create a new dash element.
        """

        for widg in self.frm_main.winfo_children():     #cycle through the entry frame widgets
            if getattr(widg, 'value',False):            #if frame widget has a 'value' attached, then it's an element config input widget
                self.result_ele_kwargs.update({widg.name: widg.value.get()})    #then add to kwarg dictionary with the name as the key
        self.result_ele_kwargs.update({'type':self.ele_typ})                    #also add element type to widget kwargs

class vw_EditorWidget_props:
    """class to control/display the editor pane that displays the current widget properties"""
    def __init__(self, master):
        self.master_ref = master

    def get_master_state(self):
        """function gets the current state of the dash configuration. This is mainly to set local
        references to the primary dash builder definitions"""

        self.current_canv = self.master_ref.editr_cntl.current_canv     #current editing/working canvas
        self.prop_frame = self.master_ref.frm_properties                #editor frame to update 
        self.master_fonts = self.master_ref.cfg_theme.fonts
        self.master_colors = self.master_ref.cfg_theme.colors
        self.master_CANch = self.master_ref.cfg_CAN.data_ch

    def clicked_wgt(self, passed_cfg):
        """function updates the reference to the clicked dash element. This information is used when
        populating and updating user inputs in the properties view
        
        :param passed_cfg: a passed element configuration
        :type passed_cfg: an element class instance - like a `Label_Static` class instance
        """
        self.current_wigtCfg = passed_cfg   #update the current working cfg to the one of the newly clicked widget
        self.get_master_state()             #get the current refs
        self.vw_clearFrame()                #clear and set up new property frame
        self.vw_update()                    #update the view

    def vw_clearFrame(self):
        """function clears out the properties frame. This method of refreshing was chosen over creating the
        elements in a sub-frame and then replacing the primary view, as this method doesn't "flicker" 
        when clearing/loading new values."""

        for child in self.prop_frame.winfo_children():
            child.destroy()

    def vw_update(self):
        """function calls the correct method to update the editor view, based on the currently selected dash element.
        The various called functions modify the displayed fields, specific to the dash element type."""

        match self.current_wigtCfg:
            case Label_Static(): self.vwPop_lblStat()
            case Label_Data(): self.vwPop_lblDat()
            case Indicator_Bullet(): self.vwPop_indBlt()
            case Indicator_Bar(): self.vwPop_indBar()
        
    def newProps_updWdgt(self, var_name, indx, mode):
        """function updates a dash element's defitinion when its properties are updated via user input
        in the properties window.
        
        :param var_name: (not used) - variable trace related value
        :param indx: (not used) - variable trace related value
        :param mode: (not used) - variable trace related value
        """
        updKWARGS = {}                                      #temp kwarg dict to build values in
        for widg in self.prop_frame.winfo_children():       #cycle through the frame widgets
            if getattr(widg, 'value',False):                    #if frame widget has a 'value' attached, then it's an element config input widget
                try: updKWARGS.update({widg.name: widg.value.get()})    #then add to temp dict with the 'name' arg as the key
                except: updKWARGS.update({widg.name: None})             #assign none if entry widget is blank
        self.current_wigtCfg.editor_upd_config(updKWARGS)           #update object config and the editor object
    
    def vwPop_lblStat(self):
        """function updates the properties pane with the input fields for a static label. Additionally creates
        the required variables and sets traces for the user inputs to trigger configuration updates."""
        #cfg.name > label name
        lbl_refname = tk.Label(self.prop_frame, text="Reference Name", font=font_hdr2)                  #entry label
        lbl_refname.grid(row=0, column=0, padx=10, pady=(10,0))                                             #place
        entry_refname = tk.Entry(self.prop_frame, width=15, state=tk.DISABLED)                          #entry widget
        entry_refname.value = tk.StringVar(); entry_refname.config(textvariable=entry_refname.value)        #create value attrb var and assign to entry widget
        entry_refname.value.set(self.current_wigtCfg.name)                                                  #set the current config value
        entry_refname.name='name'                                                                           #assign name
        entry_refname.value.trace_add("write", self.newProps_updWdgt)                                       #add trace to update function to update config
        entry_refname.grid(row=0, column=1, padx=10, pady=(10,0))                                           #place

        #cfg.text #label text
        lbl_txt = tk.Label(self.prop_frame, text="Label Text", font=font_hdr2)
        lbl_txt.grid(row=1, column=0, padx=10, pady=(10,0))
        entry_text = tk.Entry(self.prop_frame, width=15)
        entry_text.value = tk.StringVar(); entry_text.config(textvariable=entry_text.value)
        entry_text.value.set(self.current_wigtCfg.text)
        entry_text.name='text'
        entry_text.value.trace_add("write", self.newProps_updWdgt)
        entry_text.grid(row=1, column=1, padx=10, pady=(10,0))

        #cfg.x0 = int_str(kwargs.get('X0', None))           #position - X0
        lbl_x0 = tk.Label(self.prop_frame, text="Pos - X", font=font_hdr2)
        lbl_x0.grid(row=2, column=0, padx=10, pady=(10,0))
        entry_x0 = tk.Entry(self.prop_frame, width=15)
        entry_x0.value = tk.IntVar(); entry_x0.config(textvariable=entry_x0.value)
        entry_x0.value.set(self.current_wigtCfg.x0)
        entry_x0.name='x0'
        entry_x0.value.trace_add("write", self.newProps_updWdgt)
        entry_x0.grid(row=2, column=1, padx=10, pady=(10,0))

        #cfg.y0 = int_str(kwargs.get('Y0', None))           #position - Y0
        lbl_y0 = tk.Label(self.prop_frame, text="Pos - Y", font=font_hdr2)
        lbl_y0.grid(row=3, column=0, padx=10, pady=(10,0))
        entry_y0 = tk.Entry(self.prop_frame, width=15)
        entry_y0.value = tk.IntVar(); entry_y0.config(textvariable=entry_y0.value)
        entry_y0.value.set(self.current_wigtCfg.y0)
        entry_y0.name='y0'
        entry_y0.value.trace_add("write", self.newProps_updWdgt)
        entry_y0.grid(row=3, column=1, padx=10, pady=(10,0))

        #cfg.font = kwargs.get('FONT', None)                #Named font for label (see themes class)
        lbl_font = tk.Label(self.prop_frame, text="Named Font", font=font_hdr2)
        lbl_font.grid(row=4, column=0, padx=10, pady=(10,0))
        cbo_font = ttk.Combobox(self.prop_frame, values=list(self.master_fonts.keys()))
        cbo_font.value = tk.StringVar(); cbo_font.config(textvariable=cbo_font.value)
        cbo_font.value.set(self.current_wigtCfg.font)
        cbo_font.name = 'font'
        cbo_font.value.trace_add("write", self.newProps_updWdgt)
        cbo_font.grid(row=4, column=1, padx=10, pady=(10,0))

        #cfg.fill = kwargs.get('CLR_FG', kwargs.get('FILL', False)) #foreground (fill) color
        lbl_fill = tk.Label(self.prop_frame, text="Text Color", font=font_hdr2)
        lbl_fill.grid(row=5, column=0, padx=10, pady=(10,0))
        cbo_fill = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_fill.value = tk.StringVar(); cbo_fill.config(textvariable=cbo_fill.value)
        cbo_fill.value.set(self.current_wigtCfg.fill)
        cbo_fill.name = 'fill'
        cbo_fill.value.trace_add("write", self.newProps_updWdgt)
        cbo_fill.grid(row=5, column=1, padx=10, pady=(10,0))

        #cfg.pad = bool_str(kwargs.get('PAD', False))       #text is padded
        self.chk_pad = tk.Checkbutton(self.prop_frame, text="Padded Bckgnd", font=font_hdr2, onvalue=True, offvalue=False, command=self.pad_tog)
        self.chk_pad.value = tk.BooleanVar(); self.chk_pad.config(variable=self.chk_pad.value)
        self.chk_pad.value.set(self.current_wigtCfg.pad)
        self.chk_pad.name='pad'
        self.chk_pad.value.trace_add("write", self.newProps_updWdgt)
        self.chk_pad.grid(row=6, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

        #cfg.clr_bg = kwargs.get('CLR_BG', False)           #foreground color
        lbl_bg = tk.Label(self.prop_frame, text="Background Color", font=font_hdr2)
        lbl_bg.grid(row=7, column=0, padx=10, pady=10)
        self.cbo_bg = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        self.cbo_bg.value = tk.StringVar(); self.cbo_bg.config(textvariable=self.cbo_bg.value)
        self.cbo_bg.value.set(self.current_wigtCfg.clr_bg)
        self.cbo_bg.name = 'clr_bg'
        self.cbo_bg.value.trace_add("write", self.newProps_updWdgt)
        self.cbo_bg.grid(row=7, column=1, padx=10, pady=10)

        self.pad_load()     #set the background pad on load

    def vwPop_lblDat(self):
        """function updates the properties pane with the input fields for a data label. Additionally creates
        the required variables and sets traces for the user inputs to trigger configuration updates."""
        #cfg.name > label name
        lbl_refname = tk.Label(self.prop_frame, text="Reference Name", font=font_hdr2)                  #entry label
        lbl_refname.grid(row=0, column=0, padx=10, pady=(10,0))                                             #place
        entry_refname = tk.Entry(self.prop_frame, width=15, state=tk.DISABLED)                          #entry widget
        entry_refname.value = tk.StringVar(); entry_refname.config(textvariable=entry_refname.value)        #create value attrb var and assign to entry widget
        entry_refname.value.set(self.current_wigtCfg.name)                                                  #set the current config value
        entry_refname.name='name'                                                                           #assign name
        entry_refname.value.trace_add("write", self.newProps_updWdgt)                                       #add trace to update function to update config
        entry_refname.grid(row=0, column=1, padx=10, pady=(10,0))                                           #place

        #self.text = kwargs.get('MAX_VAL', None)             #label text for max value - makes it easier to see/adjust in editor
        lbl_txt = tk.Label(self.prop_frame, text="Max Value", font=font_hdr2)
        lbl_txt.grid(row=1, column=0, padx=10, pady=(10,0))
        entry_text = tk.Entry(self.prop_frame, width=15)
        entry_text.value = tk.StringVar(); entry_text.config(textvariable=entry_text.value)
        entry_text.value.set(self.current_wigtCfg.max_val)
        entry_text.name='max_val'
        entry_text.value.trace_add("write", self.newProps_updWdgt)
        entry_text.grid(row=1, column=1, padx=10, pady=(10,0))

        #cfg.x0 = int_str(kwargs.get('X0', None))           #position - X0
        lbl_x0 = tk.Label(self.prop_frame, text="Pos - X", font=font_hdr2)
        lbl_x0.grid(row=2, column=0, padx=10, pady=(10,0))
        entry_x0 = tk.Entry(self.prop_frame, width=15)
        entry_x0.value = tk.IntVar(); entry_x0.config(textvariable=entry_x0.value)
        entry_x0.value.set(self.current_wigtCfg.x0)
        entry_x0.name='x0'
        entry_x0.value.trace_add("write", self.newProps_updWdgt)
        entry_x0.grid(row=2, column=1, padx=10, pady=(10,0))

        #cfg.y0 = int_str(kwargs.get('Y0', None))           #position - Y0
        lbl_y0 = tk.Label(self.prop_frame, text="Pos - Y", font=font_hdr2)
        lbl_y0.grid(row=3, column=0, padx=10, pady=(10,0))
        entry_y0 = tk.Entry(self.prop_frame, width=15)
        entry_y0.value = tk.IntVar(); entry_y0.config(textvariable=entry_y0.value)
        entry_y0.value.set(self.current_wigtCfg.y0)
        entry_y0.name='y0'
        entry_y0.value.trace_add("write", self.newProps_updWdgt)
        entry_y0.grid(row=3, column=1, padx=10, pady=(10,0))

        #cfg.font = kwargs.get('FONT', None)                #Named font for label (see themes class)
        lbl_font = tk.Label(self.prop_frame, text="Named Font", font=font_hdr2)
        lbl_font.grid(row=4, column=0, padx=10, pady=(10,0))
        cbo_font = ttk.Combobox(self.prop_frame, values=list(self.master_fonts.keys()))
        cbo_font.value = tk.StringVar(); cbo_font.config(textvariable=cbo_font.value)
        cbo_font.value.set(self.current_wigtCfg.font)
        cbo_font.name = 'font'
        cbo_font.value.trace_add("write", self.newProps_updWdgt)
        cbo_font.grid(row=4, column=1, padx=10, pady=(10,0))

        #cfg.fill = kwargs.get('CLR_FG', kwargs.get('FILL', False)) #foreground (fill) color
        lbl_fill = tk.Label(self.prop_frame, text="Text Color", font=font_hdr2)
        lbl_fill.grid(row=5, column=0, padx=10, pady=(10,0))
        cbo_fill = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_fill.value = tk.StringVar(); cbo_fill.config(textvariable=cbo_fill.value)
        cbo_fill.value.set(self.current_wigtCfg.fill)
        cbo_fill.name = 'fill'
        cbo_fill.value.trace_add("write", self.newProps_updWdgt)
        cbo_fill.grid(row=5, column=1, padx=10, pady=(10,0))

        #cfg.pad = bool_str(kwargs.get('PAD', False))       #text is padded
        self.chk_pad = tk.Checkbutton(self.prop_frame, text="Padded Bckgnd", font=font_hdr2, onvalue=True, offvalue=False, command=self.pad_tog)
        self.chk_pad.value = tk.BooleanVar(); self.chk_pad.config(variable=self.chk_pad.value)
        self.chk_pad.value.set(self.current_wigtCfg.pad)
        self.chk_pad.name='pad'
        self.chk_pad.value.trace_add("write", self.newProps_updWdgt)
        self.chk_pad.grid(row=6, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

        #cfg.clr_bg = kwargs.get('CLR_BG', False)           #foreground color
        lbl_bg = tk.Label(self.prop_frame, text="Background Color", font=font_hdr2)
        lbl_bg.grid(row=7, column=0, padx=10, pady=(10,0))
        self.cbo_bg = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        self.cbo_bg.value = tk.StringVar(); self.cbo_bg.config(textvariable=self.cbo_bg.value)
        self.cbo_bg.value.set(self.current_wigtCfg.clr_bg)
        self.cbo_bg.name = 'clr_bg'
        self.cbo_bg.value.trace_add("write", self.newProps_updWdgt)
        self.cbo_bg.grid(row=7, column=1, padx=10, pady=(10,0))

        #self.data_ch = kwargs.get('CH_SRC', None)           #Named data channel (see CAN class)
        lbl_CANch = tk.Label(self.prop_frame, text="CAN channel", font=font_hdr2)
        lbl_CANch.grid(row=8, column=0, padx=10, pady=(10,0))
        cbo_CANch = ttk.Combobox(self.prop_frame, values=list(self.master_CANch.keys()))
        cbo_CANch.value = tk.StringVar(); cbo_CANch.config(textvariable=cbo_CANch.value)
        cbo_CANch.value.set(self.current_wigtCfg.data_ch)
        cbo_CANch.name = 'data_ch'
        cbo_CANch.value.trace_add("write", self.newProps_updWdgt)
        cbo_CANch.grid(row=8, column=1, padx=10, pady=(10,0))

        #self.sigdig = kwargs.get('SIGDIG', None)            #number of significant digits
        lbl_sigdig = tk.Label(self.prop_frame, text="Significant Digits", font=font_hdr2)
        lbl_sigdig.grid(row=9, column=0, padx=10, pady=(10,0))
        entry_sigdig = tk.Entry(self.prop_frame, width=15)
        entry_sigdig.value = tk.IntVar(); entry_sigdig.config(textvariable=entry_sigdig.value)
        entry_sigdig.value.set(self.current_wigtCfg.sigdig)
        entry_sigdig.name='sigdig'
        entry_sigdig.value.trace_add("write", self.newProps_updWdgt)
        entry_sigdig.grid(row=9, column=1, padx=10, pady=(10,0))

        #self.warn_en = bool_str(kwargs.get('WARN_EN', None))#warning is enabled
        self.chk_warn = tk.Checkbutton(self.prop_frame, text="Warn/Danger En", font=font_hdr2, onvalue=True, offvalue=False, command=self.limits_tog)
        self.chk_warn.value = tk.BooleanVar(); self.chk_warn.config(variable=self.chk_warn.value)
        self.chk_warn.value.set(self.current_wigtCfg.warn_en)
        self.chk_warn.name='warn_en'
        #self.chk_warn.value.trace_add("write", self.newProps_updWdgt)
        self.chk_warn.grid(row=10, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

        #self.lim_DngrLo = int_str(kwargs.get('DNGR_LO', None))  #danger low limit
        lbl_DngrLo = tk.Label(self.prop_frame, text="Danger Lo Lim", font=font_hdr2)
        lbl_DngrLo.grid(row=11, column=0, padx=10, pady=(10,0))
        self.entry_DngrLo = tk.Entry(self.prop_frame, width=15)
        self.entry_DngrLo.value = tk.StringVar(); self.entry_DngrLo.config(textvariable=self.entry_DngrLo.value)
        self.entry_DngrLo.value.set(strvar_str(self.current_wigtCfg.lim_DngrLo))
        self.entry_DngrLo.name='lim_DngrLo'
        self.entry_DngrLo.value.trace_add("write", self.newProps_updWdgt)
        self.entry_DngrLo.grid(row=11, column=1, padx=10, pady=(10,0))

        #self.lim_WarnLo = int_str(kwargs.get('WARN_LO', None))  #warning low limit
        lbl_WarnLo = tk.Label(self.prop_frame, text="Warning Lo Lim", font=font_hdr2)
        lbl_WarnLo.grid(row=12, column=0, padx=10, pady=(10,0))
        self.entry_WarnLo = tk.Entry(self.prop_frame, width=15)
        self.entry_WarnLo.value = tk.StringVar(); self.entry_WarnLo.config(textvariable=self.entry_WarnLo.value)
        self.entry_WarnLo.value.set(strvar_str(self.current_wigtCfg.lim_WarnLo))
        self.entry_WarnLo.name='lim_WarnLo'
        self.entry_WarnLo.value.trace_add("write", self.newProps_updWdgt)
        self.entry_WarnLo.grid(row=12, column=1, padx=10, pady=(10,0))

        #self.lim_WarnHi = int_str(kwargs.get('WARN_HI', None))  #warning high limit
        lbl_WarnHi = tk.Label(self.prop_frame, text="Warning Hi Lim", font=font_hdr2)
        lbl_WarnHi.grid(row=13, column=0, padx=10, pady=(10,0))
        self.entry_WarnHi = tk.Entry(self.prop_frame, width=15)
        self.entry_WarnHi.value = tk.StringVar(); self.entry_WarnHi.config(textvariable=self.entry_WarnHi.value)
        self.entry_WarnHi.value.set(strvar_str(self.current_wigtCfg.lim_WarnHi))
        self.entry_WarnHi.name='lim_WarnHi'
        self.entry_WarnHi.value.trace_add("write", self.newProps_updWdgt)
        self.entry_WarnHi.grid(row=13, column=1, padx=10, pady=(10,0))
        
        #self.lim_DngrHi = int_str(kwargs.get('DNGR_HI', None))  #danger high limit
        lbl_DngrHi = tk.Label(self.prop_frame, text="Danger Lo Lim", font=font_hdr2)
        lbl_DngrHi.grid(row=14, column=0, padx=10, pady=10)
        self.entry_DngrHi = tk.Entry(self.prop_frame, width=15)
        self.entry_DngrHi.value = tk.StringVar(); self.entry_DngrHi.config(textvariable=self.entry_DngrHi.value)
        self.entry_DngrHi.value.set(strvar_str(self.current_wigtCfg.lim_DngrHi))
        self.entry_DngrHi.name='lim_DngrHi'
        self.entry_DngrHi.value.trace_add("write", self.newProps_updWdgt)
        self.entry_DngrHi.grid(row=14, column=1, padx=10, pady=10)

        self.pad_load()     #set the background pad on load
        self.limits_load()  #set the limits fields on load

    def vwPop_indBlt(self):
        """function updates the properties pane with the input fields for a bullet indicator. Additionally creates
        the required variables and sets traces for the user inputs to trigger configuration updates."""
        #cfg.name > label name
        lbl_refname = tk.Label(self.prop_frame, text="Reference Name", font=font_hdr2)                  #entry label
        lbl_refname.grid(row=0, column=0, padx=10, pady=(10,0))                                             #place
        entry_refname = tk.Entry(self.prop_frame, width=15, state=tk.DISABLED)                          #entry widget
        entry_refname.value = tk.StringVar(); entry_refname.config(textvariable=entry_refname.value)        #create value attrb var and assign to entry widget
        entry_refname.value.set(self.current_wigtCfg.name)                                                  #set the current config value
        entry_refname.name='name'                                                                           #assign name
        entry_refname.value.trace_add("write", self.newProps_updWdgt)                                       #add trace to update function to update config
        entry_refname.grid(row=0, column=1, padx=10, pady=(10,0))                                           #place

        #cfg.x0 = int_str(kwargs.get('X0', None))           #position - X0
        lbl_x0 = tk.Label(self.prop_frame, text="Pos - X", font=font_hdr2)
        lbl_x0.grid(row=1, column=0, padx=10, pady=(10,0))
        entry_x0 = tk.Entry(self.prop_frame, width=15)
        entry_x0.value = tk.IntVar(); entry_x0.config(textvariable=entry_x0.value)
        entry_x0.value.set(self.current_wigtCfg.x0)
        entry_x0.name='x0'
        entry_x0.value.trace_add("write", self.newProps_updWdgt)
        entry_x0.grid(row=1, column=1, padx=10, pady=(10,0))

        #cfg.y0 = int_str(kwargs.get('Y0', None))           #position - Y0
        lbl_y0 = tk.Label(self.prop_frame, text="Pos - Y", font=font_hdr2)
        lbl_y0.grid(row=2, column=0, padx=10, pady=(10,0))
        entry_y0 = tk.Entry(self.prop_frame, width=15)
        entry_y0.value = tk.IntVar(); entry_y0.config(textvariable=entry_y0.value)
        entry_y0.value.set(self.current_wigtCfg.y0)
        entry_y0.name='y0'
        entry_y0.value.trace_add("write", self.newProps_updWdgt)
        entry_y0.grid(row=2, column=1, padx=10, pady=(10,0))

        #self.size = int_str(kwargs.get('SIZE', None))           #bullet indicator size
        lbl_sz = tk.Label(self.prop_frame, text="Size", font=font_hdr2)
        lbl_sz.grid(row=3, column=0, padx=10, pady=(10,0))
        entry_sz = tk.Entry(self.prop_frame, width=15)
        entry_sz.value = tk.IntVar(); entry_sz.config(textvariable=entry_sz.value)
        entry_sz.value.set(self.current_wigtCfg.size)
        entry_sz.name='size'
        entry_sz.value.trace_add("write", self.newProps_updWdgt)
        entry_sz.grid(row=3, column=1, padx=10, pady=(10,0))

        #self.data_ch = kwargs.get('CH_SRC', None)           #Named data channel (see CAN class)
        lbl_CANch = tk.Label(self.prop_frame, text="CAN channel", font=font_hdr2)
        lbl_CANch.grid(row=4, column=0, padx=10, pady=(10,0))
        cbo_CANch = ttk.Combobox(self.prop_frame, values=list(self.master_CANch.keys()))
        cbo_CANch.value = tk.StringVar(); cbo_CANch.config(textvariable=cbo_CANch.value)
        cbo_CANch.value.set(self.current_wigtCfg.data_ch)
        cbo_CANch.name = 'data_ch'
        cbo_CANch.value.trace_add("write", self.newProps_updWdgt)
        cbo_CANch.grid(row=4, column=1, padx=10, pady=(10,0))

        #self.lim_lo = int_str(kwargs.get('LIM_LO', None))       #lo limit
        lbl_indlo = tk.Label(self.prop_frame, text="Ind LO Limit", font=font_hdr2)
        lbl_indlo.grid(row=5, column=0, padx=10, pady=(10,0))
        entry_indlo = tk.Entry(self.prop_frame, width=15)
        entry_indlo.value = tk.StringVar(); entry_indlo.config(textvariable=entry_indlo.value)
        entry_indlo.value.set(strvar_str(self.current_wigtCfg.lim_lo))
        entry_indlo.name='lim_lo'
        entry_indlo.value.trace_add("write", self.newProps_updWdgt)
        entry_indlo.grid(row=5, column=1, padx=10, pady=(10,0))

        #self.lim_hi = int_str(kwargs.get('LIM_HI', None))       #hi limit
        lbl_indhi = tk.Label(self.prop_frame, text="Ind HI Limit", font=font_hdr2)
        lbl_indhi.grid(row=6, column=0, padx=10, pady=(10,0))
        entry_indhi = tk.Entry(self.prop_frame, width=15)
        entry_indhi.value = tk.StringVar(); entry_indhi.config(textvariable=entry_indhi.value)
        entry_indhi.value.set(strvar_str(self.current_wigtCfg.lim_hi))
        entry_indhi.name='lim_hi'
        entry_indhi.value.trace_add("write", self.newProps_updWdgt)
        entry_indhi.grid(row=6, column=1, padx=10, pady=(10,0))

        #self.clr_lo = kwargs.get('CLR_LO', None)                #foreground (fill) color - lo limit
        lbl_loclr = tk.Label(self.prop_frame, text="LO Lim Color", font=font_hdr2)
        lbl_loclr.grid(row=7, column=0, padx=10, pady=(10,0))
        cbo_loclr = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_loclr.value = tk.StringVar(); cbo_loclr.config(textvariable=cbo_loclr.value)
        cbo_loclr.value.set(self.current_wigtCfg.clr_lo)
        cbo_loclr.name = 'clr_lo'
        cbo_loclr.value.trace_add("write", self.newProps_updWdgt)
        cbo_loclr.grid(row=7, column=1, padx=10, pady=(10,0))

        #self.clr_hi = kwargs.get('CLR_HI', None)                #foreground (fill) color - hi limit
        lbl_hiclr = tk.Label(self.prop_frame, text="HI Lim Color", font=font_hdr2)
        lbl_hiclr.grid(row=8, column=0, padx=10, pady=(10,0))
        cbo_hiclr = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_hiclr.value = tk.StringVar(); cbo_hiclr.config(textvariable=cbo_hiclr.value)
        cbo_hiclr.value.set(self.current_wigtCfg.clr_hi)
        cbo_hiclr.name = 'clr_hi'
        cbo_hiclr.value.trace_add("write", self.newProps_updWdgt)
        cbo_hiclr.grid(row=8, column=1, padx=10, pady=(10,0))

        #self.outln = kwargs.get('COLOR', None)            #named outline color (see theme class)
        lbl_otln = tk.Label(self.prop_frame, text="Outline Color", font=font_hdr2)
        lbl_otln.grid(row=9, column=0, padx=10, pady=(10,0))
        cbo_otln = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_otln.value = tk.StringVar(); cbo_otln.config(textvariable=cbo_otln.value)
        cbo_otln.value.set(self.current_wigtCfg.outln)
        cbo_otln.name = 'outln'
        cbo_otln.value.trace_add("write", self.newProps_updWdgt)
        cbo_otln.grid(row=9, column=1, padx=10, pady=(10,0))
        
    def vwPop_indBar(self):
        """function updates the properties pane with the input fields for a bar indicator. Additionally creates
        the required variables and sets traces for the user inputs to trigger configuration updates."""
        #cfg.name > label name
        lbl_refname = tk.Label(self.prop_frame, text="Reference Name", font=font_hdr2)                  #entry label
        lbl_refname.grid(row=0, column=0, padx=10, pady=(10,0))                                             #place
        entry_refname = tk.Entry(self.prop_frame, width=15, state=tk.DISABLED)                          #entry widget
        entry_refname.value = tk.StringVar(); entry_refname.config(textvariable=entry_refname.value)        #create value attrb var and assign to entry widget
        entry_refname.value.set(self.current_wigtCfg.name)                                                  #set the current config value
        entry_refname.name='name'                                                                           #assign name
        entry_refname.value.trace_add("write", self.newProps_updWdgt)                                       #add trace to update function to update config
        entry_refname.grid(row=0, column=1, padx=10, pady=(10,0))                                           #place

        #cfg.x0 = int_str(kwargs.get('X0', None))           #position - X0
        lbl_x0 = tk.Label(self.prop_frame, text="Pos - X0", font=font_hdr2)
        lbl_x0.grid(row=1, column=0, padx=10, pady=(10,0))
        entry_x0 = tk.Entry(self.prop_frame, width=15)
        entry_x0.value = tk.IntVar(); entry_x0.config(textvariable=entry_x0.value)
        entry_x0.value.set(self.current_wigtCfg.x0)
        entry_x0.name='x0'
        entry_x0.value.trace_add("write", self.newProps_updWdgt)
        entry_x0.grid(row=1, column=1, padx=10, pady=(10,0))

        #cfg.y0 = int_str(kwargs.get('Y0', None))           #position - Y0
        lbl_y0 = tk.Label(self.prop_frame, text="Pos - Y0", font=font_hdr2)
        lbl_y0.grid(row=2, column=0, padx=10, pady=(10,0))
        entry_y0 = tk.Entry(self.prop_frame, width=15)
        entry_y0.value = tk.IntVar(); entry_y0.config(textvariable=entry_y0.value)
        entry_y0.value.set(self.current_wigtCfg.y0)
        entry_y0.name='y0'
        entry_y0.value.trace_add("write", self.newProps_updWdgt)
        entry_y0.grid(row=2, column=1, padx=10, pady=(10,0))

        #self.width = int_str(kwargs.get('WIDTH', None))           #bar width
        lbl_w = tk.Label(self.prop_frame, text="Bar Width", font=font_hdr2)
        lbl_w.grid(row=3, column=0, padx=10, pady=(10,0))
        entry_w = tk.Entry(self.prop_frame, width=15)
        entry_w.value = tk.IntVar(); entry_w.config(textvariable=entry_w.value)
        entry_w.value.set(self.current_wigtCfg.width)
        entry_w.name='width'
        entry_w.value.trace_add("write", self.newProps_updWdgt)
        entry_w.grid(row=3, column=1, padx=10, pady=(10,0))

        #self.height = int_str(kwargs.get('HEIGHT', None))           #bar height
        lbl_h = tk.Label(self.prop_frame, text="Bar Height", font=font_hdr2)
        lbl_h.grid(row=4, column=0, padx=10, pady=(10,0))
        entry_h = tk.Entry(self.prop_frame, width=15)
        entry_h.value = tk.IntVar(); entry_h.config(textvariable=entry_h.value)
        entry_h.value.set(self.current_wigtCfg.height)
        entry_h.name='height'
        entry_h.value.trace_add("write", self.newProps_updWdgt)
        entry_h.grid(row=4, column=1, padx=10, pady=(10,0))
        
        #cfg.fill = kwargs.get('CLR_FG', kwargs.get('FILL', False)) #foreground (fill) color
        lbl_fill = tk.Label(self.prop_frame, text="Fill Color", font=font_hdr2)
        lbl_fill.grid(row=5, column=0, padx=10, pady=(10,0))
        cbo_fill = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_fill.value = tk.StringVar(); cbo_fill.config(textvariable=cbo_fill.value)
        cbo_fill.value.set(self.current_wigtCfg.fill)
        cbo_fill.name = 'fill'
        cbo_fill.value.trace_add("write", self.newProps_updWdgt)
        cbo_fill.grid(row=5, column=1, padx=10, pady=(10,0))

        #self.outln = kwargs.get('COLOR', None)            #named outline color (see theme class)
        lbl_otln = tk.Label(self.prop_frame, text="Outline Color", font=font_hdr2)
        lbl_otln.grid(row=6, column=0, padx=10, pady=(10,0))
        cbo_otln = ttk.Combobox(self.prop_frame, values=list(self.master_colors.keys()))
        cbo_otln.value = tk.StringVar(); cbo_otln.config(textvariable=cbo_otln.value)
        cbo_otln.value.set(self.current_wigtCfg.outln)
        cbo_otln.name = 'outln'
        cbo_otln.value.trace_add("write", self.newProps_updWdgt)
        cbo_otln.grid(row=6, column=1, padx=10, pady=(10,0))

        #self.Ordr = kwargs.get('ORDR', 'FG')                    #layer order (FG or BG)
        lbl_order = tk.Label(self.prop_frame, text="Element Order", font=font_hdr2)
        lbl_order.grid(row=7, column=0, padx=10, pady=(10,0))
        cbo_order = ttk.Combobox(self.prop_frame, values=list(Ele_Order.keys()))
        cbo_order.value = tk.StringVar(); cbo_order.config(textvariable=cbo_order.value)
        cbo_order.value.set(self.current_wigtCfg.ordr)
        cbo_order.name = 'ordr'
        cbo_order.value.trace_add("write", self.newProps_updWdgt)
        cbo_order.grid(row=7, column=1, padx=10, pady=(10,0))

        #self.data_ch = kwargs.get('CH_SRC', None)           #Named data channel (see CAN class)
        lbl_CANch = tk.Label(self.prop_frame, text="CAN channel", font=font_hdr2)
        lbl_CANch.grid(row=8, column=0, padx=10, pady=(10,0))
        cbo_CANch = ttk.Combobox(self.prop_frame, values=list(self.master_CANch.keys()))
        cbo_CANch.value = tk.StringVar(); cbo_CANch.config(textvariable=cbo_CANch.value)
        cbo_CANch.value.set(self.current_wigtCfg.data_ch)
        cbo_CANch.name = 'data_ch'
        cbo_CANch.value.trace_add("write", self.newProps_updWdgt)
        cbo_CANch.grid(row=8, column=1, padx=10, pady=(10,0))

        #self.scale_lo = int_str(kwargs.get('SCALE_LO', None))   #lower bound of scale
        lbl_scaleMin = tk.Label(self.prop_frame, text="Minimum Value", font=font_hdr2)
        lbl_scaleMin.grid(row=9, column=0, padx=10, pady=(10,0))
        entry_scaleMin = tk.Entry(self.prop_frame, width=15)
        entry_scaleMin.value = tk.StringVar(); entry_scaleMin.config(textvariable=entry_scaleMin.value)
        entry_scaleMin.value.set(strvar_str(self.current_wigtCfg.scale_lo))
        entry_scaleMin.name='scale_lo'
        entry_scaleMin.value.trace_add("write", self.newProps_updWdgt)
        entry_scaleMin.grid(row=9, column=1, padx=10, pady=(10,0))

        #self.scale_hi = int_str(kwargs.get('SCALE_HI', None))   #upper bound of scale
        lbl_scaleMax = tk.Label(self.prop_frame, text="Maximum Value", font=font_hdr2)
        lbl_scaleMax.grid(row=10, column=0, padx=10, pady=(10,0))
        entry_scaleMax = tk.Entry(self.prop_frame, width=15)
        entry_scaleMax.value = tk.StringVar(); entry_scaleMax.config(textvariable=entry_scaleMax.value)
        entry_scaleMax.value.set(strvar_str(self.current_wigtCfg.scale_hi))
        entry_scaleMax.name='scale_hi'
        entry_scaleMax.value.trace_add("write", self.newProps_updWdgt)
        entry_scaleMax.grid(row=10, column=1, padx=10, pady=(10,0))
        
        #self.warn_en = bool_str(kwargs.get('WARN_EN', None))#warning is enabled
        self.chk_warn = tk.Checkbutton(self.prop_frame, text="Warn/Danger En", font=font_hdr2, onvalue=True, offvalue=False, command=self.limits_tog)
        self.chk_warn.value = tk.BooleanVar(); self.chk_warn.config(variable=self.chk_warn.value)
        self.chk_warn.value.set(self.current_wigtCfg.warn_en)
        self.chk_warn.name='warn_en'
        self.chk_warn.value.trace_add("write", self.newProps_updWdgt)
        self.chk_warn.grid(row=11, column=0 ,columnspan=2, padx=10, pady=(10,0), sticky=tk.W)

        #self.lim_DngrLo = int_str(kwargs.get('DNGR_LO', None))  #danger low limit
        lbl_DngrLo = tk.Label(self.prop_frame, text="Danger Lo Lim", font=font_hdr2)
        lbl_DngrLo.grid(row=12, column=0, padx=10, pady=(10,0))
        self.entry_DngrLo = tk.Entry(self.prop_frame, width=15)
        self.entry_DngrLo.value = tk.StringVar(); self.entry_DngrLo.config(textvariable=self.entry_DngrLo.value)
        self.entry_DngrLo.value.set(strvar_str(self.current_wigtCfg.lim_DngrLo))
        self.entry_DngrLo.name='lim_DngrLo'
        self.entry_DngrLo.value.trace_add("write", self.newProps_updWdgt)
        self.entry_DngrLo.grid(row=12, column=1, padx=10, pady=(10,0))

        #self.lim_WarnLo = int_str(kwargs.get('WARN_LO', None))  #warning low limit
        lbl_WarnLo = tk.Label(self.prop_frame, text="Warning Lo Lim", font=font_hdr2)
        lbl_WarnLo.grid(row=13, column=0, padx=10, pady=(10,0))
        self.entry_WarnLo = tk.Entry(self.prop_frame, width=15)
        self.entry_WarnLo.value = tk.StringVar(); self.entry_WarnLo.config(textvariable=self.entry_WarnLo.value)
        self.entry_WarnLo.value.set(strvar_str(self.current_wigtCfg.lim_WarnLo))
        self.entry_WarnLo.name='lim_WarnLo'
        self.entry_WarnLo.value.trace_add("write", self.newProps_updWdgt)
        self.entry_WarnLo.grid(row=13, column=1, padx=10, pady=(10,0))

        #self.lim_WarnHi = int_str(kwargs.get('WARN_HI', None))  #warning high limit
        lbl_WarnHi = tk.Label(self.prop_frame, text="Warning Hi Lim", font=font_hdr2)
        lbl_WarnHi.grid(row=14, column=0, padx=10, pady=(10,0))
        self.entry_WarnHi = tk.Entry(self.prop_frame, width=15)
        self.entry_WarnHi.value = tk.StringVar(); self.entry_WarnHi.config(textvariable=self.entry_WarnHi.value)
        self.entry_WarnHi.value.set(strvar_str(self.current_wigtCfg.lim_WarnHi))
        self.entry_WarnHi.name='lim_WarnHi'
        self.entry_WarnHi.value.trace_add("write", self.newProps_updWdgt)
        self.entry_WarnHi.grid(row=14, column=1, padx=10, pady=(10,0))
        
        #self.lim_DngrHi = int_str(kwargs.get('DNGR_HI', None))  #danger high limit
        lbl_DngrHi = tk.Label(self.prop_frame, text="Danger Lo Lim", font=font_hdr2)
        lbl_DngrHi.grid(row=15, column=0, padx=10, pady=10)
        self.entry_DngrHi = tk.Entry(self.prop_frame, width=15)
        self.entry_DngrHi.value = tk.StringVar(); self.entry_DngrHi.config(textvariable=self.entry_DngrHi.value)
        self.entry_DngrHi.value.set(strvar_str(self.current_wigtCfg.lim_DngrHi))
        self.entry_DngrHi.name='lim_DngrHi'
        self.entry_DngrHi.value.trace_add("write", self.newProps_updWdgt)
        self.entry_DngrHi.grid(row=15, column=1, padx=10, pady=10)

        self.limits_load()  #set the limits fields on load

    def pad_tog(self):
        """function handles auxiliary field setting when the "background pad" field is enabled or disabled.
        If padding is disabled, any related fields should be disabled and set to blank. If padding is enabled, it should
        enable related fields."""
        self.pad_load()                         #load function handles widget state
        if self.chk_pad.value.get():            #background pad is enabled
            self.cbo_bg.value.set("Select Color")   #set a default value of the combobox
        else:                                   #background pad is disabled
            self.cbo_bg.value.set('')               #and clear out the current value
    
    def pad_load(self):
        """function handles auxiliary field setting when the "background pad" field is enabled or disabled.
        specifically called on first populating the configuration view, this function only enables or disables
        associated fields."""
        if self.chk_pad.value.get():            #background pad is enabled
            self.cbo_bg.config(state='normal')      #allow selection of a color
            self.cbo_bg.reqd = True                 #set BG color to a required field
        else:                                   #background pad is disabled
            self.cbo_bg.config(state='disabled')    #disable color selection
            self.cbo_bg.reqd = False                #set BG color to a NR field

    def limits_tog(self):
        """function handles auxiliary field setting when the "warning enable" field is enabled or disabled.
        If limits are disabled, any related fields should be disabled and set to blank. If limits are enabled, it should
        enable related fields."""
        self.limits_load()              #load function handles widget state
        if self.chk_warn.value.get():   #warn/danger is enabled: allow entry to fields and mark as required fields
            pass
        else:                           #warn/danger is disabled: don't allow field entry, clear any entries
            self.entry_DngrLo.value.set('')
            self.entry_WarnLo.value.set('')
            self.entry_WarnHi.value.set('')
            self.entry_DngrHi.value.set('')

    def limits_load(self):
        """function handles auxiliary field setting when the "warning enable" field is enabled or disabled.
        specifically called on first populating the configuration view, this function only enables or disables
        associated fields."""
        if self.chk_warn.value.get():   #warn/danger is enabled: allow entry to fields and mark as required fields
            self.entry_DngrLo.config(state='normal'); self.entry_DngrLo.reqd = True
            self.entry_WarnLo.config(state='normal'); self.entry_WarnLo.reqd = True
            self.entry_WarnHi.config(state='normal'); self.entry_WarnHi.reqd = True
            self.entry_DngrHi.config(state='normal'); self.entry_DngrHi.reqd = True
        else:                           #warn/danger is disabled: don't allow field entry and mark as NR fields
            self.entry_DngrLo.config(state='disabled'); self.entry_DngrLo.reqd = False
            self.entry_WarnLo.config(state='disabled'); self.entry_WarnLo.reqd = False
            self.entry_WarnHi.config(state='disabled'); self.entry_WarnHi.reqd = False
            self.entry_DngrHi.config(state='disabled'); self.entry_DngrHi.reqd = False

#---------------------Help Based Windows---------------------
class wndw_About(tk.Toplevel):
    '''Editor window for About information'''
    def __init__(self, master):
        super().__init__(master)
        self.grab_set()                 #force focus
        self.title("About")             #title bar
        self.resizable(False,False)     #fixed size
        self.master_ref = master        #set reference to parent object

        self.config_window()            #add window elements
        self.wait_window()              #stay in this window until updated/closed

    def config_window(self):
        """function loads the various elements of the help pop-up window"""
        tk.Label(self, text="PyDash Desktop Configurator", font=font_hdr1).grid(row=0, column=0, padx=20, pady=(10,0))
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=0, padx=10, sticky=tk.EW)
        tk.Label(self, text=help_versionText, font=font_norm2).grid(row=2, column=0, padx=10, sticky=tk.W)
        tk.Label(self, text=help_buildDateText, font=font_norm2).grid(row=2, column=0, padx=10, sticky=tk.E)
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, column=0, padx=10, sticky=tk.EW)
        tk.Label(self, text=help_companyName, font=font_hdr2).grid(row=4, column=0, padx=10, pady=(10,0), sticky=tk.W)
        tk.Label(self, text=help_email, font=font_norm1).grid(row=5, column=0, padx=10, sticky=tk.W)
        
        #--external github links
        gitlink_main = tk.Label(self, text='GITHub Page - Main', font=font_norm1_hyper, fg='blue', cursor="hand2")
        gitlink_main.grid(row=6, column=0, padx=10, sticky=tk.W)
        gitlink_main.bind('<Button-1>', lambda event: self.open_Weblink(help_html_gitMain, event))

        gitlink_manual = tk.Label(self, text='GITHub Page - User Guide', font=font_norm1_hyper, fg='blue', cursor="hand2")
        gitlink_manual.grid(row=7, column=0, padx=10, sticky=tk.W)
        gitlink_manual.bind('<Button-1>', lambda event: self.open_Weblink(help_html_gitUserGuide, event))

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=8, column=0, padx=10, pady=10, sticky=tk.EW)
        tk.Button(self,text="  OK  ", command=self.on_close).grid(row=9, column=0, padx=10, pady=(0,10))

    def open_Weblink(self, link, event):
        """function handles opening a URL at the passed path
        
        :param link: the web URL to navigate to
        :type link: `string`
        :param evnt: (not used) the event information about the triggering event.
        :type evnt: `Event` tkinter object
        """
        wb.open_new_tab(link)

    def on_close(self):
        """function is called when the close or exit buttons are selected. No action is taken."""
        self.destroy()
