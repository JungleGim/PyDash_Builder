from lib import *

class wndw_Main(tk.Tk):
    """Primary tkinter window class"""
    def __init__(self):
        tk.Tk.__init__(self)
        
        #----high-level variables that store the loaded configuration
        self.cfg_pages = {}                 #dict of dash pages defined for the display. Format is {name: FrameClass}
        self.cfg_CAN = CAN_core()           #reference for the CAN information. Format is class:CAN_core
        self.cfg_core = config()            #dict of the primary dash config values. format is {property_name: value}
        self.cfg_theme = theme()            #reference for dash theme information. Format is class:theme

        self.editr_cntl = editrCntl(self)                   #instance editor control class
        self.init_window()                                  #intialize editor window
        self.editr_wgtProps = vw_EditorWidget_props(self)   #instance widget property control

    def init_window(self):
        """function initializes the basics of the editor window and calls other init functions"""
        self.title("PyDash Builder")        #title bar
        self.resizable(False,False)         #fixed size

        self.init_menubar()                 #intialize menubar
        self.init_eles()                    #intialize editor elements
        self.init_shortcuts()               #initalize keyboard shortcuts

    def init_menubar(self):
        """function defines the menubar options"""
        #----define menu bar
        self.menubar = tk.Menu(self)                #create menu object
        
        #--file menu
        menu_file = tk.Menu(self.menubar, tearoff=0)
        menu_file.add_command(label="New", command=self.config_new)                     #create new config
        menu_file.add_command(label="Open", command=self.config_load)                   #open existing config XML
        menu_file.add_command(label="Save", command=lambda: self.config_save(False))    #save current config XML
        menu_file.add_command(label="Save As", command=lambda: self.config_save(True))  #save current config XML as another name
        menu_file.add_separator()
        menu_file.add_command(label="Check Config", command=self.gen_dashCFG_check)         #check config for errors before generating dash XML
        menu_file.add_command(label="Generate Dash Config", command=self.gen_dashCFG)       #generate dash XML file (and also export images)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self.destroy)
        self.menubar.add_cascade(label="File", menu=menu_file)

        #--Theme menu
        menu_theme = tk.Menu(self.menubar, tearoff=0)
        menu_theme.add_command(label="Colors", command= lambda: self.new_toplvl(wndw_Colors))   #edit theme colors
        menu_theme.add_command(label="Fonts", command= lambda: self.new_toplvl(wndw_Fonts))     #edit theme fonts
        menu_theme.add_command(label="Images", command= lambda: self.new_toplvl(wndw_Imgs))     #edit theme images
        menu_theme.add_separator()
        menu_theme.add_command(label="Warning Colors", command= lambda: self.new_toplvl(wndw_AlertColors))   #window to edit/update/dispaly warning text
        self.menubar.add_cascade(label="Theme", menu=menu_theme)

        #--Core menu
        menu_core = tk.Menu(self.menubar, tearoff=0)
        menu_core.add_command(label="Config", command=lambda: self.new_toplvl(wndw_Core))       #edit the core dash config options
        self.menubar.add_cascade(label="Core", menu=menu_core)

        #--CAN menu
        menu_CAN = tk.Menu(self.menubar, tearoff=0)
        menu_CAN.add_command(label="Base Config", command=lambda: self.new_toplvl(wndw_CANcore))#edit core CAN configuration
        menu_CAN.add_command(label="CAN channels", command=lambda: self.new_toplvl(wndw_CANch)) #edit mapped CAN channels
        self.menubar.add_cascade(label="CAN", menu=menu_CAN)

        #--windows menu
        menu_pages = tk.Menu(self.menubar, tearoff=0)
        menu_pages.add_command(label="Manage Pages", command=lambda: self.new_toplvl(wndw_Pages))   #edit defined pages
        self.menubar.add_cascade(label="Dash Pages", menu=menu_pages)

        #--help menu
        menu_help = tk.Menu(self.menubar, tearoff=0)
        menu_help.add_command(label="About", command=lambda: self.new_toplvl(wndw_About))        #about software version information
        self.menubar.add_cascade(label="Help", menu=menu_help)

        #--set menubar
        self.config(menu=self.menubar)              #assign menubar

    def init_eles(self):
        """Function initializes the main control elements in the dash editor"""
        #--header frame for controls
        self.frm_hdr = tk.Frame(self, height=50)
        self.frm_hdr.grid(row=0, column=0, columnspan=2 ,sticky=tk.N)        #stick to the top
        self.frm_hdr.grid_rowconfigure(0,weight=1)                           #give any extra height to row 0 (the header row)

        #--primary window where the actual dash view is displayed
        self.frm_main = tk.Frame(self)                          #primary frame for editor view
        self.frm_main.grid(row=1, column=0, sticky=tk.NSEW)
        
        #--secondary frame for dash element editing and viewing properties
        self.frm_alt = tk.Frame(self, width=350)    #fixed size to prevent window from resizing when clicking different widgets
        self.frm_alt.grid_propagate(False)                      #prevent from resizing based on children
        self.frm_alt.grid(row=1, column=1, sticky=tk.NSEW)
        
        #--dash display working area
        self.frm_DashDisplay = tk.Frame(self.frm_main, height=dash_ySz+brdr_accent_offset, width=dash_xSz+brdr_accent_offset,
                                        highlightthickness=brdr_accent, highlightbackground='black')
        self.frm_DashDisplay.grid_propagate(False)  #prevent from resizing based on children
        self.frm_DashDisplay.grid(row=1, columnspan=2, padx=10, pady=10, sticky=tk.S)

        #--editor header and controls
        #-page selector
        lbl_frm_DashDisplay = tk.Label(self.frm_hdr, text="Dash Page:", font=font_hdr1)
        lbl_frm_DashDisplay.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        cbo_font = font_hdr2                                    #set a temp combobox font reference, so just need to maintain one setting for the cbo + listbox
        self.cbo_frame = ttk.Combobox(self.frm_hdr, values=list(self.cfg_pages.keys()), font=cbo_font)
        popdown_window_name = self.cbo_frame.tk.eval(f'ttk::combobox::PopdownWindow {str(self.cbo_frame)}')     #get the CBO listbox (pop-down) ref
        self.cbo_frame.tk.call(f'{popdown_window_name}.f.l', 'configure', '-font', cbo_font)                    #change the listbox font
        self.cbo_frame.bind('<<ComboboxSelected>>', self.editr_cntl.ChangeEditorCanv)                           #bind combo box selection to frame change
        self.cbo_frame.set('Select Page')                                                                       #set default values before selection
        self.cbo_frame.grid(row=0, column=1, padx=(0,10), sticky=tk.W)

        #-add elements buttons
        sep1 = ttk.Separator(self.frm_hdr, orient=tk.VERTICAL)
        sep1.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NS)
        btn_sLabel=tk.Button(self.frm_hdr,text="Add Static Label", font=font_hdr2, command= lambda: self.new_element(DashEle_types['LBL_STAT']))
        btn_sLabel.grid(row=0, column=3, padx=10, pady=10)
        btn_dLabel=tk.Button(self.frm_hdr,text="Add Data Label", font=font_hdr2, command= lambda: self.new_element(DashEle_types['LBL_DAT']))
        btn_dLabel.grid(row=0, column=4, padx=10, pady=10)
        btn_bltInd=tk.Button(self.frm_hdr,text="Add Bullet Ind", font=font_hdr2, command= lambda: self.new_element(DashEle_types['IND_BLT']))
        btn_bltInd.grid(row=0, column=5, padx=10, pady=10)
        btn_barInd=tk.Button(self.frm_hdr,text="Add Bar Ind", font=font_hdr2, command= lambda: self.new_element(DashEle_types['IND_BAR']))
        btn_barInd.grid(row=0, column=6, padx=10, pady=10)

        #-delete element
        sep2 = ttk.Separator(self.frm_hdr, orient=tk.VERTICAL)
        sep2.grid(row=0, column=7, padx=10, pady=10, sticky=tk.NS)
        self.btn_delEle=tk.Button(self.frm_hdr,text="Delete Element", font=font_hdr2, command= self.delete_crnt_element)
        self.btn_delEle.grid(row=0, column=8, padx=10, pady=10)

        #--element properties frame
        self.frm_alt.grid_columnconfigure(0,weight=1)   #let the whole column expand to the given width
        lbl_frm_properties = tk.Label(self.frm_alt, text="Element Properties", font=font_hdr2)
        lbl_frm_properties.grid(row=0, column=0, padx=10, pady=(10,5))
        self.frm_alt.grid_rowconfigure(1,weight=1)      #let the properties row soak up any extra height
        self.frm_properties = tk.Frame(self.frm_alt, highlightthickness=dbg_brdr,highlightbackground='black')
        self.frm_properties.grid_propagate(False)  #prevent from resizing based on children
        self.frm_properties.grid(row=1, column=0, padx=10, pady=(0,10), sticky=tk.NSEW)

    def init_shortcuts(self):
        """function binds common keyboard shortcuts to various menu functions"""
        self.bind("<Control-s>", lambda e: self.config_save(False))
        self.bind("<Control-Shift-S>", lambda e: self.config_save(True))

    def new_element(self, type):
        """function creates a new element, binds required editor controls, and also places it on the current dash page being viewed
        
        :param type: type of dash element to create
        :type type: `DashEle_types`
        """
        new_ele_info = wndw_newWidget(self, type)                                   #1) get input information from wndw_newWidget
        if bool(new_ele_info.result_ele_kwargs):                                    #1.a) check if a new element was actually created
            ele_cfg = self.editr_cntl.updCFG_addEle(new_ele_info.result_ele_kwargs) #2) add new element to cfg_pages for the page being edited
            ele_cfg.master_ref = self                                               #2.a) set master ref for editor element processing
            wgt_kwargs = ele_cfg.get_edtr_wgt_kwargs()                              #2.b) get widget kwargs from new config
            wigt_add = FrmEdit_widget_place(self, type, wgt_kwargs)                 #3) run "place" interaction to get placement coords
            self.wait_variable(wigt_add.placed)                                     #3.a) wait until widget has been placed before doing anything further 
            ele_cfg.upd_config(wigt_add.placed_coords)                              #3.b) update the config information with the placed coords
            ele_refID, ele_padID = instance_widget(type,
                                                    self.editr_cntl.current_canv, 
                                                    ele_cfg.get_edtr_wgt_kwargs())  #4) instance widget on editor canvas at clicked location
            ele_cfg.upd_config({'objID':ele_refID, 'padID':ele_padID})              #4.a) set editor canvas refID and background pad ID
            ele_cfg.editor_canvObj = self.editr_cntl.current_canv                   #4.b) set editor canvas reference for later update/use
            ele_cfg.wgtCtl=FrmEdit_bind_widget_control(self, self.editr_cntl.current_canv, ele_cfg)#5) bind widget control triggers to canvas item
            ele_cfg.upd_ele_def_refs()                                              #6) update external references for new element

        self.grab_set()                         #re-focus to parent window once popup is closed
    
    def delete_crnt_element(self):
        """function deletes the currently selected dash element"""
        self.editr_cntl.delWidget()             #delete the currently selected widget

    def new_toplvl(self, wndw_class):
        """Function calls a new toplevel window. Used consistently through the various menu option views. Additionally 
        re-grabs focus when the toplevel window is closed
        
        :param wndw_class: new toplevel window class to instance
        :type wndw_class: `tk.Toplevel` window class
        """
        wndw_class(self)        #call new toplevel
        self.grab_set()         #re-focus to parent window once popup is closed
    
    def cfg_check_exist(self):
        """function to check if there are any config values currently populated."""
        config_items = (len(self.cfg_pages) + self.cfg_core.len() + 
                        self.cfg_CAN.len() + self.cfg_theme.len())   #if any of the config option dicts has a length, something was added
        
        if config_items > 0: return True
        else: return False
    
    def cfg_clear(self):
        """function to reset/clear the current dash config"""
        self.cfg_pages.clear(); self.cfg_core.clear()   #clear out config information
        self.cfg_CAN.clear(); self.cfg_theme.clear()    #clear out config information
        self.editr_cntl.ResetEditor()                   #and reset the editor window
    
    def config_load(self):
        """function loads a saved dash config XML file. If a current config is loaded, users are wanred before being
        prompted to browse to the saved dash config file"""
        cfg_exists = self.cfg_check_exist()
        if cfg_exists:          #check for existing CFG
            delete_result = messagebox.askokcancel("Warning", "Loading a new config will delete all items in the current configuration (Colors, themes, pages, etc) and cannot be undone. Do you want to proceed?")
        else: delete_result = False

        if delete_result or not cfg_exists:         #if no cfg exists or user said it was OK
            self.cfg_clear()                        #then clear
            filedict = xmlfile_openDialogue(self)   #and load a config file
        else: messagebox.showinfo("FYI", "Dash config was not loaded")  #otherwise do nothing, but give them a reminder

        if filedict is not None:
            self.editr_cntl.configFile_dir = filedict['dir']
            self.editr_cntl.configFile_name = filedict['name']                                  #update the latest config file name and path
            xmlFile = XML_open(self.editr_cntl.configFile_dir, self.editr_cntl.configFile_name) #open a file at the saved path, return XML element tree obj
            parseXML(self, xmlFile)                                                             #parse the XML file and load data structs
            messagebox.showinfo("Success", "Loaded dash config successfully!")                  #let the user know it was loaded
            self.editr_cntl.buildAllPages()                                                     #build all the pages in the loaded config
            self.editr_cntl.cboFrames_upd()                                                     #update frame select combo box    
            self.editr_cntl.gotoEditorCanv(next(iter(self.cfg_pages)))                          #load first page in config into the editor

    def config_save(self, saveas=False):
        """function saves the current dash parameters to a config file for later use.
        
        :param saveas: If set to TRUE, prompt users with a file save dialoge. If FALSE then save to previously opened file.
        :type saveas: `bool`: default FALSE
        """
        ok_to_save = False  #local var to test/check if its okay to save
        if saveas or self.editr_cntl.configFile_name is None or self.editr_cntl.configFile_dir is None:   #if a path is missing or user clicked saveas
            filedict = xmlfile_saveDialogue(self)
            if filedict is not None:
                self.editr_cntl.configFile_dir = filedict['dir']; self.editr_cntl.configFile_name = filedict['name']  #update the latest config file name and pat
                ok_to_save = True   #and it's ok to save the file
            else:
                messagebox.showinfo("FYI", "Dash config was not saved")
                skip_message = True #skip unable to save message
        else:                   #otherwise, user clicked "Save" and file name/path had been set                    
            ok_to_save = True   #so it's ok to save the file

        if ok_to_save:          #if file save conditions have been met/set 
            xmlGen = editorXML_gen(self)                                                        #generate editor XML config file
            XML_save(self.editr_cntl.configFile_dir, self.editr_cntl.configFile_name, xmlGen)   #save editor XML config file
        elif skip_message: pass #if user was previosuly warned, then skip second message
        else: messagebox.showinfo("FYI", "Unable to save dash config.")
        
    def config_new(self):
        """function clears the current dash config"""
        cfg_exists = self.cfg_check_exist()
        if cfg_exists:          #check for existing CFG
            delete_result = messagebox.askokcancel("Warning", "This will delete all items in the current configuration (Colors, themes, pages, etc) and cannot be undone. Do you want to proceed?")
        else: delete_result = False

        if delete_result or not cfg_exists: self.cfg_clear()            #if no cfg exists or user said it was OK, then clear
        else: messagebox.showinfo("FYI", "Dash config was not cleared") #otherwise do nothing, but give them a reminder

    def gen_dashCFG(self):
        """function generates the output files to save a dash configuration"""
        if self.gen_dashCFG_check():    #if no errors were found
            #TODO: generate XML for the dash configuration
            #TODO: generate total package for dash config (including images)
            pass

    def gen_dashCFG_check(self):
        """function checks the current dash configuration for potential errors. Any identified errors may cause an issue when
        saving the dash editor file for later use, but is primarily intended for identifying errors that would not create a valid
        dash config file to save to the PyDash.
        
        If any errors are detected, they are displayed for the user to resolve"""
        errors_list = self.gen_dashCFG_VV()     #check for potential errors
        if len(errors_list) != 0:               #error result is not blank, so there are errors
            err_msg = "Error detected in configuration. Please fix the following issues before a dash config can be saved:\n\n"
            for k,v in errors_list.items(): err_msg += k + ': ' + v +'\n'   #build error message string
            err_notif_wndw = wndw_notify(self, {'type':Popup_types['ERROR'],
                                                'title':'CONFIG ERROR',
                                                'message':err_msg})         #display error message
            return False    #if errors are found, return false
        else: return True   #otherwise return true
    
    def gen_dashCFG_VV(self):
        """function checks current config for any errors that would result in an invalid configuration.
        
        :return error_dict: errors in the format of {'issue_location':'issue description'}"""
        return XML_dashCFG_checkErrs(self)  # check for errors and return list of issues
#-----------------------------main loop
if __name__ == "__main__":
    app = wndw_Main()
    app.mainloop()