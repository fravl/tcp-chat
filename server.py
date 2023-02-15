import socket

host = "::" # Listen on all available interfaces (both ipv4 and ipv6)
port = 8080 

addr = (host, port) 
if socket.has_dualstack_ipv6():
    s = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
else:
    s = socket.create_server(addr)

s.listen(5) # Now wait for client connection.
while True:
    c, addr = s.accept() # Establish connection with client.
    print('Got connection from', addr)
    c.send('Thank you for connecting'.encode())
    c.close() # Close the connection