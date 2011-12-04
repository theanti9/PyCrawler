from multiprocessing import Pool
import re, sys, logging

from ready_queue import ready_queue

logger = logging.getLogger("crawler_logger")

def rankKeywords(text):
	invalid_keywords = ['', ' ', "i", "a", "an", "and", "the", "for", "be", "to", "or", "too", "also"]
	ranks = {}
	text = text.split(' ')
	for t in text:
		if t in invalid_keywords:
			continue
		if not ranks.has_key(t):
			ranks[t] = 1
		else:
			ranks[t] += 1
	return ranks

def stripPunctuation(text):
	pattern = re.compile(r'[^\w\s]')
	return pattern.sub(' ', text)

def stripScript(text):
	pattern = re.compile(r'<script.*?\/script>')
	return pattern.sub(' ', text)

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
				else:
					self.keywords[k] = v
	
	# returns links to queue	
	def processBody(self):
		queue = ready_queue(self.url, self.body)
		#print "found %i links to queue" % len(queue)
		self.text = stripPunctuation(self.remove_html_tags(stripScript(self.body)))
		if len(self.text) > 5000:
			offset = 0
			i = 0
			l = []
			while True:
				j = self.findnth(self.text[i:],' ',500)
				offset += j
				if j == -1:
					break
				l.append(self.text[i:j])
				i = offset + j+1
			logger.debug("processing with %i threads" % len(l))
			try:
				if len(l) == 0:
					return []
				pool = Pool(processes=(len(l)))
				self.keyword_dicts = pool.map(rankKeywords, l)
			except KeyboardInterrupt:
				pool.terminate()
				pool.join()
				sys.exit()
			else:
				pool.close()
				pool.join()
			logger.debug("processed, returned %i dicts" % len(self.keyword_dicts))
		else:
			self.keyword_dicts.append(rankKeywords(self.text))
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
		self.title = self.text[text_lower.find('<title')+6:text_lower.find('</title>')]
		self.head = self.text[text_lower.find('<head')+5:text_lower.find('</head>')]
		self.processHead()
		self.body = self.text[text_lower.find('<body'):text_lower.find('</body>')]
		queue = self.processBody()
		self.combineKeywordLists()
		return queue

	def getDataDict(self):
		for k,v in self.keywords.items():
			if v < 3:
				del self.keywords[k]
		return {"address":self.url, "title":self.title, "status":self.status, "size":self.size, "keywords":self.keywords}