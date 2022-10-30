#!/usr/bin/python3
import sys, os, logging
from html import escape
from flup.server.fcgi import WSGIServer

def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    yield "hello world"

if __name__ == '__main__':
    print("Running main")
    logging.info("Running main")
    try:
        WSGIServer(app, bindAddress='/tmp/fastcgi.python.socket-0').run()
    except (KeyboardInterrupt, SystemExit, SystemError):
        logging.info("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
