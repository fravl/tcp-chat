import socket
import threading
from typing import List

host = "::" # Listen on all available interfaces (both ipv4 and ipv6)
port = 8080 

class Client():
    def __init__(self, uid: str, client_socket: socket):
        self.uid: str = uid
        self.socket: socket = client_socket
        self.is_online: bool = True
        self.buffered_messages: List[str] = [] 
    
class Group():
    def __init__(self, uid: str):
        self.uid: str = uid
        self.members: List[Client] = [] 


clients = {}
groups = {}

addr = (host, port) 
if socket.has_dualstack_ipv6():
    s = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
else:
    s = socket.create_server(addr)

s.listen(5) # Now wait for client connection.


def broadcast(message: str):
    for v in clients.values():
        v.socket.send(message)


def handle(client: socket, uid: str):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except Exception as e:
            print(e)
            clients.get(uid).is_online = False
            print("Client connection closed")
            client.close()
            break

def receive():
    print("Server started")
    while True:
        client,address = s.accept()
        print(f"Connected with {str(address)}")
        client.send('NICK'.encode('ascii'))
        uid: str = client.recv(1024).decode('ascii')
        clients.update({uid: Client(uid, client)})
        client.send('Connected'.encode('ascii'))
        
        thread = threading.Thread(target=handle, args=(client, uid))
        thread.start()

receive()