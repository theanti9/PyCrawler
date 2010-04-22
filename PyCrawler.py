import sys
import re
import urllib2
import urlparse
import threading
import sqlite3 as sqlite
# Try to import psyco for JIT compilation
try:
	import psyco
	psyco.full()
except ImportError:
	print "Continuing without psyco JIT compilation!"

# Connect to the db and create the tables if they don't already exist
connection = sqlite.connect('crawl.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS crawl_index ( url VARCHAR(256) PRIMARY KEY, title VARCHAR(256), keywords VARCHAR(256) )')
cursor.execute('CREATE TABLE IF NOT EXISTS queue ( url VARCHAR(256) PRIMARY KEY )')
connection.commit()

# Check for a start point
if len(argv) < 2:
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
		
# Compile keyword and link regex expressions
keywordregex = re.compile('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>')
linkregex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
crawled = []

class threader ( threading.Thread ):
	# Main run method to run
	def run(self):
		while 1:
			try:
				# Get the first item from the queue
				cursor.execute("SELECT * FROM queue LIMIT 1")
				crawling = cursor.fetchone()
				crawling = crawling[0]
				# Remove the item from the queue
				cursor.execute("DELETE FROM queue WHERE url = (?)", (crawling, ))
				connection.commit()
				print crawling
			except KeyError:
				raise StopIteration
			# Crawl the link
			self.crawl(crawling)
			
	def crawl(self, crawling):
		# Split the link into its sections
		url = urlparse.urlparse(crawling)
		try:
			# Add the link to the already crawled list
			crawled.append(crawling)
		except MemoryError:
			# If the crawled array is too big, deleted it and start over
			del crawled[:]
		try:
			# Load the link
			response = urllib2.urlopen(crawling)
		except:
			# If it doesn't load, kill the function
			return
		# Read response
		msg = response.read()
		# Find the title of the page
		startPos = msg.find('<title>')
		if startPos != -1:
			endPos = msg.find('</title>', startPos+7)
			if endPos != -1:
				title = msg[startPos+7:endPos]
		# Get the keywords
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
		queue_links(links)

		try:
			# Put now crawled link into the db
			cursor.execute("INSERT INTO crawl_index VALUES( (?), (?), (?) )", (crawling, title, keywordlist))
			connection.commit()
		except:
			pass
	def queue_links(links):
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
					cursor.execute("INSERT INTO queue VALUES ( (?) )", (link, ))
					connection.commit()
				except:
					continue
if __name__ == '__main__':
	# Run main loop
	threader().run()