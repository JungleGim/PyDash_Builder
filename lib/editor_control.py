from .sys import *

from datetime import datetime, timedelta
import math
from .com_defs import instance_widget           #needed for adding widgets to canvas after importing
from .com_defs import addImg                    #needed for placing images on a page/frame
from .com_defs import DashEle_types, Ele_Order  #needed for element processing
from .com_defs import Label_Static, Label_Data, Indicator_Bullet, Indicator_Bar     #needed for making new widgets

#------------editor control class
class editrCntl:
    def __init__(self, master):
        self.master_ref = master            #master window ref
        self.current_canv_name = None       #name of the current canvas
        self.current_canv = None            #current editing/working canvas
        self.current_page = None            #current editing/working page
        self.configFile_dir = None          #XML configuration file directory
        self.configFile_name = None         #XML configuration file name
        self.current_wigtCfg = None         #config of the currently clicked widget

    def ChangeEditorCanv(self, event):
        sel_frame = self.master_ref.cbo_frame.get() #get name of the selected frame
        self.gotoEditorCanv(sel_frame)    #goto selected frame

    def gotoEditorCanv(self, canvName):
        self.current_canv_name = canvName                                   #set current canvas name
        self.master_ref.cbo_frame.set(self.current_canv_name)               #set combo box selection (only needed if loading)
        try: self.current_canv.pack_forget()                                #remove the current canvas (if its been set)
        except: pass                                                        #if its not set then not needed
        
        self.current_canv = self.master_ref.cfg_pages[canvName].canvObj     #set the "current canvas" based on the passed canvas name
        self.current_page = self.master_ref.cfg_pages[canvName]             #set the current page
        self.current_canv.pack(fill= tk.BOTH, expand=True)                  #place the new canvas in frame

    def cboFrames_upd(self):
        self.master_ref.cbo_frame.config(values=list(self.master_ref.cfg_pages.keys()))      #update values in the frames combo box
        if self.current_canv is None:
            self.master_ref.cbo_frame.set('Select Page')                           #if the current frame is none, then change to 'select'
        else:
            self.master_ref.cbo_frame.set(self.current_canv_name)                  #otherwise make sure its set to the current canvas name
    
    def CheckReset(self):
        if self.current_canv_name in self.master_ref.cfg_pages: pass  #if the current canvas is still in the pages dict, then everything's OK
        else: self.ResetEditor()                  #otherwise the editor needs to be reset (likely has been deleted)

    def ResetEditor(self):
        #the goal here is to clear out the active frame and clear the current window so everything goes back to an "unselected" state
        try: self.current_canv.pack_forget()    #remove the current canvas (if its been set)
        except: pass                            #if its not set then not needed
        self.current_canv = None                #set current canvas to None
        self.cboFrames_upd()          #reset combo selection box for frames
    
    def buildAllPages(self):
        '''cycle through all pages in main dict and build the elements in their config'''
        for page in self.master_ref.cfg_pages.values():         #loop through all pages in config
            self.buildPage(page)

    def buildPage(self, psd_page):
        pg_canv = psd_page.canvObj  #canvas object for the editor

        #--add page background image
        frm_bg_img = self.master_ref.cfg_theme.images.get(psd_page.bg_img)  #frame background image path
        if frm_bg_img is not None:
            img = addImg(pg_canv, frm_bg_img)   #add background image
            pg_canv.bg_img = img                #add/update image to canvas element dict to prevent trash collection

        #--add page elements
        for ele_cfg in psd_page.Lbl_stc.values():  #loop through all static label configs
            self.addWidget(DashEle_types['LBL_STAT'], pg_canv, ele_cfg)
        for ele_cfg in psd_page.Lbl_dat.values():  #loop through all data label configs
            self.addWidget(DashEle_types['LBL_DAT'], pg_canv, ele_cfg)
        for ele_cfg in psd_page.Ind_blt.values():  #loop through all bullet indicator configs
            self.addWidget(DashEle_types['IND_BLT'], pg_canv, ele_cfg)
        for ele_cfg in psd_page.Ind_bar.values():  #loop through all bar indicator configs
            self.addWidget(DashEle_types['IND_BAR'], pg_canv, ele_cfg)

    def addWidget(self, ele_type, ref_canv, ele_cfg):
        ele_cfg.master_ref = self.master_ref                                    #set the master ref (for theme processing)
        ele_refID, ele_padID = instance_widget(ele_type,
                                               ref_canv,
                                               ele_cfg.get_edtr_wgt_kwargs())   #create new widget and assign to object ref in class
        ele_cfg.upd_config({'objID':ele_refID, 'padID':ele_padID})              #set editor canvas refID and background pad ID
        
        try:    #re-order the element if specified
            if ele_cfg.ordr == Ele_Order['BG']: ref_canv.lower(ele_cfg.objID)
        except: pass

        ele_cfg.editor_canvObj = ref_canv                                       #set editor canvas reference for later use/updating editor
        ele_cfg.wgtCtl=FrmEdit_bind_widget_control(self.master_ref, ref_canv, ele_cfg)     #bind editor controls to element
        ele_cfg.upd_ele_def_refs()                                              #update external references for new element

    def delWidget(self):
        if self.current_wigtCfg is not None:
            self.current_page.del_element(self.current_wigtCfg)             #delete current selected widget
        else:
            messagebox.showerror("Error", "No element selected to delete!") #or display error
           
    def updCFG_addEle(self, ele_info):
        """Function to add a new page element to the cfg_pages class being edited"""
        tmp_ele_info = ele_info.copy()              #copy passed element info for local modifications
        ele_type = tmp_ele_info.pop('type')         #pop off the element type
        
        #--create the appropriate element type
        if ele_type == DashEle_types['LBL_STAT']: new_cfg = Label_Static(**tmp_ele_info)
        elif ele_type == DashEle_types['LBL_DAT']: new_cfg = Label_Data(**tmp_ele_info)
        elif ele_type == DashEle_types['IND_BLT']: new_cfg = Indicator_Bullet(**tmp_ele_info)
        elif ele_type == DashEle_types['IND_BAR']: new_cfg = Indicator_Bar(**tmp_ele_info)

        self.current_page.update_eleCfg({tmp_ele_info.get('name'): new_cfg})             #add new element to the page config
        eleCfg_ref = self.current_page.get_eleCfg(ele_type, tmp_ele_info.get('name'))    #get element configuration class reference after adding
        return eleCfg_ref           #return element config ref

    def clicked_wgt(self, passed_cfg):
        self.current_wigtCfg = passed_cfg   #update the current working cfg to the one of the newly clicked widget
    
    def enable_editor_controls(self):
        """function updates element control enable/disable status based on the current page"""
        
        pass

