#!/usr/bin/env python

import socket

print "Creating socket...",
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "done."

port=51423

print "Connecting to remote host on port %d..." % port,
s.connect(("10.11.145.35", port))
#s.connect(("127.0.0.1", port))
print "done."


print "Connected from", s.getsockname()
print "Connected to", s.getpeername()

content = ""
try:
    send_len = s.send("http://www.toutiao.com/a6359410912260423938/")
    print send_len
    while 1:
        tmp = s.recv(409600)
        print "Receive data length: " + str(len(tmp))
        if tmp and len(tmp) > 0:
            content = content + tmp
        else:
            break
except :
    print "error"

#print content
s.close()