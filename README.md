Setup
=====
- Open settings.py and adjust database settings
- DATABASE_ENGINE can either be "mysql" or "sqlite"
- For sqlite only DATABASE_HOST is used, and it should begin with a '/'
- All other DATABASE_* settings are required for mysql
- DEBUG mode causes the crawler to output some stats that are generated as it goes, and other debug messages
- LOGGING is a dictConfig dictionary to log output to the console and a rotating file, and works out-of-the-box, but can be modified


Current State
=============
- mysql engine untested
- Issue in some situations where the database is locked and queries cannot execute. Presumably an issue only with sqlite's file-based approach

Logging
=======
- DEBUG+ level messages are logged to the console, and INFO+ level messages are logged to a file.
- By default, the file for logging uses a TimedRotatingFileHandler that rolls over at midnight
- Setting DEBUG in the settings toggles wether or not DEBUG level messages are output at all
- Setting USE_COLORS in the settings toggles whether or not messages output to the console use colors depending on the level.

Misc
====
- Designed to be able to run on multiple machines and work together to collect info in central DB
- Queues links into the database to be crawled. This means that any machine running the crawler with the central db can grab from the same queue. Reduces crawling redundancy.
- Thread pool apprach to analyzing keywords in text.
