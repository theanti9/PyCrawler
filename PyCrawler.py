from query import CrawlerDb
from content_processor import ContentProcessor
from settings import VERBOSE
import sys, urlparse, urllib2

# ===== Init stuff =====

# db init
cdb = CrawlerDb()
cdb.connect()

# content processor init
processor = ContentProcessor(None, None, None)

if len(sys.argv) < 2:
	print "Error: No start url was passed"
	sys.exit()

l = sys.argv[1:]

cdb.enqueue(l)

def crawl():
	print "starting..."
	queue_empty = False
	while True:
		url = cdb.dequeue()
		print url
		if cdb.checkCrawled(url):
			continue
		if url is False:
			queue_empty = True

		# Get HTTPConnection
		#connection = httplib.HTTPConnection(parsed_url.netloc)
		# Make the request
		#connection.request("GET", parsed_url.path)
		# Get response
		#response = connection.getresponse()
		#data = response.read()
		status = 0
		request = None
		try:
			request = urllib2.urlopen(str(url))
		except urllib2.URLError, e:
			print e.reason
		except urllib2.HTTPError, e:
			status = e.code
		if status == 0:
			status = 200
		data = request.read()

		if VERBOSE:
			print "Got %s status from %s" % (status, url)
		processor.setInfo(str(url), status, data)
		add_queue = processor.process()
		l = len(add_queue)
		print "Found %i links" % l
		if l > 0:
			if queue_empty == True:
				queue_empty = False
			cdb.enqueue(add_queue)	
		cdb.addPage(processor.getDataDict())
		processor.reset()
		if queue_empty:
			break

	print "finishing..."
	cdb.close()
	print "done! goodbye!"

if __name__ == "__main__":
	crawl()