#!/usr/bin/env python
import random
import socket, traceback
import sys
import urllib2
import json
import time
import urlparse

import Queue
import threading
default_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.102 Safari/537.36'
}
last_request_time={}
def Download(req_url):
    parsedTuple = urlparse.urlparse(req_url)
    host = parsedTuple.hostname
    global  last_request_time

    if (host in last_request_time  and time.time() - last_request_time[host] < 3.0) :
        sleep_time = random.randint(3, 6)  # '%.2f' % random.random()
        print >> sys.stderr, "sleep seconds: " + str(sleep_time)
        time.sleep(sleep_time)

    last_request_time[host] = time.time()
    try:
        req = urllib2.Request(req_url, headers=default_headers)
        page = urllib2.urlopen(req, timeout=20)
        content = page.read()
    except:
        print >> sys.stderr, "request url: " + req_url
        traceback.print_exc()
        return ""
    return content

class Job(object):
    def __init__(self, priority, queue, socket):
        self.priority = priority
        self.queue = queue
        self.socket = socket
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)








host = ''                               # Bind to all interfaces
port = 51423

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))

s.listen(1)

while 1:
    try:
        clientsock, clientaddr = s.accept()
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()
        continue

    # Process the connection

    try:
        print "Got connection from", clientsock.getpeername()
        # Process the request here
        req_url = clientsock.recv(1024)
        print req_url
        if (len(req_url) == 0):
            print "Error url get from remote"
        content = ""
        if (len(req_url) != 0):
            content = Download(req_url)
        send_len = clientsock.sendall(content)
        print >> sys.stderr, "Get data length: " + str(len(content)) + ", send the data: " + str(send_len)



    except (KeyboardInterrupt, SystemExit):
        print "Error"
        raise
    except:
        traceback.print_exc()

    # Close the connection

    try:
        clientsock.close()
    except KeyboardInterrupt:
        raise
    except:
        traceback.print_exc()