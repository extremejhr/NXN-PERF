import os
import gevent.monkey
import multiprocessing

bind = "0.0.0.0:5000"

loglevel = 'debug'
accesslog = "/var/log/gunicorn_access.log"
errorlog = "/var/log/gunicorn_debug.log"

daemon = 'True'

workers = multiprocessing.cpu_count()*2 + 1

worker_class = 'gevent'

