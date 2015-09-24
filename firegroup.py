import wx, yaml
import wx.lib.scrolledpanel as scrolled
from passlib.hash import sha256_crypt
import collections
from collections import OrderedDict
import serial, glob, sys
import time 
import struct


class FireGroup(wx.Panel):

    def __init__(self, main_frame, parent, destination, id):
	wx.Panel.__init__(self, parent, id, size = (400,-1), style=wx.SUNKEN_BORDER)


	self.SetBackgroundColour('#d3d3d3')
        #self.SetBackgroundColour('#D6ADC2')
	self.main_frame = main_frame
	self.parent = parent
	self.destination = destination

	self.blurb = ''
	self.sub_groups = {}

	self.SubFireGroup_list = []

	self.ver_box = wx.BoxSizer(wx.VERTICAL)
	self.main_hor_box = wx.BoxSizer(wx.HORIZONTAL)

	self.group_name = ''
	self.group_name_field = wx.TextCtrl(self, -1, self.group_name, size=(200,-1))
	self.main_hor_box.Add(self.group_name_field, 0, 0, 0)
	self.Bind(wx.EVT_TEXT, self.OnChangeName, self.group_name_field)
	
	self.channel_combo_box = wx.ComboBox(self, -1, choices=map(str, self.main_frame.channel_list), size = (60,-1), style = wx.CB_READONLY)
	self.main_hor_box.Add(self.channel_combo_box, 0, 0, 0)	
	self.Bind(wx.EVT_COMBOBOX, self.OnGetComboValue, self.channel_combo_box)

	self.current_channel = ''
	    	
	add_image = FireGroup.MakeIcon(self,"add_button.png", 30, 30)
	add_button = wx.BitmapButton(self, -1, bitmap = add_image, size=(add_image.GetWidth(),add_image.GetHeight()))
	self.main_hor_box.Add(add_button, 0, 0, 0)
	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnAdd(evt, self, self.ver_box), add_button)

	up_image = FireGroup.MakeIcon(self,"up_arrow.png", 21, 21)
	up_button = wx.BitmapButton(self, -1, bitmap = up_image, size = (up_image.GetWidth()+9, up_image.GetHeight()+9))
	self.main_hor_box.Add(up_button, 0, 0, 0)
	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnUpArrow(evt, self.main_frame), up_button)

	down_image = FireGroup.MakeIcon(self,"down_arrow.png", 21, 21)
	down_button = wx.BitmapButton(self, -1, bitmap = down_image, size = (down_image.GetWidth()+9, down_image.GetHeight()+9))
	self.main_hor_box.Add(down_button, 0, 0, 0)
	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnDownArrow(evt, self.main_frame), down_button)

	info_image = FireGroup.MakeIcon(self,"info_button.png", 21, 21)
	info_button = wx.BitmapButton(self, -1, bitmap = info_image, size = (info_image.GetWidth()+9, info_image.GetHeight()+9))
	self.Bind(wx.EVT_BUTTON, self.OnInfo, info_button)
	self.main_hor_box.Add(info_button, 0, 0, 0)


	delete_image = FireGroup.MakeIcon(self,"delete_button.png", 19, 19)
	delete_button = wx.BitmapButton(self, -1, bitmap = delete_image, size=(add_image.GetWidth(),add_image.GetHeight()))
	self.main_hor_box.Add(delete_button, 0, 0, 0)
	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnDelete(evt, self.parent, self.destination), delete_button)

	self.ver_box.Add(self.main_hor_box, 0, 0, 0)
	self.SetSizer(self.ver_box)

    def OnUpArrow(self, evt, main_frame):

	main_frame.Save()	

        this_index = main_frame.FireGroup_list.index(self)
	if (this_index != 0) & (len(main_frame.FireGroup_list) != 1):
	    main_frame.FireGroup_list[this_index], main_frame.FireGroup_list[this_index - 1] = main_frame.FireGroup_list[this_index - 1], main_frame.FireGroup_list[this_index]
	    self.main_frame.Save()

	    for group in main_frame.FireGroup_list:
		for sub_group in group.SubFireGroup_list:
		    sub_group.Destroy()
	        group.Destroy()

	    del main_frame.FireGroup_list[:]	

	    main_frame.channel_list = main_frame.config['ARDUINOS'][main_frame.arduino_model]['channels']
	    main_frame.occupied_channels = []
	    main_frame.occupied_channels = map(str,main_frame.occupied_channels)
	    main_frame.channel_list = map(str, main_frame.channel_list)
	
	    main_frame.Load()
	    #main_frame.panel.Layout()
	
    def OnDownArrow(self, evt, main_frame):

	main_frame.Save()

	this_index = main_frame.FireGroup_list.index(self)
	if (this_index != len(main_frame.FireGroup_list)-1) & (len(main_frame.FireGroup_list) != 1):
	    main_frame.FireGroup_list[this_index], main_frame.FireGroup_list[this_index + 1] = main_frame.FireGroup_list[this_index + 1], main_frame.FireGroup_list[this_index]
	    main_frame.Save()

	    for group in main_frame.FireGroup_list:
		for sub_group in group.SubFireGroup_list:
		    sub_group.Destroy()
	        group.Destroy()

	    del main_frame.FireGroup_list[:]	

	    main_frame.channel_list = main_frame.config['ARDUINOS'][main_frame.arduino_model]['channels']
	    main_frame.occupied_channels = []
	    main_frame.occupied_channels = map(str,main_frame.occupied_channels)
	    main_frame.channel_list = map(str, main_frame.channel_list)
	
	    main_frame.Load()

    def OnChangeName(self, evt):
	new_name = evt.GetEventObject().GetValue()
	self.group_name = new_name
	self.main_frame.somethings_changed = True

    def ChangeName(self, new_name):
	self.group_name = new_name
	self.group_name_field.SetValue(str(self.group_name))

    def ChangeChannel(self, new_channel):
	self.current_channel = new_channel
	self.channel_combo_box.SetValue(str(new_channel))
	

    def OnGetComboValue(self, evt):	
	
	self.main_frame.somethings_changed = True

        if str(self.current_channel) in self.main_frame.occupied_channels:
	    
	    self.main_frame.occupied_channels.remove(str(self.current_channel))
	    self.main_frame.channel_list.append(str(self.current_channel))

	new_channel = self.channel_combo_box.GetStringSelection()
	
	self.main_frame.occupied_channels.append(str(new_channel))
	self.main_frame.occupied_channels = map(str,self.main_frame.occupied_channels )

	self.current_channel = new_channel

	for x in range(0, len(self.main_frame.occupied_channels)):
	    if self.main_frame.occupied_channels[x] in self.main_frame.channel_list:
		self.main_frame.channel_list.remove(self.main_frame.occupied_channels[x])

	self.main_frame.channel_list = sorted(self.main_frame.channel_list, key=int)

	for objects in self.main_frame.FireGroup_list:
	    objects.channel_combo_box.Clear()
	    for channels in self.main_frame.channel_list:
		objects.channel_combo_box.Append(channels)
	
	    for sub_objects in objects.SubFireGroup_list:
		sub_objects.channel_combo_box.Clear()
		for sub_channels in self.main_frame.channel_list:
		    sub_objects.channel_combo_box.Append(sub_channels)


    def MakeIcon(self,the_file, scalex, scaley):
	image = wx.Image(the_file, wx.BITMAP_TYPE_ANY)
	image = image.Scale(scalex, scaley, wx.IMAGE_QUALITY_HIGH)
	image = image.ConvertToBitmap()
	return image


    def OnDelete(self, evt, parent, destination):
	dlg = wx.MessageDialog(self, "Are you sure you want to delete this group?", "Confirm Deletion", wx.YES_NO|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy() 
	if result == wx.ID_YES:

	    self.main_frame.somethings_changed = True
	    
	    if self.current_channel in self.main_frame.occupied_channels:
	        self.main_frame.occupied_channels.remove(str(self.current_channel))
	        self.main_frame.channel_list.append(str(self.current_channel))

	    for my_sub_objects in self.SubFireGroup_list:
	        if my_sub_objects.current_channel in self.main_frame.occupied_channels:
	    	    self.main_frame.occupied_channels.remove(str(my_sub_objects.current_channel))
	            self.main_frame.channel_list.append(str(my_sub_objects.current_channel))
		self.SubFireGroup_list.remove(my_sub_objects)
	        my_sub_objects.Destroy()
		
	    self.main_frame.channel_list = sorted(self.main_frame.channel_list, key=int)


	    for objects in self.main_frame.FireGroup_list:
	        objects.channel_combo_box.Clear()
	        for channels in self.main_frame.channel_list:
		    objects.channel_combo_box.Append(channels)

		for sub_objects in objects.SubFireGroup_list:
		    sub_objects.channel_combo_box.Clear()
		    for sub_channels in self.main_frame.channel_list:
		        sub_objects.channel_combo_box.Append(sub_channels)
	     

	    self.main_frame.FireGroup_list.remove(self)

	    main_frame = self.main_frame
	
	    self.Destroy()
	    #parent.SetSizerAndFit(destination)  #important
	    main_frame.panel.SetupScrolling(scrollToTop=False)    #new
	    

    def OnAdd(self, evt, parent, destination):
	if not self.main_frame.channel_list:
	    dlg = wx.MessageDialog(self, "There are no more available channels!", "New Group", wx.OK)
	    result = dlg.ShowModal()
	    dlg.Destroy()
	else:
	    new_sub_group = SubFireGroup(parent, destination, wx.ALL)
	    destination.Add(new_sub_group, 0, 0, 0)
	    self.SetSizerAndFit(destination)
	    #self.parent.SetSizerAndFit(self.destination) #old
	    self.SubFireGroup_list.append(new_sub_group)
	    self.main_frame.somethings_changed = True
	    self.main_frame.panel.SetupScrolling(scrollToTop=False) #new
	

    def OnInfo(self, evt):
	info_frame = TextFrame(self, self.blurb)
	info_frame.Show(True)
	info_frame.MakeModal(True)
	self.main_frame.somethings_changed = True


class SubFireGroup(wx.Panel):
	
    def __init__(self, parent, destination, id):
	wx.Panel.__init__(self, parent, id, size = (400, -1))

	self.SetBackgroundColour('#d3d3d3')

	self.parent = parent
	self.destination = destination

	hor_box = wx.BoxSizer(wx.HORIZONTAL)

	self.subgroup_name = ''

	self.subgroup_name_field = wx.TextCtrl(self, -1, self.subgroup_name, size=(200,-1))
	hor_box.Add(self.subgroup_name_field, 0, 0, 0)
	self.Bind(wx.EVT_TEXT, self.OnChangeName, self.subgroup_name_field)

	self.channel_combo_box = wx.ComboBox(self, -1, choices= self.parent.main_frame.channel_list, size = (60,-1))
	hor_box.Add(self.channel_combo_box, 0, 0, 0)
	self.Bind(wx.EVT_COMBOBOX, self.OnGetComboValue, self.channel_combo_box)
	
	self.current_channel = ''

	remove_image = wx.Image("remove_button.png", wx.BITMAP_TYPE_ANY)
	remove_image = remove_image.Scale(28, 28, wx.IMAGE_QUALITY_HIGH)
	remove_image = remove_image.ConvertToBitmap()

	remove_button = wx.BitmapButton(self, -1, bitmap = remove_image, size=(remove_image.GetWidth()+2,remove_image.GetHeight()+2))
	hor_box.Add(remove_button, 0, 0, 0)

	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnRemove(evt, self.parent, self.destination), remove_button)
	
	self.SetSizerAndFit(hor_box)

    def OnChangeName(self, evt):
	new_name = evt.GetEventObject().GetValue()
	self.subgroup_name = new_name
	self.parent.main_frame.somethings_changed = True

    def ChangeName(self, new_name):
	self.subgroup_name = new_name
	self.subgroup_name_field.SetValue(str(self.subgroup_name))


    def ChangeChannel(self, new_channel):
	self.current_channel = new_channel
	self.channel_combo_box.SetValue(str(new_channel))


    def OnGetComboValue(self, evt):	

	self.parent.main_frame.somethings_changed = True

        if self.current_channel in self.parent.main_frame.occupied_channels:
	 
	    self.parent.main_frame.occupied_channels.remove(str(self.current_channel))
	    self.parent.main_frame.channel_list.append(str(self.current_channel))

	new_channel = self.channel_combo_box.GetStringSelection()
	
	self.parent.main_frame.occupied_channels.append(str(new_channel))
	self.parent.main_frame.occupied_channels = map(str,self.parent.main_frame.occupied_channels )

	self.current_channel = new_channel

	for x in range(0, len(self.parent.main_frame.occupied_channels)):
	    if self.parent.main_frame.occupied_channels[x] in self.parent.main_frame.channel_list:
		self.parent.main_frame.channel_list.remove(self.parent.main_frame.occupied_channels[x])

	self.parent.main_frame.channel_list = sorted(self.parent.main_frame.channel_list, key=int)

	for objects in self.parent.main_frame.FireGroup_list:
	    objects.channel_combo_box.Clear()
	    for channels in self.parent.main_frame.channel_list:
		objects.channel_combo_box.Append(channels)
	
	    for sub_objects in objects.SubFireGroup_list:
		sub_objects.channel_combo_box.Clear()
		for sub_channels in self.parent.main_frame.channel_list:
		    sub_objects.channel_combo_box.Append(sub_channels)


    def OnRemove(self, evt, parent, destination):
	dlg = wx.MessageDialog(self.parent, "Are you sure you want to delete this subgroup?", "Confirm Deletion", wx.YES_NO|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy() 
	if result == wx.ID_YES:

	    self.parent.main_frame.somethings_changed = True

	    if self.current_channel in self.parent.main_frame.occupied_channels:
	        self.parent.main_frame.occupied_channels.remove(str(self.current_channel))
	        self.parent.main_frame.channel_list.append(str(self.current_channel))

	    self.parent.main_frame.channel_list = sorted(self.parent.main_frame.channel_list, key=int)

	    for objects in self.parent.main_frame.FireGroup_list:
	        objects.channel_combo_box.Clear()
	        for channels in self.parent.main_frame.channel_list:
		    objects.channel_combo_box.Append(channels)

		for sub_objects in objects.SubFireGroup_list:
		    sub_objects.channel_combo_box.Clear()
		    for sub_channels in self.parent.main_frame.channel_list:
		        sub_objects.channel_combo_box.Append(sub_channels)

	    self.parent.SubFireGroup_list.remove(self)
	    self.Destroy()
	    parent.SetSizerAndFit(destination)
	    #parent.parent.SetSizerAndFit(parent.destination) #old
	    parent.main_frame.panel.SetupScrolling(scrollToTop=False)
	    
	
	
class TextFrame(wx.Frame):
	
    def __init__(self, parent, contents):

	self.contents = contents
	self.parent = parent
	
	wx.Frame.__init__(self, None, title="Group Info", pos=(300,250), size = (300,200), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
	self.Bind(wx.EVT_CLOSE, self.OnClose)

	panel = wx.Panel(self)
	box = wx.BoxSizer(wx.VERTICAL)

	midpan = wx.Panel(panel)

	info_text = wx.TextCtrl(midpan, -1, contents, size=(280,180), pos = (10,10), style = wx.TE_MULTILINE)
	self.Bind(wx.EVT_TEXT, lambda evt: self.OnEnterText(evt, info_text), info_text)

	box.Add(midpan, 1, wx.EXPAND | wx.ALL)
	panel.SetSizer(box)
		
	
    def OnClose(self, evt):
	self.MakeModal(False)
	evt.Skip()

    def OnEnterText(self, evt, text):	
	self.parent.blurb = text.GetValue()
