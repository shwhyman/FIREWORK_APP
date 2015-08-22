#!/usr/bin/python2

import wx, yaml
from passlib.hash import sha256_crypt

class Frame(wx.Frame):
    def __init__(self, title, config_file_name="config.yml"):

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,400))
        self.Bind(wx.EVT_CLOSE, lambda evt: self.OnClose(evt, edit_text))

	#---OPEN THE YAML FILE---#

	self.config_file_name = config_file_name
	self.config = {}
        with open(config_file_name, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)
	
	arduino_model = ''

	for model in self.config['ARDUINOS']:
	    if self.config['ARDUINOS'][model]['active'] == True:
		arduino_model = model

	self.channel_list = self.config['ARDUINOS'][arduino_model]['channels']
	self.occupied_channels = []
	self.occupied_channels = map(str,self.occupied_channels)
	self.channel_list = map(str, self.channel_list)
  

	menuBar = wx.MenuBar()

        #---FILE MENU---#

	file_menu = wx.Menu()
	m_exit = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnClose(evt, edit_text), m_exit)
	m_save = file_menu.Append(wx.ID_SAVE,"S&ave\tAlt-S", "Save")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnSave(evt, edit_text), m_save)
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

	self.SetMenuBar(menuBar)

	#---TEMPORARY TEXT BOX---#

	self.panel = wx.Panel(self)
	self.box = wx.BoxSizer(wx.VERTICAL)

	edit_text = wx.TextCtrl(self.panel, -1, self.config["text"], size=(300,90), pos=(10,10), style = wx.TE_MULTILINE)
	self.box.Add(edit_text, 0, wx.ALL)

	self.FireGroup_list = []

	#---LOAD LIST OF FIREGROUP OBJECTS FROM CONFIG---#

	for groups_names in self.config["FIREGROUPS"]:
  
	    new_FireGroup = FireGroup(self, self.panel, self.box, wx.ALL)	    
	    self.FireGroup_list.append(new_FireGroup)
	    new_FireGroup.ChangeName(str(self.config["FIREGROUPS"][groups_names]["name"]))

	    if self.config["FIREGROUPS"][groups_names]["channel"] != '':

	        new_FireGroup.ChangeChannel(str(self.config["FIREGROUPS"][groups_names]["channel"]))
	    	    
	        self.occupied_channels.append(str(self.config["FIREGROUPS"][groups_names]["channel"]))
	        self.channel_list.remove(str(self.config["FIREGROUPS"][groups_names]["channel"]))   
	    
 	    for sub_name, sub_channel in self.config["FIREGROUPS"][groups_names]["sub_groups"].iteritems():
		new_sub_group = SubFireGroup(new_FireGroup, new_FireGroup.ver_box, wx.ALL)
		new_FireGroup.ver_box.Add(new_sub_group, 0, 0, 0)
		new_FireGroup.SetSizerAndFit(new_FireGroup.ver_box)
	      
	        new_FireGroup.SubFireGroup_list.append(new_sub_group)

		new_sub_group.ChangeName(str(sub_name))

	        if sub_channel != '':	
		    new_sub_group.ChangeChannel(str(sub_channel))
		    self.occupied_channels.append(str(sub_channel))
		    self.channel_list.remove(str(sub_channel))
	   
	    self.channel_list = sorted(self.channel_list, key=int)	    

            for objects in self.FireGroup_list:
		
	        objects.channel_combo_box.Clear()
		
	        for channels in self.channel_list:
		    objects.channel_combo_box.Append(channels)
	        
	        for sub_objects in objects.SubFireGroup_list:
		    sub_objects.channel_combo_box.Clear()
		    for sub_channels in self.channel_list:
		        sub_objects.channel_combo_box.Append(sub_channels)
		
	    self.box.Add(new_FireGroup, 0, 0, 0)
	    self.panel.SetSizerAndFit(self.box)
   
	self.panel.SetSizer(self.box)
	self.panel.Layout()


    def OnChooseArduino(self, event, name, other_name):
	self.config['ARDUINOS'][name]['active'] = True	
	self.config['ARDUINOS'][other_name]['active'] = False
	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)


    def OnPasswordSettings(self, event):
	password_frame = PasswordSettings(self.config, self.config_file_name)
	password_frame.Show(True)
	password_frame.MakeModal(True)


    def OnSave(self, event, text):
	text_value = text.GetValue()	
	self.config["text"] = str(text_value)	
	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)

	self.config["FIREGROUPS"].clear()	
	
	for group in self.FireGroup_list:
	    name = group.group_name
	    channel = group.current_channel
	    
	    sub_dict = {}	

	    for sub_groups in group.SubFireGroup_list:
		sub_name = sub_groups.subgroup_name
	        sub_channel = sub_groups.current_channel
		sub_dict[str(sub_name)] = str(sub_channel)

	    append_dict = {'channel': str(channel), 'name': str(name), 'sub_groups': sub_dict}
	    

	    self.config["FIREGROUPS"][str(name)] = append_dict
	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)
	 

    def Save(self, text):
	text_value = text.GetValue()	
	self.config["text"] = text_value	
	with open(self.config_file_name, "w") as u_cfg:
	    yaml.dump(self.config, u_cfg)


    def OnClose(self, event, text):
	if text.GetValue() != self.config["text"]:
            dlg = wx.MessageDialog(self, "Would you like to save the changes you have made?", "Save Changes?", wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
	        Frame.Save(self, text)
                self.Destroy()   
	    elif result == wx.ID_NO:
	        self.Destroy()
	else:
	    dlg = wx.MessageDialog(self, "Are you sure you want to quit the application?", "Confirm Exit", wx.YES_NO|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.Destroy()   


    def OnNewGroup(self, evt):
	if not self.channel_list:
	    dlg = wx.MessageDialog(self, "There are no more available channels!", "New Group", wx.OK)
	    result = dlg.ShowModal()
	    dlg.Destroy()
	else:
	    new_FireGroup = FireGroup(self, self.panel, self.box, wx.ALL)
	    self.box.Add(new_FireGroup, 0, 0, 0)
	    self.panel.SetSizerAndFit(self.box)

	    self.FireGroup_list.append(new_FireGroup)	

	    self.panel.Layout()


class PasswordSettings(wx.Frame):
    
    def __init__(self, config, config_file_name):
        wx.Frame.__init__(self, None, title="Password Settings", pos=(250,250))

	self.config = config
	self.config_file_name = config_file_name

	self.Bind(wx.EVT_CLOSE, self.OnClose)	

	panel = wx.Panel(self)
	box = wx.BoxSizer(wx.VERTICAL)

	prompt_text = wx.StaticText(panel, -1, 'Please enter your current password:')
	box.Add(prompt_text, 0, wx.ALL)

	current_password = wx.TextCtrl(panel, -1, '', size=(300,-1), pos=(10,10), style = wx.TE_PASSWORD)
	self.Bind(wx.EVT_TEXT, lambda evt: self.OnTryPassword(evt, current_password, new_password), current_password)
	box.Add(current_password, 0, wx.ALL)


	new_prompt_text = wx.StaticText(panel, -1, 'Please enter a new password:')
	box.Add(new_prompt_text, 0, wx.ALL)

	new_password = wx.TextCtrl(panel, -1, '', size=(300,-1), pos=(10,10), style = wx.TE_PASSWORD)
	box.Add(new_password, 0, wx.ALL)
	self.Bind(wx.EVT_TEXT, lambda evt: self.OnTypeNewPassword(evt, confirm_password), new_password)
	new_password.Disable()

	confirm_prompt_text = wx.StaticText(panel, -1, 'Please confirm the new password:')
	box.Add(confirm_prompt_text, 0, wx.ALL)

	confirm_password = wx.TextCtrl(panel, -1, '', size=(300,-1), pos=(10,10), style = wx.TE_PASSWORD)
	box.Add(confirm_password, 0, wx.ALL)
	self.Bind(wx.EVT_TEXT, lambda evt: self.OnConfirmNewPassword(evt, new_password, enter_button), confirm_password)
	confirm_password.Disable()

	enter_button = wx.Button(panel, -1, 'Change')
	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnEnterButton(evt, new_password.GetValue()), enter_button)
	enter_button.Disable()

	box.Add(enter_button, 0, wx.ALL)

	panel.SetSizer(box)
	panel.Layout()

    def OnTryPassword(self, evt, field_to_compare, field_to_unlock):

	outcome = sha256_crypt.verify(field_to_compare.GetValue(), self.config["password"])	

	if outcome == True: 
	    field_to_unlock.Enable()
	else:
	    field_to_unlock.Disable()

    def OnTypeNewPassword(self, evt, field_to_unlock):

	if evt.GetEventObject().GetValue() != '':
	    field_to_unlock.Enable()
        else:
	    field_to_unlock.Disable()

    def OnConfirmNewPassword(self, evt, field_to_compare, button_to_unlock):
	
	if evt.GetEventObject().GetValue() == field_to_compare.GetValue():
	    button_to_unlock.Enable()
	else:
	    button_to_unlock.Disable()
    

    def OnEnterButton(self, evt, new_password):
	
	dlg = wx.MessageDialog(self, "Are you sure you want to change your password?", "Confirm Password Change", wx.YES_NO|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
	
	if result == wx.ID_YES:
	
	    self.config["password"] = sha256_crypt.encrypt(new_password)	
	    with open(self.config_file_name, "w") as u_cfg:
	        yaml.dump(self.config, u_cfg)

	    self.MakeModal(False)
	    self.Destroy()
		    
	    info_dlg = wx.MessageDialog(self, "Password has been changed.", "Change Password", wx.OK| wx.ICON_INFORMATION)
	    info_result = info_dlg.ShowModal()  
 
    def OnClose(self, evt):
	self.MakeModal(False)
	evt.Skip()
	

class FireGroup(wx.Panel):

    def __init__(self, main_frame, parent, destination, id):
	wx.Panel.__init__(self, parent, id, size = (400,-1), style=wx.SUNKEN_BORDER)

	self.SetBackgroundColour('#d3d3d3')

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

    def OnChangeName(self, evt):
	new_name = evt.GetEventObject().GetValue()
	self.ChangeName(new_name)

    def ChangeName(self, new_name):
	self.group_name = new_name
	self.group_name_field.SetValue(str(self.group_name))

    def ChangeChannel(self, new_channel):
	self.current_channel = new_channel
	self.channel_combo_box.SetValue(str(new_channel))

    def OnGetComboValue(self, evt):	
	
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
	    
	    if self.current_channel in self.main_frame.occupied_channels:
	        self.main_frame.occupied_channels.remove(str(self.current_channel))
	        self.main_frame.channel_list.append(str(self.current_channel))

	    for my_sub_objects in self.SubFireGroup_list:
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
	    self.Destroy()
	    parent.SetSizerAndFit(destination) 
	    

    def OnAdd(self, evt, parent, destination):
	if not self.main_frame.channel_list:
	    dlg = wx.MessageDialog(self, "There are no more available channels!", "New Group", wx.OK)
	    result = dlg.ShowModal()
	    dlg.Destroy()
	else:
	    new_sub_group = SubFireGroup(parent, destination, wx.ALL)
	    destination.Add(new_sub_group, 0, 0, 0)
	    self.SetSizerAndFit(destination)
	    self.parent.SetSizerAndFit(self.destination)
	    self.SubFireGroup_list.append(new_sub_group)
	

    def OnInfo(self, evt):
	info_frame = TextFrame(self, self.blurb)
	info_frame.Show(True)
	info_frame.MakeModal(True)


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
	self.ChangeName(new_name)

    def ChangeName(self, new_name):
	self.subgroup_name = new_name
	self.subgroup_name_field.SetValue(str(self.subgroup_name))


    def ChangeChannel(self, new_channel):
	self.current_channel = new_channel
	self.channel_combo_box.SetValue(str(new_channel))


    def OnGetComboValue(self, evt):	

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
	    parent.parent.SetSizerAndFit(parent.destination)
	    
	
	
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


if __name__ == '__main__':
    app = wx.App(redirect=True)
    top = Frame("SHIT Remote Firing System", config_file_name="config.yml")
    top.Show()
    app.MainLoop()
