"""
File:       sys.py
Function:   This file handles any common "system wide" (hence the name "sys") common definitions or includes
            that are used in nearly all files. Good examples of this include common font definitions for
            the application, verision information, constants used, any any other (for lack of a better term)
            "global" information that's common to the application.
"""
import tkinter as tk
from tkinter import messagebox, colorchooser, ttk, filedialog
from tkinter import font as tkFont
from PIL import Image, ImageTk
import re as rgx
import webbrowser as wb
import os

#---help file parameters
help_companyName = "Langholz Racing and Consulting Services"
help_html_gitMain = 'https://github.com/JungleGim/PyDash_Builder/'      #github page for the builder
help_html_gitUserGuide = 'https://github.com/JungleGim/PyDash_Builder/blob/main/User_Guide.md'  #program userguide
help_email = 'tbd_email@gmail.com'                                      #contact email
help_versionText = "Version 0.0"                                        #app version
help_buildDateText = "Build Date: 10/19/2025"                           #app build date

#---fixed hardware PyDash values
dash_xSz = 1024         #X resolution
dash_ySz = 600          #Y resolution
dash_resRatio = dash_xSz/dash_ySz   #X/Y ratio
refrsh_rt = 67          #refresh rate in ms
deflt_backlite = 100    #backlight PWM

#---applciation constants
font_hdr1 = ("Arial", 20)
font_hdr2 = ("Arial", 12)
font_norm1 = ("Arial", 10)
font_norm2 = ("Arial", 8)
font_norm1_hyper = ('Arial', 10, 'underline')
sys_fonts = ['Cascadia Mono', 'Lucida Sans','MS Serif']
PyDash_fonts = {'Cascadia Mono':'Liberation Mono', 'Lucida Sans':'Liberation Sans', 'MS Serif':'Liberation Serif'}

text_example =  'ABCDEFGHIJKLMN\n' \
                'OPQRSTUVWXYZ\n' \
                '1234567890.#%'

brdr_accent = 2                     #accent border to show where certain frames/elements are when they're blank
brdr_accent_offset = brdr_accent*2  #offset for dimentions of panes to account for the debug border

#---misc constants
pad_margin = 2      #the padding margin, in pixels, that the background pad rectangle is sized
pad_radius = 20      #the radius of the background pad polygon
clr_dflt_FG= "#000000"
clr_dflt_WARN= "#C0C0C0"
clr_dflt_DNGR= "#C0C0C0"

#TODO: move these to a global program settings that can be configured by the user on the front-end
click_delay = 50            #delay in miliseconds to check if left-mouse is still held (indicating a click and drag)
sys_wrap_len = 400          #custom warning box width
sys_CAN_base_PID = '0x9A'   #base CAN PID default

#---configuration output constants
dashCFG_PKGname = 'PyDash_Config'       #zip file name of the output package
dashCFG_CFGname = 'PyDash_Config.xml'   #xml config file name
dashCFG_imgDir = 'images'               #output image directory

#---DEBUG: temp values for helping show frame borders and other boundaries easily
dbg_brdr = 2                    #debug/building border thickness for panes
dbg_brdr_offset = dbg_brdr*2    #offset for dimentions of panes to account for the debug border
dbg_brdr_clr_rd = 'red'         #debug/building border color
dbg_brdr_clr_bk = 'black'       #debug/building border color
dbg_brdr_clr_bl = 'blue'        #debug/building border color