import re, urlparse

linkregex = re.compile('<a\s(?:.*?\s)*?href=[\'"](.*?)[\'"].*?>')

def ready_queue(address, html):
	url = urlparse.urlparse(str(address))
	links = linkregex.findall(html)
	queue = []
	for link in links:
		#no anchors i.e. video#title
		if "#" in link:
			continue
		if link.startswith("/"):
			queue.append('http://'+url[1]+link)
		elif link.startswith("http") or link.startswith("https"):
			queue.append(link)
		elif link.startswith("#"):
			continue
		else:
			queue.append(urlparse.urljoin(url.geturl(),link))
	return queue
	