#------------widget moving class
class FrmEdit_bind_widget_control:
    '''class for binding click/move/edit actions to elements in the editor'''
    def __init__(self, master, parent_canv, ele_cfg):
        self.master_ref = master                    #reference back to the master window
        self.parent_canv = parent_canv              #parent canvas assocaited with the widget
        self.ele_cfg = ele_cfg                      #base element config data
        self.ele_ID = ele_cfg.objID                 #element reference ID for use with the widget edit/control
        self.upd_refs()                             #update external refs
        self.frameEditor_widgetBind()               #call bindings    

    def upd_refs(self):
        if hasattr(self.ele_cfg, 'padID'):self.pad_id = self.ele_cfg.padID    #background pad reference ID
        else: self.pad_id = None

#------------bind mounse controls to passed widget
    def frameEditor_widgetBind(self):
        self.parent_canv.tag_bind(self.ele_ID, '<ButtonPress-1>', self.widget_click)
        self.parent_canv.tag_bind(self.ele_ID, "<B1-Motion>", self.widget_drag)
        self.parent_canv.tag_bind(self.ele_ID, "<ButtonRelease-1>", self.widget_release)

#------------mouse action functions while editing
    def widget_click(self, evnt):
        self.frmEditor_widgetLocked = True                          #lock widget temporarily
        self.frmEditor_tClick = datetime.now()                      #set time mouse was clicked - for "debounce" of clicks
        self.frmEditor_x0 = evnt.x ; self.frmEditor_y0 = evnt.y     #set the initial "zero" point for the widget being moved (based on mouse position)
        self.uXmoveRect_make(evnt)                                  #make the "positioning" rectangle for visual indication
        self.master_ref.editr_wgtProps.clicked_wgt(self.ele_cfg)    #update the properties view
        self.master_ref.editr_cntl.clicked_wgt(self.ele_cfg)        #update the current clicked widget in the control class
    
    def widget_drag(self, event):
        #--mouse click/unlock for "debounce" of the click/drag
        if(self.frmEditor_widgetLocked):                #if mouse is clicked and widget is locked
            dt = self.delta_ms(self.frmEditor_tClick)   #calc time difference
            if (dt > click_delay):                      #if the "debounce" or time delay has elapsed
                self.frmEditor_widgetLocked = False     #then unlock widget movement
                self.uXhelperGrid_make()                #and draw helper gridlines
        
        #--updating position if its a valid drag
        if (not self.frmEditor_widgetLocked):           #if widget is unlocked, then move it
            self.uXmoveRect_updPos(event)               #update position of the "positioning" rectangle for visual indication
            
    def widget_release(self, event):
        self.uXhelperGrid_del()                                             #delete the helper grid lines
        self.uXmoveRect_del()                                               #delete the "positioning" rectangle
        if (not self.frmEditor_widgetLocked):                               #if widget is unlocked, then calculate updated position
            dx = event.x - self.frmEditor_x0; dy = event.y - self.frmEditor_y0  #calculate change in mouse position
            self.parent_canv.move(self.ele_ID, dx, dy)                              #move parent object
            if self.pad_id is not None: self.parent_canv.move(self.pad_id, dx, dy)  #move background pad
            new_x0 = self.ele_cfg.x0 + dx; new_y0 = self.ele_cfg.y0 + dy    #calc the new X0 and Y0 to update config
            self.ele_cfg.upd_config({'x0': new_x0, 'y0': new_y0})           #update config information with new position
            if(hasattr(self.ele_cfg, 'x1')):                                #if element has an x1, y1, attribute that has to be udpated as well
                new_x1 = self.ele_cfg.x1 + dx; new_y1 = self.ele_cfg.y1 + dy    #calc the new X1 and Y1 to update config
                self.ele_cfg.upd_config({'x1': new_x1, 'y1': new_y1})           #update config information with new position
            self.master_ref.editr_wgtProps.clicked_wgt(self.ele_cfg)        #call function to update the properties view

