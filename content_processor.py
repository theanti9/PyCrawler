from ready_queue import ready_queue

from multiprocessing import Pool

import re, sys

def rankKeywords(text):
	invalid_keywords = ['', ' ', "i", "a", "an", "and", "the", "for", "be", "to", "or", "too", "also"]
	ranks = {}
	text = text.split(' ')
	for t in text:
		if t in invalid_keywords:
			continue
		if not ranks.has_key(t):
			print "adding %s" % t
			ranks[t] = 1
		else:
			ranks[t] += 1
			print "setting %s to %i" % (t, ranks[t])
	return ranks

def stripPunctuation(text):
	pattern = re.compile(r'[^\w\s]')
	return pattern.sub('', text)
class ContentProcessor:
	
	def __init__(self, url, status, text):
		self.keyword_dicts = []
		self.invalid_keywords = ['', ' ', "i", "a", "an", "and", "the", "for", "be", "to", "or", "too", "also"]
		self.keywords = {}
		self.text = text
		self.size = 0
		self.url = url
		self.status = status

	def setText(self, text):
		self.text = text
		self.size = len(text)

	def setUrl(self, url):
		self.url = url

	def setStatus(self, status):
		self.status = status

	def setInfo(self, url, status, text):
		self.url = url
		self.status = status
		self.text = text
		self.size = len(text)

	def reset(self):
		self.keyword_dicts = []
		self.keywords = {}
		self.text = None
		self.head = None
		self.body = None
		self.title = None
		self.size = 0
		self.status = None

	def combineKeywordLists(self):
		if len(self.keyword_dicts) == 1:
			self.keywords = self.keyword_dicts[0]
			return
		for l in self.keyword_dicts:
			for k,v in l.items():
				if self.keywords.has_key(k):
					self.keywords[k] += v
					print "setting %s to %i" %(k,self.keywords[k])
				else:
					self.keywords[k] = v
					print "setting %s to %i" %(k,v)
	
	# returns links to queue	
	def processBody(self):
		queue = ready_queue(self.url, self.body)
		print "found %i links to queue" % len(queue)
		self.text = stripPunctuation(self.remove_html_tags(self.body))
		if len(self.text) > 5000:
			offset = 0
			i = 0
			l = []
			print "splitting text"
			while True:
				j = self.findnth(self.text[i:],' ',500)
				offset += j
				print "SPLIT: 500th space at %i" % j
				if j == -1:
					print "appending from %i on" % i
					l.append(self.text[i:])
					break
				print "appending from %i to %i" % (i,j)
				l.append(self.text[i:j])
				i = offset + j+1
			print "processing with %i threads" % len(l)
			pool = Pool(processes=(len(l)))
			self.keyword_dicts = pool.map(rankKeywords, l)
			print "processed, returned %i dicts" % len(self.keyword_dicts)
		else:
			self.keyword_dicts.append(self.rankKeywords(self.text))
		return queue
		
	def processHead(self):
		pass

	def remove_html_tags(self, data):
		p = re.compile(r'<.*?>')
		return p.sub('', data)

	def findnth(self, haystack, needle, n):
		parts = haystack.split(needle, n)
		if len(parts) <= n:
			return -1
		return len(haystack)-len(parts[-1])-len(needle)

	# returns the queue from processBody
	def process(self):
		text_lower = self.text.lower()
		print "Finding title"
		self.title = self.text[text_lower.find('<title')+6:text_lower.find('</title>')]
		print "Found title: %s" % self.title
		print "Finding head"
		self.head = self.text[text_lower.find('<head')+5:text_lower.find('</head>')]
		print "Found head of length %i" % len(self.head)
		self.processHead()
		print "Finding body"
		self.body = self.text[text_lower.find('<body'):text_lower.find('</body>')]
		print "Found body of length %i" % len(self.body)
		queue = self.processBody()
		print "combining keyword lists"
		self.combineKeywordLists()
		return queue

	def getDataDict(self):
		return {"address":self.url, "title":self.title, "status":self.status, "size":self.size, "keywords":self.keywords}