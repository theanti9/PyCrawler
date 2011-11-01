# settings.py

DATABASE_ENGINE = "sqlite"		# sqlite or mysql
DATABASE_NAME = "PyCrawler"		# Database name
DATABASE_HOST = "/PyCrawler.db"	# Host address of mysql server or file location of sqlite db
DATABASE_PORT = ""				# Port number as a string. Not used with sqlite
DATABASE_USER = ""				# Not used with sqlite
DATABASE_PASS = ""				# Not used with sqlite

VERBOSE = True

# These values are for the text output colors.
# List values are 0-255 RGB values, respectively.

COLOR_SUCCESS = [0, 255, 0]		# Success Color (Green)
COLOR_ERROR = [255, 0, 0]		# Error Color (Red)