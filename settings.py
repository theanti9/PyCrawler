# settings.py

DATABASE_ENGINE = "sqlite"		# sqlite or mysql
DATABASE_NAME = "PyCrawler"		# Database name
DATABASE_HOST = "/PyCrawler.db"	# Host address of mysql server or file location of sqlite db
DATABASE_PORT = ""				# Port number as a string. Not used with sqlite
DATABASE_USER = ""				# Not used with sqlite
DATABASE_PASS = ""				# Not used with sqlite

SQLITE_ROTATE_DATABASE_ON_STARTUP = True # Rotate the database to a new one on startup

VERBOSE = True

USE_COLORS = True 				# Whether or not colors should be used when printing text