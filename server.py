import socket
import threading
from typing import List
from datetime import datetime
from msg_parser import *
from exceptions import ServerException, UidNotFoundException
from persistence import Group, Client, Persistence
from colors import bcolors

host = "::" # Listen on all available interfaces (both ipv4 and ipv6)
port = 8080 

def log(event: str):
    print(f"{datetime.now()}: {event}")


addr = (host, port) 
if socket.has_dualstack_ipv6():
    s = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
else:
    s = socket.create_server(addr)

s.listen(5) # Now wait for client connection.

db = Persistence()

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

    if(db.has_client(reciever_uid)):
        reciever: Client = db.get_client(reciever_uid)
        send_message(sender, reciever, message_content)
    elif(db.has_group(reciever_uid)):
        print("send to group, not yet implemented")
    else: 
        raise UidNotFoundException(f"No known group or user with name {reciever_uid}")



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
                    group_uid: str = msg['args']['group_uid']
                    db.create_group(group_uid, client)
                    client.socket.send(f"{bcolors.OKGREEN}Group {group_uid} successfully created{bcolors.ENDC}".encode('ascii')) 
                case Action.GROUP_DELETE:
                    group_uid: str = msg['args']['group_uid']
                    db.delete_group(group_uid, client)
                    client.socket.send(f"{bcolors.OKGREEN}Group {group_uid} successfully deleted{bcolors.ENDC}".encode('ascii'))
                case Action.GROUP_ADD_USER:
                    group: Group = db.get_group(msg['args']['group_uid'])
                    client_uids: List[str] = msg['args']['client_uids']                    
                    for uid in client_uids:
                        try:
                            new_member: Client = db.get_client(uid)
                            if(new_member in group.members):
                                client.socket.send(f"{bcolors.WARNING}User {uid} already in {group.uid}{bcolors.ENDC}".encode('ascii')) 
                            else:
                                group.add_member(new_member, client)
                                client.socket.send(f"{bcolors.OKGREEN}User {uid} added to {group.uid}{bcolors.ENDC}".encode('ascii')) 
                        except UidNotFoundException as e:
                            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}".encode('ascii')) 
                            continue                       
                case Action.GROUP_REMOVE_USER:
                    group: Group = db.get_group(msg['args']['group_uid'])
                    client_uids: List[str] = msg['args']['client_uids']                    
                    for uid in client_uids:
                        try:
                            to_remove: Client = db.get_client(uid)
                            if(to_remove not in group.members):
                                client.socket.send(f"{bcolors.WARNING}User {uid} is not in {group.uid}{bcolors.ENDC}".encode('ascii')) 
                            else:
                                group.remove_member(to_remove, client)
                                client.socket.send(f"{bcolors.OKGREEN}User {uid} removed from {group.uid}{bcolors.ENDC}".encode('ascii')) 
                        except UidNotFoundException as e:
                            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}".encode('ascii')) 
                            continue
                
        except ServerException as e:
            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}".encode('ascii'))        
            
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


        if(not db.has_client(uid)):
            db.create_client(uid, client_socket)
            client_socket.send(f'Welcome {uid}!'.encode('ascii'))       
        else:
            client_socket.send(f'Welcome back {uid}!'.encode('ascii'))  
            buffered_messages: List[str] = db.get_client(uid).buffered_messages
            if len(buffered_messages) > 0:
                for msg in buffered_messages.copy():                   
                    client_socket.send(msg.encode('ascii'))   
                    buffered_messages.remove(msg)


        thread = threading.Thread(target=handle, args=(db.get_client(uid),))
        thread.start()

receive()

