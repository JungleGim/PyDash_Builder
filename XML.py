"""
File:       XML.py
Function:   This file handles any classes or functions used when handling XML files. This is primarily
            when reading or creating dash editor config files, or when generating the output dash
            configuration.
"""

from .sys import *
from .com_defs import *
import xml.etree.ElementTree as ET

def xmlfile_openDialogue(master):
    filepath = filedialog.askopenfilename(defaultextension='.xml',
                                            initialdir=master.editr_cntl.configFile_dir,
                                            filetypes=[('XML','*.xml'), ('All Files','*.*')],
                                            title='Select File')#prompt to get the location and name
    if filepath:
        dir = os.path.dirname(filepath) + '/'                   #set last config file directory
        name = os.path.basename(filepath)                       #set last config file name
        return {'dir':dir, 'name':name}
    else:
        return None

def xmlfile_saveDialogue(master):
    filepath = filedialog.asksaveasfile(defaultextension='.xml',
                                            initialdir=master.editr_cntl.configFile_dir,
                                            filetypes=[('XML','*.xml'), ('All Files','*.*')],
                                            title='Save As')    #prompt to get the location and name
    if filepath:
        dir = os.path.dirname(filepath.name) + '/'              #set last config file directory
        name = os.path.basename(filepath.name)                  #set last config file name
        return {'dir':dir, 'name':name}
    else:
        return None

def XML_open(xmlFile_dir, xmlFile_name):
    xmlFile = None  #opened XML file
    try: xmlFile = ET.parse(xmlFile_dir + xmlFile_name)
    except Exception as e:
        messagebox.showerror("FYI", "Unable to Open XML file. Ensure formatting is correct before trying again. System error is: " + e)
    
    return xmlFile

def XML_save(xmlFile_dir, xmlFile_name, xmlFile):
    try:
        xmlFile.write(xmlFile_dir + xmlFile_name, encoding="utf-8", xml_declaration=True)   #save XML file
    except Exception as e:
        messagebox.showerror("FYI", "Unable to Save XML file. System error is: " + e)

def parseXML(master, config_tree):
    config_root = config_tree.getroot()             #get root element

    #--parse XML file blocks for various dash config options
    '''Updated from using config_root[x] for each element so that order doesn't matter'''
    master.cfg_core = parseXML_CORE(config_root.find('DISP'))       #cycle through DISPLAY (core) config
    master.cfg_theme = parseXML_THEME(config_root.find('THEME'))    #cycle through THEME config
    master.cfg_CAN = parseXML_CAN(config_root.find('CAN'))          #cycle through CAN channels config
    master.cfg_pages = parseXML_PAGES(config_root.find('FRAMES'))   #cycle through page definitions
    buildPages(master, master.cfg_pages)                            #build canvas items for the pages

def parseXML_CORE(block):
    tmp_config = dash_config()                           #temp core config opt instance
    read_DISPconfig = {}                            #temp dict for read values
    
    for disp in block.findall('DISP'):
        for cfg in disp:
            read_DISPconfig.update({cfg.tag : cfg.text})    #append to temp dict
    tmp_config.set_core(**read_DISPconfig)                  #update core dash display values

    return tmp_config

def parseXML_THEME(block):
    tmp_theme = dash_theme()                             #temp dash theme instance
    for clrs in block.findall('COLORS'):        #read all colors
        read_colors = {}                            #temp colors dict for read values
        for clr in clrs.findall('COLOR'):           #cycle through all parsed colors
            read_colors.update({clr.attrib.get('NAME') : clr.text})   #append color to temp dict
        tmp_theme.set_colors(read_colors)           #set theme colors
    for fnts in block.findall('FONTS'):         #read all fonts
        read_fnts = []                              #temp fonts array for read values
        read_fnts_data = {}                         #temp fonts property dict for read values
        for fnt in fnts.findall('FONT'):
            for font_props in fnt:
                read_fnts_data.update({font_props.tag : font_props.text})       #append font to temp dict
            read_fnts.append(dash_font(fnt.attrib.get('NAME'), **read_fnts_data))    #append font data to temp array
        tmp_theme.set_fonts(read_fnts)              #set theme fonts
    for imgs in block.findall('IMAGES'):        #read all images
        read_imgs = {}                              #temp dict for read images
        for img in imgs.findall('IMG'):             #cycle through all parsed images
            read_imgs.update({img.attrib.get('NAME') : img.text})   #append image to temp dict
        tmp_theme.set_imgs(read_imgs)               #set theme images
    for alert in block.findall('ALERT_COLORS'): #read all alert colors
        alert_colors = {}                           #temp dict for read alert color settings
        for alrt_color in alert:                    #read all alert colors
            alert_colors.update({alrt_color.tag:alrt_color.text}) #append to temp dict
        tmp_theme.set_alert_colors(alert_colors)    #set the alert colors
    
    return tmp_theme
   
