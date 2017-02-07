
import socket
import threading
import SocketServer
import urlparse
import random
import socket, traceback
import sys
import urllib2
import json
import time

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

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        request_url = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = Download(request_url)
        self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    HOST, PORT =  '', 51424
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    server_thread.join()