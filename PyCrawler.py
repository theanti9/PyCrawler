from query import CrawlerDb
from content_processor import ContentProcessor
from settings import VERBOSE
import sys, urlparse, urllib2, robotparser

# ===== Init stuff =====

# db init
cdb = CrawlerDb()
cdb.connect()

# content processor init
processor = ContentProcessor(None, None, None)

# robot parser init
robot = robotparser.RobotFileParser()

if len(sys.argv) < 2:
	print "Error: No start url was passed"
	sys.exit()

l = sys.argv[1:]

cdb.enqueue(l)

def crawl():
	print "starting..."
	while True:
		url = cdb.dequeue()
		u = urlparse.urlparse(url)
		robot.set_url('http://'+u[1]+"/robots.txt")
		if not robot.can_fetch('PyCrawler', url):
			print "Url disallowed by robots.txt: %s " % url
			continue
		if not url.startswith('http'):
			print "Unfollowable link found at %s " % url
			continue

		if cdb.checkCrawled(url):
			continue
		if url is False:
			break
		status = 0
		req = urllib2.Request(str(url))
		req.add_header('User-Agent', 'PyCrawler 0.2.0')
		request = None

		try:
			request = urllib2.urlopen(req)
		except urllib2.URLError, e:
			print e
			print "Exception at url: %s" % url
			continue
		except urllib2.HTTPError, e:
			status = e.code
		if status == 0:
			status = 200
		data = request.read()
		processor.setInfo(str(url), status, data)
		ret = processor.process()
		if status != 200:
			continue
		add_queue = []
		for q in ret:
			if not cdb.checkCrawled(q):
				add_queue.append(q)

		l = len(add_queue)
		if VERBOSE:
			print "Got %s status from %s" % (status, url)
			print "Found %i links" % l
		if l > 0:
			cdb.enqueue(add_queue)	
		cdb.addPage(processor.getDataDict())
		processor.reset()

	print "finishing..."
	cdb.close()
	print "done! goodbye!"

if __name__ == "__main__":
	try:
		crawl()
	except KeyboardInterrupt:
		print "Stopping"
		sys.exit()
	except Exception, e:
		print "EXCEPTION: %s " % e
	