#------------positioning rectangle actions
    def delta_ms(self, start_time):
        crnt_time = datetime.now()                  #get current time object
        dt = crnt_time - start_time                 #find overall time delta
        dt = math.trunc(dt.total_seconds()*1000)    #convert to ms    
        return dt
   
    def uXmoveRect_make(self, evnt):
        if self.pad_id is not None:
            wX0, wY0, wX1, wY1 = self.parent_canv.bbox(self.pad_id)     #bounding box dims are the outer pad element
        else: wX0, wY0, wX1, wY1 = self.parent_canv.bbox(self.ele_ID)   #otherwise just the object
        self.uxRect_x0 = evnt.x; self.uxRect_y0 = evnt.y                #set the initial "zero" point for "positioning" rectangle                                                        
        self.frmEditor_UXrect = self.parent_canv.create_rectangle(wX0,wY0, wX1,wY1, 
                                                                  outline='black', width=2) #make the "positioning" rectangle
    
    def uXmoveRect_updPos(self, evnt):
        '''---uxRect moving notes
            ~remember that event.x and event.y are the mouse position relative to the 0,0 of the widget
                that is clicked (upper-left corner)
            ~also remember that x_root and y_root are relative to the SCREEN not the widget
        '''
        dx = evnt.x - self.uxRect_x0; self.uxRect_x0=evnt.x     #calculate pixels moved and update new "zero" position
        dy = evnt.y - self.uxRect_y0; self.uxRect_y0=evnt.y
        self.parent_canv.move(self.frmEditor_UXrect, dx, dy)    #move "positioning" rect

    def uXmoveRect_del(self):
        self.parent_canv.delete(self.frmEditor_UXrect)          #delte the "positioning" rectangle

    def uXhelperGrid_make(self):
        """function to draw dotted helper grid lines on the editing canvas"""
        pass

    def uXhelperGrid_del(self):
        """function to delete dotted helper grid lines on the editing canvas"""
        pass

