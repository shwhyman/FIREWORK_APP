#!/usr/bin/python2

import firewindow, firegroup, settings

import wx, yaml
import wx.lib.scrolledpanel as scrolled
from passlib.hash import sha256_crypt
import collections
from collections import OrderedDict
import serial, glob, sys
import time 
import struct

class Frame(wx.Frame):
    def __init__(self, title, config_file_name="config.yml"):

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(455,400))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

	self.somethings_changed = False

	#---OPEN THE YAML FILE---#

	self.config_file_name = config_file_name
	self.config = {}
        with open(config_file_name, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

	self.arduino_model = ''

	for model in self.config['ARDUINOS']:
	    if self.config['ARDUINOS'][model]['active'] == True:
		self.arduino_model = model

	self.channel_list = self.config['ARDUINOS'][self.arduino_model]['channels']
	self.occupied_channels = []
	self.occupied_channels = map(str,self.occupied_channels)
	self.channel_list = map(str, self.channel_list)
  

	menuBar = wx.MenuBar()

        #---FILE MENU---#

	file_menu = wx.Menu()
	m_new = file_menu.Append(wx.ID_ANY, "N&ew", "New")
	m_open = file_menu.Append(wx.ID_ANY, "O&pen...", "Open")
	file_menu.AppendSeparator()
	m_save = file_menu.Append(wx.ID_SAVE,"S&ave\tAlt-S", "Save")
	m_save_as = file_menu.Append(wx.ID_ANY, "S&ave As...\tCtrl-Shft-S", "Save As")
	self.Bind(wx.EVT_MENU, self.OnSave, m_save)
	file_menu.AppendSeparator()
	m_exit = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")
	self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
	menuBar.Append(file_menu, "File")


	#---EDIT MENU---#
	
	edit_menu = wx.Menu()
	m_new_group = edit_menu.Append(-1, "N&ew Group", "Add a new group")
	self.Bind(wx.EVT_MENU, self.OnNewGroup, m_new_group)
	menuBar.Append(edit_menu, "Edit")


	#---SETTINGS MENU---#

        settings_menu = wx.Menu()
	m_password_settings = settings_menu.Append(-1, "Change Password")
	self.Bind(wx.EVT_MENU, self.OnPasswordSettings, m_password_settings)

	arduino_menu = wx.Menu()
	MEGA = arduino_menu.Append(wx.ID_ANY, 'MEGA', kind = wx.ITEM_RADIO)	
	UNO = arduino_menu.Append(wx.ID_ANY, 'UNO', kind = wx.ITEM_RADIO)	
	settings_menu.AppendMenu(wx.ID_ANY, "ARDUINO", arduino_menu)

	if self.config['ARDUINOS']['MEGA']['active'] == True:
	    MEGA.Check()
	else:
	    UNO.Check()

	self.Bind(wx.EVT_MENU, lambda evt: self.OnChooseArduino(evt, 'MEGA', 'UNO' ), MEGA)
	self.Bind(wx.EVT_MENU, lambda evt: self.OnChooseArduino(evt, 'UNO', 'MEGA' ), UNO)
			

	menuBar.Append(settings_menu, "Settings")

	#---FIRE MENU---#

	fire_menu = wx.Menu()

	menuBar.Append(fire_menu, "Fire")
	m_preview = fire_menu.Append(-1, "Preview Firing Sequence")
	m_begin_sequence = fire_menu.Append(-1, "Begin Firing Sequence")
	self.Bind(wx.EVT_MENU, self.OnFire, m_begin_sequence)

	self.SetMenuBar(menuBar)

	#--------------------#

	self.panel = scrolled.ScrolledPanel(self, -1)

	self.panel.Unbind(wx.EVT_SET_FOCUS)
	self.panel.Unbind(wx.EVT_KILL_FOCUS)
	
	self.box = wx.BoxSizer(wx.VERTICAL)
	self.box.AddSpacer(20)

	self.FireGroup_list = []

	#---LOAD LIST OF FIREGROUP OBJECTS FROM CONFIG---#

	self.Load()

	#test_window = FireWindow(self, self.config, self.config_file_name)


	self.panel.Layout()
	self.panel.SetupScrolling(scrollToTop=False) #HERE

	self.somethings_changed = False

    def OnFire(self, evt):

	ports_in_use = self.serial_ports()

	if not ports_in_use:
	    no_ard_dlg = wx.MessageDialog(self, "There is no Arduino connected! Please connect a serial device to begin the firing sequence.", "Serial Device Not Found!", wx.OK | wx.ICON_WARNING)
	    no_ard_dlg.ShowModal()
	    no_ard_dlg.Destroy()
	else:
	    if len(ports_in_use) > 1:
		many_ard_dlg = wx.MessageDialog(self, "More than one serial device was found!", "Serial Device Error!", wx.OK | wx.ICON_WARNING)
	        many_ard_dlg.ShowModal()
	        many_ard_dlg.Destroy()
	    else:
	        dlg = wx.PasswordEntryDialog(self, "Please confirm your password to arm the firing system:", "Password Verification Required!")
	        result = dlg.ShowModal()
	        password_attempt = dlg.GetValue()
	        outcome = sha256_crypt.verify(password_attempt, self.config["password"])
	        dlg.Destroy()
	        if result != wx.ID_CANCEL:
	            if outcome == False:
	                error_dlg = wx.MessageDialog(self, "The password you entered is incorrect!", "Incorrect Password!", wx.OK | wx.ICON_WARNING)
	                error_dlg.ShowModal()
	                error_dlg.Destroy()
	            elif outcome == True:
	                caution_dlg = wx.MessageDialog(self, "The firing system is now live. Once the sequence begins, it may only be aborted with password confirmation. Do you wish to proceed?", "Firing System Armed", wx.YES_NO | wx.ICON_INFORMATION)
	                result = caution_dlg.ShowModal()
	                caution_dlg.Destroy()
	                if result == wx.ID_NO:
		            no_dlg = wx.MessageDialog(self, "The firing sequence was successfully aborted.", "Sequence Aborted", wx.OK | wx.ICON_INFORMATION)
	                    no_dlg.ShowModal()
	                elif result == wx.ID_YES:
		            new_fire_frame = firewindow.FireWindow(self, self.config, self.config_file_name, ports_in_use)
		            new_fire_frame.MakeModal(True)
		

    def Load(self):

	for groups_names in self.config["FIREGROUPS"]:
  
	    new_FireGroup = firegroup.FireGroup(self, self.panel, self.box, wx.ALL)	    
	    self.FireGroup_list.append(new_FireGroup)
	    new_FireGroup.ChangeName(str(self.config["FIREGROUPS"][groups_names]["name"]))
	    new_FireGroup.blurb = self.config["FIREGROUPS"][groups_names]["blurb"]

	    if self.config["FIREGROUPS"][groups_names]["channel"] != '':

	        new_FireGroup.ChangeChannel(str(self.config["FIREGROUPS"][groups_names]["channel"]))
	    	    
	        self.occupied_channels.append(str(self.config["FIREGROUPS"][groups_names]["channel"]))
	        self.channel_list.remove(str(self.config["FIREGROUPS"][groups_names]["channel"]))   
	    
 	    for sub_name, sub_channel in self.config["FIREGROUPS"][groups_names]["sub_groups"].iteritems():
		new_sub_group = firegroup.SubFireGroup(new_FireGroup, new_FireGroup.ver_box, wx.ALL)
		new_FireGroup.ver_box.Add(new_sub_group, 0, 0, 0)
		new_FireGroup.SetSizerAndFit(new_FireGroup.ver_box)
	    
	      
	        new_FireGroup.SubFireGroup_list.append(new_sub_group)

		new_sub_group.ChangeName(str(sub_name[0]))

	        if sub_channel != '':	
		    new_sub_group.ChangeChannel(str(sub_channel))
		    self.occupied_channels.append(str(sub_channel))
		    self.channel_list.remove(str(sub_channel))
	   
	    self.channel_list = sorted(self.channel_list, key=int)	    
	
	    #print len(self.FireGroup_list)

            for objects in self.FireGroup_list:
		
	        objects.channel_combo_box.Clear()
		
	        for channels in self.channel_list:
		    objects.channel_combo_box.Append(channels)
	        
	        for sub_objects in objects.SubFireGroup_list:
		    sub_objects.channel_combo_box.Clear()
		    for sub_channels in self.channel_list:
		        sub_objects.channel_combo_box.Append(sub_channels)
		
	    self.box.Add(new_FireGroup, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)
	  
	    #self.panel.SetSizerAndFit(self.box)  important
   
	self.panel.SetSizer(self.box) 
	self.panel.SetupScrolling(scrollToTop=False)   #New

    def OnChooseArduino(self, event, name, other_name):
	self.config['ARDUINOS'][name]['active'] = True	
	self.config['ARDUINOS'][other_name]['active'] = False
	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)


    def OnPasswordSettings(self, event):
	password_frame = settings.PasswordSettings(self.config, self.config_file_name)
	password_frame.Show(True)
	password_frame.MakeModal(True)


    def Save(self):
	
	self.somethings_changed = False

	self.config["FIREGROUPS"].clear()	
	
	main_ordered_dict = OrderedDict()

	item_number = 0

	for group in self.FireGroup_list:
	    name = group.group_name
	    channel = group.current_channel
	    blurb = group.blurb
	    
	    sub_dict = OrderedDict()		 

	    for sub_groups in group.SubFireGroup_list:

		item_number += 1	       

		sub_name = sub_groups.subgroup_name
	        sub_channel = sub_groups.current_channel
		
		sub_dict.update({(str(sub_name), item_number) : str(sub_channel)})


	    item_number += 1

	    main_ordered_dict.update({str(name)+'_'+str(item_number):{'channel': str(channel), 'name': str(name), 'blurb': str(blurb), 'sub_groups': sub_dict}})
	    
	self.config["FIREGROUPS"] = main_ordered_dict

	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)
 

    def OnSave(self, event):
	self.Save()
	dlg = wx.MessageDialog(self, "The changes you have made have been saved.", "Saved Changes", wx.OK|wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()


    def OnClose(self, event):
	if self.somethings_changed == True:
            dlg = wx.MessageDialog(self, "Would you like to save the changes you have made?", "Save Changes?", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
	        Frame.Save(self)
		#self.ser.close()
                self.Destroy()   
	    elif result == wx.ID_NO:
		#self.ser.close()
	        self.Destroy()
	else:
	    dlg = wx.MessageDialog(self, "Are you sure you want to quit the application?", "Confirm Exit", wx.YES_NO|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
		#self.ser.close()
                self.Destroy()   


    def OnNewGroup(self, evt):
	if not self.channel_list:
	    dlg = wx.MessageDialog(self, "There are no more available channels!", "New Group", wx.OK)
	    result = dlg.ShowModal()
	    dlg.Destroy()
	else:
	    new_FireGroup = firegroup.FireGroup(self, self.panel, self.box, wx.ALL)
	    self.box.Add(new_FireGroup, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)
	    #self.panel.SetSizerAndFit(self.box)   #important

	    self.FireGroup_list.append(new_FireGroup)	
	    self.panel.SetupScrolling(scrollToTop=False)
	    
 
	    self.somethings_changed = True

    def serial_ports(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
	
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
	
        result = []
        
	for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        return result

	 	

if __name__ == '__main__':
    app = wx.App(redirect=True)
    top = Frame("SHIT Remote Firing System", config_file_name="config.yml")
    top.Show()
    app.MainLoop()
