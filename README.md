Setup
=====
- Open settings.py and adjust database settings
- DATABASE_ENGINE can either be "mysql" or "sqlite"
- For sqlite only DATABASE_HOST is used, and it should begin with a '/'
- All other DATABASE_* settings are required for mysql
- VERBOSE mode causes the crawler to output some stats that are generated as it goes


Current State
=============
- mysql engine untested
- Lots of debug prints
- Issue in some situations where the database is locked and queries cannot execute. Presumably an issue only with sqlite's file-based approach

Misc
====
- Designed to be able to run on multiple machines and work together to collect info in central DB
- Queues links into the database to be crawled. This means that any machine running the crawler with the central db can grab from the same queue. Reduces crawling redundancy.
- Thread pool apprach to analyzing keywords in text.
