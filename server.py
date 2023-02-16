import socket
import threading
from typing import List
from datetime import datetime
from msg_parser import *

host = "::" # Listen on all available interfaces (both ipv4 and ipv6)
port = 8080 

class Client():
    def __init__(self, uid: str, client_socket: socket):
        self.uid: str = uid
        self.socket: socket = client_socket
        self.is_online: bool = True
        self.last_online: datetime.date = datetime.now()
        self.buffered_messages: List[str] = [] 
    
class Group():
    def __init__(self, uid: str, owner: Client):
        self.uid: str = uid
        self.owner: Client = owner
        self.members: List[Client] = [] 

def log(event: str):
    print(f"{datetime.now()}: {event}")


clients = {}
groups = {}

addr = (host, port) 
if socket.has_dualstack_ipv6():
    s = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
else:
    s = socket.create_server(addr)

s.listen(5) # Now wait for client connection.

def send_message(sender_uid: str, reciever_uid: str, message: str):   
    text = f"{sender_uid}@{reciever_uid}: {message}"

    reciever: Client = clients.get(reciever_uid)
    sender: Client = clients.get(sender_uid)
    if(reciever.is_online):
        reciever.socket.send(text.encode('ascii'))
    else:
        reciever.buffered_messages.append(text)    


def process_message(sender_uid: str, message: ParsedMsg): 
    reciever_uid = message["args"]["uid"]   
    message_content = message['args']['msg']
    if(reciever_uid in clients.keys()):
        # handle offline client
        send_message(sender_uid, reciever_uid, message_content)
    if(reciever_uid in groups.keys()):
        print("send to group, not yet implemented")    

def handle(client: socket, uid: str):
    if(not clients.get(uid).is_online):
        clients.get(uid).is_online = True

    while True:
        try:           
            msg: ParsedMsg = parse(client.recv(1024).decode('ascii'))
            match msg["action"]:
                case Action.MESSAGE:                    
                    process_message(uid, msg)
        
        except ParserException as e:
            client.send(f"Error: {e}".encode('ascii'))

        except Exception as e:
            print(e)
            clients.get(uid).is_online = False
            clients.get(uid).last_online = datetime.now()
            log(f"Client {uid} disconnected")
            client.close()
            break

def receive():
    log("Server started")
    while True:
        client,address = s.accept()
        client.send('NICK'.encode('ascii'))
        uid: str = client.recv(1024).decode('ascii')
        log(f"{uid} connected from {str(address)}")
        if(uid not in clients.keys()):
            clients.update({uid: Client(uid, client)})
            client.send(f'Welcome {uid}!'.encode('ascii'))       
        else:
            client.send(f'Welcome back {uid}!'.encode('ascii'))  
            buffered_messages: List[str] = clients.get(uid).buffered_messages
            if len(buffered_messages) > 0:
                for msg in buffered_messages.copy():
                    print(len(buffered_messages))
                    print(msg)
                    client.send(msg.encode('ascii'))   
                    buffered_messages.remove(msg)


        thread = threading.Thread(target=handle, args=(client, uid))
        thread.start()

receive()