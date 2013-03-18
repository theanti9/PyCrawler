from datetime import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, select

import settings

class CrawlerDb:

	def __init__(self):
		self.connected = False

	def connect(self):
		e = settings.DATABASE_ENGINE + "://"
		p = ""
		if settings.DATABASE_ENGINE == "mysql":
			e += settings.DATABASE_USER + ":" + settings.DATABASE_PASS + "@"
			p = ":" + settings.DATABASE_PORT

		e += settings.DATABASE_HOST + p
		if settings.DATABASE_ENGINE != "sqlite":
			e += "/" +settings.DATABASE_NAME
		self.engine = create_engine(e)
		self.connection = self.engine.connect()
		self.connected = True if self.connection else False
		self.metadata = MetaData()

		# Define the tables
		self.queue_table = Table('queue', self.metadata,
			Column('id', Integer, primary_key=True),
			Column('address', String, nullable=False),
			Column('added', DateTime, nullable=False, default=datetime.now())
		)

		self.crawl_table = Table('crawl', self.metadata,
			Column('id', Integer, primary_key=True),
			Column('address', String, nullable=False),
			Column('http_status', String, nullable=False),
			Column('title', String, nullable=True),
			Column('size', Integer, nullable=True),

		)

		self.keyword_table = Table('keywords', self.metadata,
			Column('id', Integer, primary_key=True),
			Column('page_id', None, ForeignKey('crawl.id')),
			Column('keyword', String, nullable=False),
			Column('weight', Integer, nullable=False),
		)

		# Create the tables
		self.metadata.create_all(self.engine)


	def enqueue(self, urls):
		if not self.connected:
			return False
		if len(urls) == 0:
			return True
		args = [{'address':u.decode("utf8")} for u in urls]
		result = self.connection.execute(self.queue_table.insert(), args)
		if result:
			return True
		return False

	def dequeue(self):
		if not self.connected:
			return False
		# Get the first thing in the queue
		s = select([self.queue_table]).limit(1)
		res = self.connection.execute(s)
		result = res.fetchall()
		res.close()
		# If we get a result
		if len(result) > 0:
			# Remove from the queue
			delres = self.connection.execute(self.queue_table.delete().where(self.queue_table.c.id == result[0][0]))
			if not delres:
				return False
			# Return the row
			return result[0][1]
		return False
	
	def checkCrawled(self, url):
		s =  select([self.crawl_table]).where(self.crawl_table.c.address == url.decode("utf8"))
		result = self.connection.execute(s)
		if len(result.fetchall()) > 0:
			result.close()
			return True
		else:
			result.close()
			return False

	# Data should be a dictionary containing the following
	# key : desc
	# 	address : the url of the page
	# 	http_status : the status code returned by the request
	# 	title : the contents of the <title> element
	# 	size : the of the returned content in bytes
	def addPage(self, data):
		if not self.connected:
			return False
		# Add the page to the crawl table
		try:
			result = self.connection.execute(self.crawl_table.insert().values(address=unicode(data['address']),http_status=data['status'],title=unicode(data['title']),size=data['size']))
		except UnicodeDecodeError:
			return False
		if not result:
			return False
		# generate list of argument dictionaries for the insert many statement
		args = [{"page_id":result.inserted_primary_key[0], "keyword":unicode(k), "weight":w} for k,w in data["keywords"].items()]
		# Add all the keywords
		if len(args) > 0:
			result2 = self.connection.execute(self.keyword_table.insert(),args)
			if not result2:
				return False
		return True

	def close(self):
		self.connection.close()
