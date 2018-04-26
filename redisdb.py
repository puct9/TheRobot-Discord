import os
import urllib
import redis


# Initialize database
URL = urllib.parse.urlparse(os.environ.get('REDISTOGO_URL',
                                           'redis://localhost:6379'))
REDISDB = redis.Redis(host=URL.hostname, port=URL.port,
                      db=0, password=URL.password)
