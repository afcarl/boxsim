import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind(('', 0))
sock.listen(socket.SOMAXCONN)
ipaddr, port = sock.getsockname()
sock.close()

print "Random port {} selected by OS".format(port)
