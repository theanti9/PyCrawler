import sys
import re
import urllib2
import urlparse
import threading
import sqlite3 as sqlite
from BeautifulSoup import BeautifulSoup
# Try to import psyco for JIT compilation
try:
	import psyco
	psyco.full()
except ImportError:
	print "Continuing without psyco JIT compilation!"

"""
The program should take 3 arguments
1) database file name
2) start url
3) crawl depth 
Start out by checking to see if the args are there and
set them to their variables
"""
if len(sys.argv) < 4:
	sys.exit("Not enough arguments!")
else:
	dbname = sys.argv[1]
	starturl = sys.argv[2]
	crawldepth = sys.argv[3]


# Connect to the db and create the tables if they don't already exist
connection = sqlite.connect(db)
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS crawl_index (id INTEGER, parent INTEGER, url VARCHAR(256), title VARCHAR(256), keywords VARCHAR(256) )')
cursor.execute('CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY, parent INTEGER, depth INTEGER, url VARCHAR(256) PRIMARY KEY )')
cursor.execute('CREATE TABLE IF NOT EXISTS status ( s INTEGER, t TEXT )')
connection.commit()

"""
# Check for a start point
if len(sys.argv) < 2:
	print "No starting point! Checking existing queue"
	cursor.execute("SELECT * FROM queue LIMIT 1")
	c = cursor.fetchone()
	if c == None:
		sys.exit("ERROR: No start point! Exiting")
else:
	try:
		if sys.argv[1]:
			cursor.execute("INSERT INTO queue VALUES ( (?) )", (sys.argv[1], ))
			connection.commit()
	except:
		pass
"""	

# Compile keyword and link regex expressions
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
crawled = []

# set crawling status and stick starting url into the queue
cursor.execute("INSERT INTO status VALUES ((?), (?))", (1, "datetime('now')"))
cursor.execute("INSERT INTO queue VALUES ((?), (?), (?))", (None, 0, 0, staturl))
connection.commit()


# insert starting url into queue

class threader ( threading.Thread ):
	# Main run method to run
	def run(self):
		while 1:
			try:
				# Get the first item from the queue
				cursor.execute("SELECT * FROM queue LIMIT 1")
				crawling = cursor.fetchone()
				# Remove the item from the queue
				cursor.execute("DELETE FROM queue WHERE id = (?)", (crawling[0], ))
				connection.commit()
				print crawling
			except KeyError:
				raise StopIteration
			
			# if theres nothing in the que, then set the status to done and exit
			if crawling == None:
				cursor.execute("INSERT INTO status VALUES ((?), (?))", (0, "datetime('now')"))
				connection.commit()
				sys.exit("Done!")
			# Crawl the link
			self.crawl(crawling)
		
			
	def crawl(self, crawling):
		# crawler id
		cid = crawling[0]
		# parent id. 0 if start url
		pid = crawling[1]
		# current depth
		curdepth = crawling[2]
		# crawling urL
		curl = crawling[3]
		# Split the link into its sections
		url = urlparse.urlparse(curl)
		try:
			# Add the link to the already crawled list
			crawled.append(curl)
		except MemoryError:
			# If the crawled array is too big, deleted it and start over
			del crawled[:]
		try:
			# Load the link
			response = urllib2.urlopen(curl)
		except:
			# If it doesn't load, kill the function
			return
		# Read response
		msg = response.read()
		
		# Create the BS object for parsing the doc
		soup = BeautifulSoup(msg)
		# find the title
		title = soup.find('title' limit=1)
			
		keywordlist = keywordregex.findall(msg)
		if len(keywordlist) > 0:
			keywordlist = keywordlist[0]
		else:
			keywordlist = ""
		# Get the links
		links = linkregex.findall(msg)
		title.replace("'", "\'")
		keywordlist.replace("'", "\'")

		# queue up the links
		queue_links(links, cid, curdepth)

		try:
			# Put now crawled link into the db
			cursor.execute("INSERT INTO crawl_index VALUES( (?), (?), (?), (?), (?) )", (cid, pid, curl, title, keywordlist))
			connection.commit()
		except:
			pass
	def queue_links(self, links, cid, curdepth):
		if curdepth < crawldepth:
			# Read the links and inser them into the queue
			for link in (links.pop(0) for _ in xrange(len(links))):
				if link.startswith('/'):
					link = 'http://' + url[1] + link
				elif link.startswith('#'):
					link = 'http://' + url[1] + url[2] + link
				elif not link.startswith('http'):
					link = 'http://' + url[1] + '/' + link
				if link.decode('utf-8') not in crawled:
					try:
						cursor.execute("INSERT INTO queue VALUES ( (?), (?), (?), (?) )", (None, cid, curdepth+1, link))
						connection.commit()
					except:
						continue
		else:
			pass
if __name__ == '__main__':
	# Run main loop
	threader().run()