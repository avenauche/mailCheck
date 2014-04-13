import sublime, sublime_plugin, imaplib, email, re
from . import Settings
from . import MLStripper

Settings = Settings.Settings()
Settings.option = "1"
Settings.selectedImapFolder = ""
Settings.logoutConfirmationFlag = True;

class emailCommand(sublime_plugin.TextCommand):
		
	def strip_tags(self, html):
		s = MLStripper.MLStripper()
		s.feed(html)
		return s.get_data()

	def run(self, edit):
		settings = Settings()
		mail = settings.mail
		

		# print("email self.settings.option : " + self.settings.option)
		# print("self.settings.selectedImapFolder :: " + self.settings.selectedImapFolder)

		if settings.selectedImapFolder != "" :
			# print("settings.selectedImapFolder :: " + settings.selectedImapFolder)
			mail.select('"'+settings.selectedImapFolder+'"')
		else :	
			# print("defaulting to inbox")
			mail.select("inbox")

		result, data = mail.search(None,  '(UNSEEN)')
		 
		ids = data[0] # data is a list.
		id_list = ids.split() # ids is a space separated string
		latest_email_id = id_list[-1] # get the latest
		 
		result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
		raw_email = data[0][1]
		email_message = email.message_from_string(str(raw_email, encoding='utf-8'))

		fromAddress = "From\t:" +str(email_message['From']).replace("\r", "")+"\n\n" 
		toAddress = "To\t\t: " +str(email_message['To']).replace("\r", "")+"\n\n"
		subjectLine = "Subject\t: " +str(email_message['Subject']).replace("\r", "")+"\n\n"
		self.bodyLine = "No Message"
		for part in email_message.walk():
			# each part is a either non-multipart, or another multipart message
			# that contains further parts... Message is organized like a tree
			if part.get_content_type() == 'text/html':
				self.bodyLine = self.strip_tags(part.get_payload().replace("\r", ""))
				# self.bodyLine = self.bodyLine.replace("\n", "")
			if part.get_content_type() == 'text/plain':
				self.bodyLine = part.get_payload().replace("\r","")

		newTab = self.view.window().new_file()		
		newTab.insert(edit, 0, fromAddress+toAddress+subjectLine+self.bodyLine)


class SelectImapFolderCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.edit = edit
		self.settings = Settings()
		
		folder_list = self.listFolders()
		self.internalFolderNames = [x.decode('utf-8') for x in folder_list]
		self.internalDirectoryNames = [x.split("\" ")[1] for x in self.internalFolderNames]
		self.labelNames = [x.split("\" ")[1].replace("\"","") for x in self.internalFolderNames]
		# gen = self.getRootFolders(self.internalFolderNames)
		# print(gen)
		# self.view.window().show_quick_panel(self.internalFolderNames, self.selectIMAPFolder)
		self.view.window().show_quick_panel(self.labelNames, self.selectIMAPFolder)


	def parse_list_response(self, line):
		return line.replace("\'","").split("\" ")[1]
	
	def listFolders(self, dir=""):
		directory = dir.strip()
		# print("dir ::" + directory)
		
		imap = self.settings.mail;
		status, folder_list = imap.list(directory)

		return folder_list

	# def getRootFolders(self, folderNames): 
	# 		return [x.replace("(\\HasChildren)","") for x in folderNames if x.find("HasChildren") != -1  and x.count("/") == 0 ]	

	# def getFolderName(self, folderNames):
	# 	return folderNames.replace("(\\HasChildren)","") 			

	def selectIMAPFolder(self, selectedIndex):
		
		# print("settings.option : " + self.settings.option)
		self.settings.option = "2"
		# print("settings.option : " + self.settings.option)
		
		self.settings.selectedImapFolder =  self.labelNames[selectedIndex]
		# print("selectedIndex :: " + str(selectedIndex) + " :: folderNames : " + self.settings.selectedImapFolder)

		# if (self.folderNames[selectedIndex].find("HasChildren") != -1) :
		# 	gen = self.getFolderName(self.folderNames[selectedIndex])
		# 	print("folder name : " + str(gen))
			
		# 	folder_list = self.listFolders(gen)
		# 	self.folderNames = [x.decode('utf-8').replace("\"/\"","") for x in folder_list]
		# 	print("sub folders listFolders : "+str(self.folderNames))

		# 	newMenuTab = self.view.window().new_file()
		# 	newMenuTab.insert(self.edit, 0, self.folderNames)

		# else :
		# 	print("No Sub Folders :: " + self.folderNames[selectedIndex])

class logoutCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		self.settings = Settings()
		logoutConfirmationFlag = sublime.ok_cancel_dialog("Would you like to 'Logout' your email? ", "Yes")
		
		if logoutConfirmationFlag == True :
			print("Logout")
			self.settings.mail.logout()
