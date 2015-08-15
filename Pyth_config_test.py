#!/usr/bin/python

import wx, yaml
from passlib.hash import sha256_crypt

#Open the YAML file

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

the_text = cfg['text']
encrypted_password = cfg['password']



class Frame(wx.Frame):
    def __init__(self, title):

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(600,400))
        self.Bind(wx.EVT_CLOSE, lambda evt: self.OnClose(evt, edit_text))
	

	menuBar = wx.MenuBar()

        #File menu

	file_menu = wx.Menu()

	m_exit = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnClose(evt, edit_text), m_exit)

	m_save = file_menu.Append(wx.ID_SAVE,"S&ave\tAlt-S", "Save")
	self.Bind(wx.EVT_MENU, lambda evt: self.OnSave(evt, edit_text), m_save)

	menuBar.Append(file_menu, "File")


	#Settings menu

        settings_menu = wx.Menu()

	m_password_settings = settings_menu.Append(0, "P&assword settings")
	self.Bind(wx.EVT_MENU, self.OnPasswordSettings, m_password_settings)
	

	menuBar.Append(settings_menu, "Settings")

	self.SetMenuBar(menuBar)


	panel = wx.Panel(self)
	box = wx.BoxSizer(wx.VERTICAL)

	edit_text = wx.TextCtrl(panel, -1, the_text, size=(300,90), pos=(10,10), style = wx.TE_MULTILINE)
	box.Add(edit_text, 0, wx.ALL)




	panel.SetSizer(box)
	panel.Layout()

    def OnPasswordSettings(self, event):
	password_frame = PasswordSettings()
	password_frame.Show(True)
	password_frame.MakeModal(True)


    def OnSave(self, event, text):
	text_value = text.GetValue()	
	cfg["text"] = text_value	
	with open("config.yml", "w") as u_cfg:
	    yaml.dump(cfg, u_cfg)

    def Save(self, text):
	text_value = text.GetValue()	
	cfg["text"] = text_value	
	with open("config.yml", "w") as u_cfg:
	    yaml.dump(cfg, u_cfg)

    def OnClose(self, event, text):
	if text.GetValue() != cfg["text"]:
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
	

class PasswordSettings(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, title="Password Settings", pos=(250,250))
	self.Bind(wx.EVT_CLOSE, self.OnClose)	

	panel = wx.Panel(self)
	box = wx.BoxSizer(wx.VERTICAL)

	prompt_text = wx.StaticText(panel, -1, 'Please enter your password:')
	box.Add(prompt_text, 0, wx.ALL)

	edit_text = wx.TextCtrl(panel, -1, '', size=(300,-1), pos=(10,10), style = wx.TE_PASSWORD)
	box.Add(edit_text, 0, wx.ALL)

	enter_button = wx.Button(panel, -1, 'Go')

	enter_button.Bind(wx.EVT_BUTTON, lambda evt: self.OnEnterButton(evt, edit_text.GetValue(), result_text))

	box.Add(enter_button, 0, wx.ALL)

	result_text = wx.TextCtrl(panel, -1, '', style = wx.TE_READONLY, size=(200,-1))
	box.Add(result_text, 0, wx.ALL)

	panel.SetSizer(box)
	panel.Layout()

    def OnEnterButton(self, evt, password, result_text):
	
	hash = encrypted_password
	outcome = sha256_crypt.verify(password, encrypted_password)

	if outcome == True:
	    result_text.SetValue('Correct password!')
	else:
	    result_text.SetValue('Incorrect password!')


    def OnClose(self, evt):
	self.MakeModal(False)
	evt.Skip()
	


app = wx.App(redirect=True)
top = Frame("SHIT Remote Firing System")
top.Show()
app.MainLoop()


