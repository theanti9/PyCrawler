from query import CrawlerDb
from content_processor import ContentProcessor
from settings import VERBOSE, COLOR_ERROR, COLOR_SUCCESS
import sys, urlparse, urllib2
import cPrinter

# ===== Init stuff =====

# db init
cdb = CrawlerDb()
cdb.connect()

# content processor init
processor = ContentProcessor(None, None, None)

# get cprinter
printer = cPrinter.Printer(COLOR_SUCCESS, COLOR_ERROR)

if len(sys.argv) < 2:
	printer.p("Error: No start url was passed", printer.error)
	sys.exit()

l = sys.argv[1:]

cdb.enqueue(l)

def crawl():
	printer.p("starting...", printer.success)
	queue_empty = False
	while True:
		url = cdb.dequeue()
		if cdb.checkCrawled(url):
			continue
		if url is False:
			queue_empty = True
		status = 0
		request = None
		try:
			request = urllib2.urlopen(str(url))
		except urllib2.URLError, e:
			printer.p(e.reason, printer.error)
		except urllib2.HTTPError, e:
			status = e.code
		if status == 0:
			status = 200
		data = request.read()

		processor.setInfo(str(url), status, data)
		add_queue = processor.process()
		l = len(add_queue)
		if VERBOSE:
			printer.p("Got %s status from %s" % (status, url), printer.success)
			printer.p("Found %i links" % l, printer.success)
		if l > 0:
			if queue_empty == True:
				queue_empty = False
			cdb.enqueue(add_queue)	
		cdb.addPage(processor.getDataDict())
		processor.reset()
		if queue_empty:
			break

	printer.p("finishing...", printer.success)
	cdb.close()
	printer.p("done! goodbye!", printer.success)

if __name__ == "__main__":
	crawl()