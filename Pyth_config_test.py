#!/usr/bin/python2

import wx, yaml
from passlib.hash import sha256_crypt

class Frame(wx.Frame):
    def __init__(self, title, config_file_name="config.yml"):

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,400))
        self.Bind(wx.EVT_CLOSE, lambda evt: self.OnClose(evt, edit_text))

	#Open the YAML file

	self.config_file_name = config_file_name
	self.config = {}
        with open(config_file_name, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)


	menuBar = wx.MenuBar()

        #File menu

	file_menu = wx.Menu()
	m_exit = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnClose(evt, edit_text), m_exit)
	m_save = file_menu.Append(wx.ID_SAVE,"S&ave\tAlt-S", "Save")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnSave(evt, edit_text), m_save)
	menuBar.Append(file_menu, "File")


	#Edit menu
	
	edit_menu = wx.Menu()
	m_new_group = edit_menu.Append(-1, "N&ew Group", "Add a new group")
	self.Bind(wx.EVT_MENU, self.OnNewGroup, m_new_group)
	menuBar.Append(edit_menu, "Edit")


	#Settings menu

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

	self.panel = wx.Panel(self)
	self.box = wx.BoxSizer(wx.VERTICAL)

	edit_text = wx.TextCtrl(self.panel, -1, self.config["text"], size=(300,90), pos=(10,10), style = wx.TE_MULTILINE)
	self.box.Add(edit_text, 0, wx.ALL)


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
	self.config["text"] = text_value	
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
	test_FireGroup = FireGroup(self.panel, self.box, wx.ALL)
	self.box.Add(test_FireGroup, 0, 0, 0)
	self.panel.SetSizerAndFit(self.box)
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

    def __init__(self, parent, destination, id):
	wx.Panel.__init__(self, parent, id, size = (400,-1), style=wx.SUNKEN_BORDER)

	self.parent = parent
	self.destination = destination

	self.blurb = ''
	self.sub_groups = {}

	self.SetBackgroundColour('#d3d3d3')

	self.ver_box = wx.BoxSizer(wx.VERTICAL)

	self.main_hor_box = wx.BoxSizer(wx.HORIZONTAL)

	group_name = wx.TextCtrl(self, -1, 'Title', size=(200,-1))
	self.main_hor_box.Add(group_name, 0, 0, 0)

	self.group_name = group_name.GetValue()

	combo_box = wx.ComboBox(self, -1, choices=['1', '2'], size = (60,-1))
	self.main_hor_box.Add(combo_box, 0, 0, 0)

	

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
	    self.GetName()
	    self.Destroy()
	    parent.SetSizerAndFit(destination) 
	    

    def OnAdd(self, evt, parent, destination):
	new_sub_group = SubFireGroup(parent, destination, wx.ALL)
	destination.Add(new_sub_group, 0, 0, 0)
	self.SetSizerAndFit(destination)
	self.parent.SetSizerAndFit(self.destination)
	

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

	subgroup_name = wx.TextCtrl(self, -1, 'Sub Title', size=(200,-1))
	hor_box.Add(subgroup_name, 0, 0, 0)
	combo_box = wx.ComboBox(self, -1, choices=['1', '2'], size = (60,-1))
	hor_box.Add(combo_box, 0, 0, 0)

	remove_image = wx.Image("remove_button.png", wx.BITMAP_TYPE_ANY)
	remove_image = remove_image.Scale(28, 28, wx.IMAGE_QUALITY_HIGH)
	remove_image = remove_image.ConvertToBitmap()

	remove_button = wx.BitmapButton(self, -1, bitmap = remove_image, size=(remove_image.GetWidth()+2,remove_image.GetHeight()+2))
	hor_box.Add(remove_button, 0, 0, 0)

	self.Bind(wx.EVT_BUTTON, lambda evt: self.OnRemove(evt, self.parent, self.destination), remove_button)
	
	self.SetSizerAndFit(hor_box)

    def OnRemove(self, evt, parent, destination):
	dlg = wx.MessageDialog(self.parent, "Are you sure you want to delete this subgroup?", "Confirm Deletion", wx.YES_NO|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy() 
	if result == wx.ID_YES:
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