def parseXML_CAN(block):
    #--get core config values
    CAN_coreCFG = {}                                    #temp dict for CAN core CFG values 
    for canCFG in block.findall('CORE'):
        for cfg in canCFG:
            CAN_coreCFG.update({cfg.tag : cfg.text})    #append to temp dict
    tmp_CAN = CAN_core(**CAN_coreCFG)                   #temp CAN instance
    
    #--get CAN data channels
    for chs in block.findall('CHANNELS'):
        read_CAN_data = {}                                              #temp CANch property dict for read values
        read_CAN_ch = []                                                #temp CANch array for read values

        for ch in chs.findall('CH'):
            read_CAN_data.update({'NAME' : ch.attrib.get('NAME')})      #append CANch Name to temp dict
            for ch_props in ch:
                read_CAN_data.update({ch_props.tag : ch_props.text})    #append CANch props to temp dict
            read_CAN_ch.append(CAN_ch(**read_CAN_data))                 #append CANch data to temp array
        tmp_CAN.set_CAN_ch(read_CAN_ch)                                 #set CANch

    return tmp_CAN

def parseXML_PAGES(block):
    tmp_cfg_pages = {}                          #temp dict for pages
    for child in block:
        read_frame_props = {}                   #temp frame prop dict for core frame props
        read_frame_props.update({'NAME' : child.attrib.get('NAME')})
        for atrb in child:                      #for each frame
            if atrb.tag != 'ELM':
                read_frame_props.update({atrb.tag : atrb.text})
                
        read_frame = dash_page(**read_frame_props)   #new read frame 
        read_frame_props.clear()                #clear temp dict

        for elmnts in child.findall('ELM'):     #elements in frame
            read_elm = {}                       #temp element dict for all read elements
            read_lbl = {}                       #temp static label element dict
            for lbl_static in elmnts.findall('LBL_STATIC'):            
                for lbl in lbl_static:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    read_elm.update({lbl.attrib.get('NAME') : Label_Static(**read_lbl)}) #append static label to read elements
            read_lbl.clear()                    #clear temp dict
            for lbl_data in elmnts.findall('LBL_DATA'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    read_elm.update({lbl.attrib.get('NAME') : Label_Data(**read_lbl)})  #append data labels to read elements
            read_lbl.clear() #clear temp dict
            for lbl_data in elmnts.findall('IND_BLT'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    read_elm.update({lbl.attrib.get('NAME') : Indicator_Bullet(**read_lbl)})  #append data labels to read elements
            read_lbl.clear() #clear temp dict
            for lbl_data in elmnts.findall('IND_BAR'):
                for lbl in lbl_data:
                    read_lbl.update({'NAME' : lbl.attrib.get('NAME')})
                    for atributes in lbl:
                        read_lbl.update({atributes.tag : atributes.text})
                    read_elm.update({lbl.attrib.get('NAME') : Indicator_Bar(**read_lbl)})  #append data labels to read elements
            read_lbl.clear() #clear temp dict

        read_frame.update_eleCfg(read_elm)      #add frame elements
        read_elm.clear()                        #clear temp dict
        tmp_cfg_pages.update({read_frame.name : read_frame})    #add or update frame to config dict

    return tmp_cfg_pages

def editorXML_gen(master_ref):
    '''main save structure to call individual elements'''
    #--shorthand refs to various config paths - primarily for reading code and var length
    cfg = master_ref.cfg_core       #defined core params
    thm = master_ref.cfg_theme      #defined themes
    can = master_ref.cfg_CAN        #defined CAN params
    pgs = master_ref.cfg_pages      #defined pages/frames

    #-----XML structure / children
    #root
    dashCFG = ET.Element('DASH')    #define the root element
    genXML_CORE(dashCFG, cfg)       #add core display information
    genXML_THEME(dashCFG, thm)      #add theme information
    #       COLORS
    #           COLOR...n
    #       FONTS
    #           FONT...n
    #       IMAGES
    #           IMAGE...n
    genXML_CAN(dashCFG, can)        #add CAN information
    #       CAN_core
    #       CAN_CHANNELS
    #           CAN_CH...n
    genXML_PAGES(dashCFG, pgs)      #add frames/pages information
    #       FRAME...n
    #           STATIC_LABELS
    #               LBL...n
    #           DATA_LABELS
    #               LBL...n
    #           BULLET_IND
    #               IND...n
    #           BAR_IND
    #               IND...n

    dashCFG_tree = ET.ElementTree(dashCFG)  #make the tree
    ET.indent(dashCFG_tree, space="  ")     #format
    return dashCFG_tree
    
def genXML_CORE(root_XML, core_cfg):
    cfg_core = ET.SubElement(root_XML,'DISP')       #add core config subelement to root
    for atrb, val in core_cfg.__dict__.items():
        sub = ET.SubElement(cfg_core, atrb.upper()) #add core attribute as subelement
        sub.text = str(val)                         #and add its value

def genXML_THEME(root_XML, theme_cfg):
    cfg_theme = ET.SubElement(root_XML,'THEME')         #add theme config subelement to root
    theme_colors = ET.SubElement(cfg_theme,'COLORS')    #add theme colors subelement to root
    for name, dat in theme_cfg.colors.items():              #cycle through all colors in dict
        color = ET.SubElement(theme_colors, 'COLOR')            #add color
        color.set('NAME', name)                                 #set color name
        color.text = xmlGen_str(dat)                            #set color value

    theme_fonts = ET.SubElement(cfg_theme,'FONTS')      #add theme fonts subelement to root
    for name, dat in theme_cfg.fonts.items():               #cycle through all fonts in dict
        font = ET.SubElement(theme_fonts, 'FONT')               #add font
        font.set('NAME', name)                                  #set font name
        for atrb, val in dat.__dict__.items():                  #cycle through all font dict attributes
            if atrb in dat.fields_editorCFG:                        #if the attribute is flagged for saving in the editor config
                sub = ET.SubElement(font, atrb.upper())             #add as a sub-element, using the attribute name
                sub.text = xmlGen_str(val)                          #and set its value

    theme_images = ET.SubElement(cfg_theme,'IMAGES')    #add theme images subelement to root
    for name, dat in theme_cfg.images.items():              #cycle through all images in dict
        img = ET.SubElement(theme_images, 'IMG')                #add image
        img.set('NAME', name)                                   #set image name
        img.text = xmlGen_str(dat)                              #set image value

    #--add alert colors
    theme_alert = ET.SubElement(cfg_theme, 'ALERT_COLORS')  #add alert color subelement to root
    clr_FG = ET.SubElement(theme_alert, 'ALERT_FG'); clr_FG.text = theme_cfg.alert_FG           #add alert FG color
    clr_WARN = ET.SubElement(theme_alert, 'ALERT_WARN'); clr_WARN.text = theme_cfg.alert_warn   #add alert warning color
    clr_DNGR = ET.SubElement(theme_alert, 'ALERT_DNGR'); clr_DNGR.text = theme_cfg.alert_dngr   #add alert danger color

def genXML_CAN(root_XML, can_cfg):
    CANcfg = ET.SubElement(root_XML,'CAN')              #add CANbus config subelement to root
    CANcfg_core = ET.SubElement(CANcfg,'CORE')          #add CANbus core subelement to CAN config
    for atrb, val in can_cfg.__dict__.items():
        if atrb != 'data_ch' and atrb != 'CAN_CH_ext_ref':  #add all core attributes
            sub = ET.SubElement(CANcfg_core, atrb.upper())      #add core attribute as subelement
            sub.text = xmlGen_str(val)                          #and add its value

    CANcfg_ch = ET.SubElement(CANcfg,'CHANNELS')        #add CAN channels subelement to CAN config
    for name, dat in can_cfg.data_ch.items():               #cycle through all can channels in dict
        ch = ET.SubElement(CANcfg_ch, 'CH')                     #add can channel
        ch.set('NAME', name)                                    #set channel name
        for atrb, val in dat.__dict__.items():                  #cycle through all CANchannel dict attributes
            if atrb in dat.fields_editorCFG:                        #if the attribute is flagged for saving in the editor config
                sub = ET.SubElement(ch, atrb.upper())                       #add channel attribute as a sub-element, using the name
                if(atrb == 'frames'): sub.text = ",".join(str(e) for e in val)  #if frames attribute, then join
                else: sub.text = xmlGen_str(val)                            #and set its value

def genXML_PAGES(root_XML, page_cfg):
    cfg_pages = ET.SubElement(root_XML,'FRAMES')        #add frames/pages config subelement to root
    for frm_name, frm_dat in page_cfg.items():                  #cycle through all pages
        frm = ET.SubElement(cfg_pages, 'FRM')               #add page
        frm.set('NAME', frm_name)                           #set name
        
        for atrb, val in frm_dat.__dict__.items():          #cycle through all frame dict attributes
            if atrb in frm_dat.fields_editorCFG:                #if the attribute is flagged for saving in the editor config
                sub = ET.SubElement(frm, atrb.upper())          #add as a sub-element, using the attribute name
                sub.text = xmlGen_str(val)                      #and set its value
        
        elm = ET.SubElement(frm, 'ELM')                     #add elements
        lbl_stat = ET.SubElement(elm, 'LBL_STATIC')
        genXML_elements(lbl_stat, frm_dat.Lbl_stc.items())      #add static labels

        lbl_dat = ET.SubElement(elm, 'LBL_DATA')
        genXML_elements(lbl_dat, frm_dat.Lbl_dat.items())       #add data labels

        lbl_ind = ET.SubElement(elm, 'IND_BLT')
        genXML_elements(lbl_ind, frm_dat.Ind_blt.items())       #add bullet indicators
        
        lbl_bar = ET.SubElement(elm, 'IND_BAR')
        genXML_elements(lbl_bar, frm_dat.Ind_bar.items())       #add bar indicators

def genXML_elements(xml_parent, elm_dict):
    for name, dat in elm_dict:                          #cycle through all elements
        widg = ET.SubElement(xml_parent, 'LBL')             #add element
        widg.set('NAME', name)                              #set name
        for atrb, val in dat.__dict__.items():                  #cycle through all element dict attributes
            if atrb in dat.fields_editorCFG:                        #if the attribute is flagged for saving in the editor config
                sub = ET.SubElement(widg, atrb.upper())             #add as a sub-element, using the attribute name
                sub.text = xmlGen_str(val)                          #and set its value

def XML_dashCFG_checkErrs(master_ref):
    """function checks current config for any errors that would result in an invalid configuration. Returns a dict
        of errors in the format of {'issue_location':'issue description'}"""
    tmp_err_str = {}                                                    #temp error string to hold feedback
    tmp_err_str.update(master_ref.cfg_theme.XML_dashCFG_checkErrs())    #append any theme errors
    tmp_err_str.update(master_ref.cfg_core.XML_dashCFG_checkErrs())     #append any core config errors
    tmp_err_str.update(master_ref.cfg_CAN.XML_dashCFG_checkErrs())      #append any CAN config errors
    for cfg in master_ref.cfg_pages.values():
        tmp_err_str.update(cfg.XML_dashCFG_checkErrs())                 #append any page config errors

    return tmp_err_str
    