from html.parser import HTMLParser

class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.fed = []
		self.omitHeadFlag = False

	def handle_starttag(self, tag, attrs):
		if tag == "head":
			self.omitHeadFlag = True

	def handle_endtag(self, tag):
		if tag == "head" :
			self.omitHeadFlag = False

	def handle_data(self, d):
		if self.omitHeadFlag == False :
			self.fed.append(d)
			
	def get_data(self):
		return ''.join(self.fed)
