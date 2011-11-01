from query import CrawlerDb
from content_processor import ContentProcessor
from settings import VERBOSE, USE_COLORS, DATABASE_ENGINE, DATABASE_NAME, SQLITE_ROTATE_DATABASE_ON_STARTUP
import sys, urlparse, urllib2, shutil, glob, robotparser
import cPrinter

# ===== Init stuff =====

# db init
cdb = CrawlerDb()
cdb.connect()

# content processor init
processor = ContentProcessor(None, None, None)

# get cprinter
printer = cPrinter.Printer(USE_COLORS)

# robot parser init
robot = robotparser.RobotFileParser()

if len(sys.argv) < 2:
	printer.p("Error: No start url was passed", printer.other)
	sys.exit()

l = sys.argv[1:]

cdb.enqueue(l)

def crawl():
	printer.p("starting...", printer.other)
	while True:
		url = cdb.dequeue()
		u = urlparse.urlparse(url)
		robot.set_url('http://'+u[1]+"/robots.txt")
		if not robot.can_fetch('PyCrawler', url):
			printer.p("Url disallowed by robots.txt: %s " % url, printer.other)
			continue
		if not url.startswith('http'):
			printer.p("Unfollowable link found at %s " % url, printer.other)
			continue

		if cdb.checkCrawled(url):
			continue
		if url is False:
			break
		status = 0
		request = None
		try:
			request = urllib2.urlopen(str(url))
		except urllib2.URLError, e:
			printer.p(e.reason, printer.error)
			printer.p("Exception at url: %s" % url, printer.error)
			
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
		if VERBOSE:
			printer.p("Got %s status from %s" % (status, url), printer.success)
			printer.p("Found %i links" % l, printer.success)
		if l > 0:
			cdb.enqueue(add_queue)	
		cdb.addPage(processor.getDataDict())
		processor.reset()

	printer.p("finishing...", printer.other)
	cdb.close()
	printer.p("done! goodbye!", printer.success)

if __name__ == "__main__":
	if DATABASE_ENGINE == "sqlite" and SQLITE_ROTATE_DATABASE_ON_STARTUP:
		dbs = glob.glob("*.db*")
		index = 1;
		while("%s.db.%s" % (DATABASE_NAME, index) in dbs):
			index += 1
		shutil.copy2(dbs[len(dbs)-1], "%s.db.%s" % (DATABASE_NAME, index))
	try:
		crawl()
	except KeyboardInterrupt:
		printer.p("Stopping", printer.error)
		sys.exit()
	except Exception, e:
		printer.p("EXCEPTION: %s " % e, printer.error)
	
