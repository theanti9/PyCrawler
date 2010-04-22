import sys
import re
import urllib2
import urlparse
import threading
import sqlite3 as sqlite
try:
	import psyco
	psyco.full()
except ImportError:
	print "Continuing without psyco JIT compilation!"

connection = sqlite.connect('crawl.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS crawl_index ( url VARCHAR(256) PRIMARY KEY, title VARCHAR(256), keywords VARCHAR(256) )')
cursor.execute('CREATE TABLE IF NOT EXISTS queue ( url VARCHAR(256) PRIMARY KEY )')
connection.commit()
try:
	cursor.execute("INSERT INTO queue VALUES ( (?) )", (sys.argv[1], ))
	connection.commit()
except:
	pass
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
crawled = []
class threader ( threading.Thread ):
	def run(self):
		while 1:
			try:
				cursor.execute("SELECT * FROM queue LIMIT 1")
				crawling = cursor.fetchone()
				crawling = crawling[0]
				cursor.execute("DELETE FROM queue WHERE url = (?)", (crawling, ))
				connection.commit()
				print crawling
			except KeyError:
				raise StopIteration
			self.crawl(crawling)
			
	def crawl(self, crawling):
		url = urlparse.urlparse(crawling)
		try:
			crawled.append(crawling)
		except MemoryError:
			del crawled[:]
		try:
			response = urllib2.urlopen(crawling)
		except:
			return
		msg = response.read()
		startPos = msg.find('<title>')
		if startPos != -1:
			endPos = msg.find('</title>', startPos+7)
			if endPos != -1:
				title = msg[startPos+7:endPos]
		keywordlist = keywordregex.findall(msg)
		if len(keywordlist) > 0:
			keywordlist = keywordlist[0]
		else:
			keywordlist = ""
		links = linkregex.findall(msg)
		title.replace("'", "\'")
		keywordlist.replace("'", "\'")

		for link in (links.pop(0) for _ in xrange(len(links))):
			if link.startswith('/'):
				link = 'http://' + url[1] + link
			elif link.startswith('#'):
				link = 'http://' + url[1] + url[2] + link
			elif not link.startswith('http'):
				link = 'http://' + url[1] + '/' + link
			if link.decode('utf-8') not in crawled:
				try:
					cursor.execute("INSERT INTO queue VALUES ( (?) )", (link, ))
					connection.commit()
				except:
					continue
		try:
			cursor.execute("INSERT INTO crawl_index VALUES( (?), (?), (?) )", (crawling, title, keywordlist))
			connection.commit()
		except:
			pass
if __name__ == '__main__':
	threader().run()