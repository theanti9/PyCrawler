#!/usr/bin/python
import sys
import re
import urllib2
import urlparse
import threading
import sqlite3 as sqlite
import robotparser
# Try to import psyco for JIT compilation


"""
The program should take arguments
1) database file name
2) start url
3) crawl depth 
4) domains to limit to, regex (optional)
5) verbose (optional)
Start out by checking to see if the args are there and
set them to their variables
"""
if len(sys.argv) < 4:
	sys.exit("Not enough arguments!")
else:
	dbname = sys.argv[1]
	starturl = sys.argv[2]
	crawldepth = int(sys.argv[3])
if len(sys.argv) >= 5:
	domains = sys.argv[4]
if len(sys.argv) == 6:
	if (sys.argv[5].upper() == "TRUE"):
		verbose = True
	else:
		verbose = False
else:
	domains = False
	verbose = False
# urlparse the start url
surlparsed = urlparse.urlparse(starturl)

# Connect to the db and create the tables if they don't already exist
connection = sqlite.connect(dbname)
cursor = connection.cursor()
# crawl_index: holds all the information of the urls that have been crawled
cursor.execute('CREATE TABLE IF NOT EXISTS crawl_index (crawlid INTEGER, parentid INTEGER, url VARCHAR(256), title VARCHAR(256), keywords VARCHAR(256), status INTEGER )')
# queue: this should be obvious
cursor.execute('CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY, parent INTEGER, depth INTEGER, url VARCHAR(256))')
# status: Contains a record of when crawling was started and stopped. 
# Mostly in place for a future application to watch the crawl interactively.
cursor.execute('CREATE TABLE IF NOT EXISTS status ( s INTEGER, t TEXT )')
connection.commit()

# Compile keyword and link regex expressions
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s(?:.*?\s)*?href=[\'"](.*?)[\'"].*?>')
if domains:
	domainregex = re.compile(domains)
else:
	domainregex = False
crawled = []

# set crawling status and stick starting url into the queue
cursor.execute("INSERT INTO status VALUES ((?), (?))", (1, "datetime('now')"))
cursor.execute("INSERT INTO queue VALUES ((?), (?), (?), (?))", (None, 0, 0, starturl))
connection.commit()


# insert starting url into queue

class threader ( threading.Thread ):
	
	# Parser for robots.txt that helps determine if we are allowed to fetch a url
	rp = robotparser.RobotFileParser()
	
	"""
	run()
	Args:
		none
	the run() method contains the main loop of the program. Each iteration takes the url
	at the top of the queue and starts the crawl of it. 
	"""
	def run(self):
		while 1:
			try:
				# Get the first item from the queue
				cursor.execute("SELECT * FROM queue LIMIT 1")
				crawling = cursor.fetchone()
				# Remove the item from the queue
				cursor.execute("DELETE FROM queue WHERE id = (?)", (crawling[0], ))
				connection.commit()
				if verbose:
					print crawling[3]
			except KeyError:
				raise StopIteration
			except:
				pass
			
			# if theres nothing in the que, then set the status to done and exit
			if crawling == None:
				cursor.execute("INSERT INTO status VALUES ((?), datetime('now'))", (0,))
				connection.commit()
				sys.exit("Done!")
			# Crawl the link
			self.crawl(crawling)
		
	"""
	crawl()
	Args:
		crawling: this should be a url
	
	crawl() opens the page at the "crawling" url, parses it and puts it into the database.
	It looks for the page title, keywords, and links.
	"""
	def crawl(self, crawling):
		# crawler id
		cid = crawling[0]
		# parent id. 0 if start url
		pid = crawling[1]
		# current depth
		curdepth = crawling[2]
		# crawling urL
		curl = crawling[3]
		if domainregex and not domainregex.search(curl):
			return
		# Split the link into its sections
		url = urlparse.urlparse(curl)
		
		try:
			# Have our robot parser grab the robots.txt file and read it
			self.rp.set_url('http://' + url[1] + '/robots.txt')
			self.rp.read()
		
			# If we're not allowed to open a url, return the function to skip it
			if not self.rp.can_fetch('PyCrawler', curl):
				if verbose:
					print curl + " not allowed by robots.txt"
				return
		except:
			pass
			
		try:
			# Add the link to the already crawled list
			crawled.append(curl)
		except MemoryError:
			# If the crawled array is too big, deleted it and start over
			del crawled[:]
		try:
			# Create a Request object
			request = urllib2.Request(curl)
			# Add user-agent header to the request
			request.add_header("User-Agent", "PyCrawler")
			# Build the url opener, open the link and read it into msg
			opener = urllib2.build_opener()
			f = opener.open(request)
			msg = f.read()
			# put meta data in info
			info = f.info() 
		
			
		except urllib2.URLError, e:
			# If it doesn't load, skip this url
			#print e.code
			try: 
				cursor.execute("INSERT INTO crawl_index VALUES( (?), (?), (?), (?), (?), (?) )", (cid, pid, curl, '', '', e.code))
				connection.commit
			except:
				pass

			return
		
		# Find what's between the title tags
		startPos = msg.find('<title>')
		if startPos != -1:
			endPos = msg.find('</title>', startPos+7)
			if endPos != -1:
				title = msg[startPos+7:endPos]
			
		# Start keywords list with whats in the keywords meta tag if there is one
		keywordlist = keywordregex.findall(msg)
		if len(keywordlist) > 0:
			keywordlist = keywordlist[0]
		else:
			keywordlist = ""
			
		
			
		# Get the links
		links = linkregex.findall(msg)
		# queue up the links
		self.queue_links(url, links, cid, curdepth)

		try:
			# Put now crawled link into the db
			cursor.execute("INSERT INTO crawl_index VALUES( (?), (?), (?), (?), (?), (?) )", (cid, pid, curl, title, keywordlist, 200))
			connection.commit()
		except:
			pass
			
			
	def queue_links(self, url, links, cid, curdepth):
		if curdepth < crawldepth:
			# Read the links and inser them into the queue
			for link in links:
				cursor.execute("SELECT url FROM queue WHERE url=?", [link])
				for row in cursor:
					if row[0].decode('utf-8') == url:
						continue
				if link.startswith('/'):
					link = 'http://' + url[1] + link
				elif link.startswith('#'):
					continue
				elif not link.startswith('http'):
					link = urlparse.urljoin(url.geturl(),link)
				
				if link.decode('utf-8') not in crawled:
					try:
						cursor.execute("INSERT INTO queue VALUES ( (?), (?), (?), (?) )", (None, cid, curdepth+1, link))
						connection.commit()
					except:
						continue
		else:
			pass
if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		print "Continuing without psyco JIT compilation!"
	# Run main loop
	threader().run()
