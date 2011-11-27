from query import CrawlerDb
from content_processor import ContentProcessor
from settings import LOGGING
import sys, urlparse, urllib2, shutil, glob, robotparser
import logging, logging.config
import traceback

# ===== Init stuff =====

# db init
cdb = CrawlerDb()
cdb.connect()

# content processor init
processor = ContentProcessor(None, None, None)

# logging setup
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("crawler_logger")

# robot parser init
robot = robotparser.RobotFileParser()

if len(sys.argv) < 2:
	logger.info("Error: No start url was passed")
	sys.exit()

l = sys.argv[1:]

cdb.enqueue(l)

def crawl():
	logger.info("Starting (%s)..." % sys.argv[1])
	while True:
		url = cdb.dequeue()
		u = urlparse.urlparse(url)
		robot.set_url('http://'+u[1]+"/robots.txt")
		if not robot.can_fetch('PyCrawler', url.encode('ascii', 'replace')):
			logger.warning("Url disallowed by robots.txt: %s " % url)
			continue
		if not url.startswith('http'):
			logger.warning("Unfollowable link found at %s " % url)
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
			logger.error("Exception at url: %s\n%s" % (url, e))
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

		processor.setInfo(str(url), status, data)
		add_queue = processor.process()
		l = len(add_queue)
		logger.info("Got %s status from %s (Found %i links)" % (status, url, l))
		if l > 0:
			cdb.enqueue(add_queue)	
		cdb.addPage(processor.getDataDict())
		processor.reset()

	logger.info("Finishing...")
	cdb.close()
	logger.info("Done! Goodbye!")

if __name__ == "__main__":
	try:
		crawl()
	except KeyboardInterrupt:
		logger.error("Stopping (KeyboardInterrupt)")
		sys.exit()
	except Exception, e:
		logger.error("EXCEPTION: %s " % e)
		traceback.print_exc()
	