class FrmEdit_widget_place:
    def __init__(self, master, ele_type, passed_wgt_kwarg):
        self.master_ref = master                        #master window ref
        self.ref_canv = master.editr_cntl.current_canv  #canvas to make the widget on
        self.allow_place = False                        #allow placing the widget
        self.ele_type = ele_type                        #type of widget being placed
        self.wgt_kwarg = passed_wgt_kwarg.copy()        #copy of kwargs for widget being placed

        #results vars
        self.placed = tk.BooleanVar(value=False)    #new widget has been placed; needs to be boolvar so wait_variable can be used in main window
        self.placed_coords = {}                     #dict that will hold the placed coords

        self.widgt_width, self.widgt_height = self.preCalc_widgetSize()  #pre-calc width and height for positioning rectangle

        self.ref_canv.bind("<Enter>", self.place_enter)          #bind mouse entering the canvas
        self.ref_canv.bind("<Leave>", self.place_leave)          #bind mouse leaving the canvas
        self.ref_canv.bind("<Motion>", self.place_move)          #bind mouse moving on the canvas
        self.ref_canv.bind('<ButtonPress-1>', self.place_click)  #bind the click action to place label

    def place_enter(self, event):
        if not self.placed.get():
            self.uXmoveRect_make(event)     #make the "positioning" rectangle
            self.allow_place = True         #allow placing the widget if in frame
    
    def place_leave(self, event):
        if not self.placed.get():
            self.uXmoveRect_del()           #delete the "positioning" rectangle
            self.allow_place = False        #do not allow placing the widget if out of frame
    
    def place_move(self, event):
        if not self.placed.get():
            self.uXmoveRect_updPos(event)               #update position of the "positioning" rectangle for visual indication

    def place_click(self, event):
        if not self.placed.get() and self.allow_place:
            self.placed_coords.update({'x0':event.x, 'y0':event.y})         #set the resultant placed coords
            if hasattr(self.wgt_kwarg, 'x1'):                               #if element requires x1, y1 coords then update those as well
                w = self.wgt_kwarg.get('x1') - self.wgt_kwarg.get('x0');        #calc width
                h = self.wgt_kwarg.get('y1') - self.wgt_kwarg.get('y0');        #calc height
                self.placed_coords.update({'x1':event.x+w, 'y1':event.y+h})     #set the new x1, y1
            self.uXmoveRect_del()                                   #delete the "positioning" rectangle
            self.placed.set(True)                                   #update the positioning flag

    def uXmoveRect_make(self, evnt):
        self.uxRect_x0 = evnt.x; self.uxRect_y0 = evnt.y    #calculate the initial "zero" point for "positioning" rectangle
        uxRect_w = self.uxRect_x0+self.widgt_width          #calculate width "end" pixel
        uxRect_h = self.uxRect_y0 + self.widgt_height       #calculate height "end" pixel
        self.frmEditor_UXrect = self.ref_canv.create_rectangle(self.uxRect_x0,self.uxRect_y0,
                                                                uxRect_w, uxRect_h,
                                                                outline='black', width=2)         #make the "positioning" rectangle
    
    def uXmoveRect_updPos(self, evnt):
        '''---uxRect moving notes
            ~remember that event.x and event.y are the mouse position relative to the 0,0 of the widget
                that is clicked (upper-left corner)
            ~also remember that x_root and y_root are relative to the SCREEN not the widget
        '''
        rect = self.frmEditor_UXrect
        prnt_canv = self.ref_canv  #parent canvas
        dx = evnt.x - self.uxRect_x0; self.uxRect_x0=evnt.x     #calculate pixels moved and update new "zero" position
        dy = evnt.y - self.uxRect_y0; self.uxRect_y0=evnt.y
        prnt_canv.move(rect, dx, dy)                            #move "positioning" rect

    def uXmoveRect_del(self):
        self.ref_canv.delete(self.frmEditor_UXrect)    #delte the "positioning" rectangle

    def preCalc_widgetSize(self):
        """function to calculate the widget size before placing. Used to set the helper placement rectangle"""
        tmp_widg_kwargs = self.wgt_kwarg.copy()
        tmp_widg_kwargs.update({'x0':0,'y0':0})                             #add dummy position for the temp widget
        if hasattr(tmp_widg_kwargs, 'x1'):                                  #if element requires x1, y1 coords then update those as well
            w = tmp_widg_kwargs.get('x1') - tmp_widg_kwargs.get('x0');          #calc width
            h = tmp_widg_kwargs.get('y1') - tmp_widg_kwargs.get('y0');          #calc height
            tmp_widg_kwargs.update({'x1':w, 'y1':h})                            #set the new x1, y1
        tmp_eleID, tmp_padID = instance_widget(self.ele_type, 
                                               self.ref_canv, 
                                               tmp_widg_kwargs)             #instance the temp item
        wX0, wY0, wX1, wY1 = self.ref_canv.bbox(tmp_eleID)                  #find the bounding box dims
        if tmp_padID is not None:
            wX0, wY0, wX1, wY1 = self.ref_canv.bbox(tmp_padID)      #bounding box dims are the outer pad element
            self.ref_canv.delete(tmp_padID)                                 #delete the temp object
        else:
            wX0, wY0, wX1, wY1 = self.ref_canv.bbox(tmp_eleID)      #otherwise just the object
        width = wX1 - wX0 ; height = wY1 - wY0                              #calculate width and height
        self.ref_canv.delete(tmp_eleID)                                     #delete the temp object

        return width, height                                                #return calc'd size