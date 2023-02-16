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

class UidNotFoundException(Exception):
    pass
class DuplicateUidException(Exception):
    pass

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

def send_message(sender: Client, reciever: Client, message: str):   
    text = f"{datetime.now()}: {sender.uid}@{reciever.uid}: {message}"
    if(reciever.is_online):
        reciever.socket.send(text.encode('ascii'))
        sender.socket.send(f"{datetime.now()}: {reciever.uid} recieved your message".encode('ascii'))
    else:
        reciever.buffered_messages.append(text)    
        sender.socket.send(f"{datetime.now()}: {reciever.uid} is offline. Last seen at {reciever.last_online}".encode('ascii'))


def process_message(sender: Client, message: ParsedMsg): 
    reciever_uid = message["args"]["uid"]     
    message_content = message['args']['msg']    

    if(reciever_uid in clients.keys()):
        reciever: Client = clients.get(reciever_uid)
        send_message(sender, reciever, message_content)
    elif(reciever_uid in groups.keys()):
        print("send to group, not yet implemented")
    else: 
        raise UidNotFoundException(f"No known group or user with name {reciever_uid}")

def create_group(uid: str, owner: Client):
    if(uid in groups.keys()):
        raise DuplicateUidException(f"Group name {uid} already exists")
    if(uid in clients.keys()):
        raise DuplicateUidException(f"Group name {uid} not allowed. User with such a name exists already.")

    groups.update({uid: Group(uid, owner)})

def delete_group(uid: str):
    if(uid not in groups.keys()):
        raise UidNotFoundException(f"No known group with name {uid}")
    groups.pop(uid)

def group_add_member(group_uid: str, client_uid: str):
    if(group_uid not in groups.keys()):
        raise UidNotFoundException(f"No known group with name {group_uid}")
    if(client_uid not in clients.keys()):
        raise UidNotFoundException(f"No known user with name {group_uid}")

    group: Group = groups.get(group_uid)    
    group.members.append(clients.get(client_uid))

def group_remove_member(group_uid: str, client_uid: str):
    if(group_uid not in groups.keys()):
        raise UidNotFoundException(f"No known group with name {group_uid}")
    if(client_uid not in clients.keys()):
        raise UidNotFoundException(f"No known user with name {group_uid}")

    group: Group = groups.get(group_uid)    
    group.members.remove(clients.get(client_uid))

def client_can_modify_group(group_uid:str, client: Client):
    pass

def handle(client: Client):
    if(not client.is_online):
        client.is_online = True

    while True:
        try:           
            msg: ParsedMsg = parse(client.socket.recv(1024).decode('ascii'))
            match msg["action"]:
                case Action.MESSAGE:                    
                    process_message(client, msg)
                case Action.GROUP_CREATE:
                    create_group(msg['args']['group_uid'], client)
                case Action.GROUP_DELETE:
                    delete_group(msg['args']['group_uid'])
                case Action.GROUP_ADD_USER:
                    pass
                case Action.GROUP_REMOVE_USER:
                    pass
                

        
        except ParserException as e:
            client.socket.send(f"Error: {e}".encode('ascii'))
        except UidNotFoundException as e:
            client.socket.send(f"{e}".encode('ascii'))

        except Exception as e:
            print(e)
            client.is_online = False
            client.last_online = datetime.now()
            log(f"Client {client.uid} disconnected")
            client.socket.close()
            break

def receive():
    log("Server started")
    while True:
        client_socket,address = s.accept()
        client_socket.send('NICK'.encode('ascii'))
        uid: str = client_socket.recv(1024).decode('ascii')
        log(f"{uid} connected from {str(address)}")


        if(uid not in clients.keys()):
            clients.update({uid: Client(uid, client_socket)})
            client_socket.send(f'Welcome {uid}!'.encode('ascii'))       
        else:
            client_socket.send(f'Welcome back {uid}!'.encode('ascii'))  
            buffered_messages: List[str] = clients.get(uid).buffered_messages
            if len(buffered_messages) > 0:
                for msg in buffered_messages.copy():                   
                    client_socket.send(msg.encode('ascii'))   
                    buffered_messages.remove(msg)


        thread = threading.Thread(target=handle, args=(clients.get(uid),))
        thread.start()

receive()

