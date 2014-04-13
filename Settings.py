import sublime, imaplib

class Settings:
	def __call__(self):
		settings = sublime.load_settings('checkMail.sublime-settings')
		self.mail = imaplib.IMAP4_SSL(settings.get("mailServer"))
		self.mail.login(settings.get("mail_id"), settings.get("pwd"))
		return self
