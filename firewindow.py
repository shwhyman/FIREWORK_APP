import wx, yaml
import wx.lib.scrolledpanel as scrolled
from passlib.hash import sha256_crypt
import serial, glob, sys
import time 
import struct


class FireWindow(wx.Frame):

    def __init__(self, parent, config, config_file_name, ports_in_use):
	wx.Frame.__init__(self, parent, title = "Fire Sequence")

	self.parent = parent

	self.ser = serial.Serial(ports_in_use[0], 9600)	
	
	time.sleep(2)
	      
	self.ShowFullScreen(True)
	
	self.config = config

	self.panel = scrolled.ScrolledPanel(self, -1)
		
	
	self.panel.Unbind(wx.EVT_SET_FOCUS)
	self.panel.Unbind(wx.EVT_KILL_FOCUS)

	
	fire_id = wx.NewId()
	abort_id = wx.NewId()
	self.Bind(wx.EVT_MENU, self.OnFire,id=fire_id)
	self.Bind(wx.EVT_MENU, self.OnAbort, id=abort_id)
	
	self.accel_table = wx.AcceleratorTable([(wx.ACCEL_SHIFT | wx.ACCEL_CTRL, wx.WXK_RETURN, fire_id), (wx.ACCEL_SHIFT | wx.ACCEL_CTRL, wx.WXK_ESCAPE, abort_id)])
	self.SetAcceleratorTable(self.accel_table)
		

	self.box = wx.BoxSizer(wx.VERTICAL)
	self.box.AddSpacer(20)

	self.FireGroups = []
	self.counter = 0
	
	#---SETUP FIRE LIST---#


	for groups in parent.FireGroup_list:

	    new_display = FireGroupDisplay(self.panel, -1, groups)
	    self.box.Add(new_display, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=20)
	    self.FireGroups.append(new_display)

	
	self.panel.SetSizer(self.box) 	
	self.panel.Layout()
	self.panel.SetupScrolling()

	self.panel.SetFocus()

    def OnAbort(self, evt):
	
	dlg = wx.PasswordEntryDialog(self, "Please confirm your password to abort the firing system:", "Password Verification Required!")
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
	        caution_dlg = wx.MessageDialog(self, "Are you sure you wish to abort the firing sequence?", "Abort Firing Sequence", wx.YES_NO | wx.ICON_INFORMATION)
	        result = caution_dlg.ShowModal()
	        caution_dlg.Destroy()
	        if result == wx.ID_YES:
		    self.ser.close()
		    yes_dlg = wx.MessageDialog(self, "The firing sequence was successfully aborted.", "Sequence Aborted", wx.OK | wx.ICON_INFORMATION)	
		    yes_dlg.ShowModal()
	            self.MakeModal(False)
		    self.Destroy()
	
    def OnFire(self,evt):
	
        if self.counter == len(self.FireGroups):
	    self.FireGroups[self.counter - 1].SetBackgroundColour('#d3d3d3')
	    finish_dlg = wx.MessageDialog(self, "The firing sequence has finished, and will now exit.", "End Of Sequence", wx.OK | wx.ICON_INFORMATION)
	    finish_dlg.ShowModal()
	    self.MakeModal(False)
	    self.ser.close()
	    self.Destroy()
	    return
 
	if self.FireGroups[self.counter].status.GetLabel() == 'STBY':
	    self.FireGroups[self.counter].status.SetLabel('ARMED')	
	    self.FireGroups[self.counter].status.SetForegroundColour('#FF0000')
	    if self.counter != 0:
		self.FireGroups[self.counter - 1].SetBackgroundColour('#d3d3d3')
	elif self.FireGroups[self.counter].status.GetLabel() == 'ARMED':

	    channel_list = []

	    channel_list.append(self.parent.FireGroup_list[self.counter].current_channel) 
	    for subs in self.parent.FireGroup_list[self.counter].SubFireGroup_list:
		channel_list.append(subs.current_channel)

	    send_string = ''
	    
	    for i in range(0, len(channel_list)):
		if (i > 0):
		    send_string = send_string + ','
		send_string = send_string + channel_list[i]

	    try:		
	        self.ser.write(send_string.encode("utf-8"))

	        self.FireGroups[self.counter].status.SetForegroundColour('#000000')
	        self.FireGroups[self.counter].SetBackgroundColour('#FF0000')
	        self.FireGroups[self.counter].status.SetLabel('FIRED')
	  	
	        self.counter += 1
		
	    except serial.serialutil.SerialException:
	 	
		msgbox = wx.MessageBox('There is no serial device connected! Please connect a device to continue.', 
                       'Serial Error!', wx.ICON_WARNING) 
		     
	        ports = []

		while len(ports) < 1:
	            
		    ports = self.parent.serial_ports()
		    
	            if len(ports) == 1:
                        self.ser = serial.Serial(ports[0], 9600)



class FireGroupDisplay(wx.Panel):

    def __init__(self, parent, id, fire_group):
	wx.Panel.__init__(self, parent, id, style=wx.SUNKEN_BORDER)

	self.SetBackgroundColour('#00E500')
	self.parent = parent

	self.main_grid_box = wx.GridSizer(1, 0, 0, 100)    #divide into two portions

	self.sub_grid_box = wx.GridSizer(len(fire_group.SubFireGroup_list)+1, 2, 5, 100)

	font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

	group_name_field = wx.StaticText(self, label=fire_group.group_name)
	group_name_field.SetFont(font)
	group_channel_field = wx.StaticText(self, label=fire_group.current_channel)
	group_channel_field.SetFont(font)

	self.sub_grid_box.AddMany([(group_name_field,2, wx.EXPAND), (group_channel_field, 1, wx.EXPAND)])

	for sub_groups in fire_group.SubFireGroup_list:
	    sub_name_field = wx.StaticText(self, label=sub_groups.subgroup_name)
	    sub_channel_field = wx.StaticText(self, label=sub_groups.current_channel)
	    sub_name_field.SetFont(font)
	    sub_channel_field.SetFont(font)
	    self.sub_grid_box.AddMany([(sub_name_field,2, wx.EXPAND), (sub_channel_field, 1, wx.EXPAND)])

	self.main_grid_box.Add(self.sub_grid_box,3, flag=wx.EXPAND |wx.Left | wx.RIGHT)

	self.status = wx.StaticText(self,label='STBY')
	self.status.SetFont(font)

	self.main_grid_box.Add(self.status,1,wx.EXPAND)

	self.SetSizer(self.main_grid_box)
