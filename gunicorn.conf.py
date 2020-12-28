# coding:utf-8
# gunicorn.conf.py
import multiprocessing

# The number of worker processes for handling requests.
workers = multiprocessing.cpu_count() * 2 + 1
# bind = 'unix:/tmp/gunicorn.sock'
# Restart workers when code changes.
reload = True
# The type of workers to use. 
worker_class = 'gevent'
# The Error log file to write to.
errorlog = 'error.log'
loglevel = 'warning'
# A filename to use for the PID file.
pidfile = '/run/gunicorn.pid'
