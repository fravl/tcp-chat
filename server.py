import socket
import threading
from typing import List
from datetime import datetime
from msg_parser import *
from exceptions import OperationNotPermitted, ServerException, UidNotFoundException
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
    if(sender is not reciever):
        if(reciever.is_online):
            reciever.socket.send(message.encode('ascii'))
            sender.socket.send(f"{bcolors.OKGREEN}{datetime.now().strftime('%Y-%m-%d %H:%M')}: {reciever.uid} recieved your message{bcolors.ENDC}\n".encode('ascii'))
        else:
            reciever.buffered_messages.append(message)    
            sender.socket.send(f"{bcolors.WARNING}{datetime.now().strftime('%Y-%m-%d %H:%M')}: {reciever.uid} is offline. Last seen at {reciever.last_online.strftime('%Y-%m-%d %H:%M')}{bcolors.ENDC}\n".encode('ascii'))

def group_broadcast(sender: Client, group: Group, message: str):
    if(sender not in group.members):
        raise OperationNotPermitted(f"You are not a member of {group.uid}")
    for i, member in enumerate(group.members):
        send_message(sender, member, message)
    if(i<1):
        sender.socket.send(f"{bcolors.WARNING}You are the only member of {group.uid} {bcolors.ENDC}".encode('ascii'))

def process_message(sender: Client, message: ParsedMsg): 
    reciever_uid = message["args"]["uid"]     
    message_content = message['args']['msg'] 
    
    message_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {sender.uid}@{reciever_uid}: {message_content}\n"  

    if(db.has_client(reciever_uid)):
        reciever: Client = db.get_client(reciever_uid)
        send_message(sender, reciever, message_text)
    elif(db.has_group(reciever_uid)):
        group: Group = db.get_group(reciever_uid)            
        group_broadcast(sender, group, message_text)
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
                    client.socket.send(f"{bcolors.OKGREEN}Group {group_uid} created{bcolors.ENDC}\n".encode('ascii')) 
                
                case Action.GROUP_DELETE:
                    group_uid: str = msg['args']['group_uid']
                    db.delete_group(group_uid, client)
                    client.socket.send(f"{bcolors.OKGREEN}Group {group_uid} deleted{bcolors.ENDC}\n".encode('ascii'))
                
                case Action.GROUP_RENAME:
                    group_uid: str = msg['args']['group_uid']
                    new_uid: str = msg['args']['new_uid']
                    db.rename_group(group_uid, new_uid, client)
                    client.socket.send(f"{bcolors.OKGREEN}Group {group_uid} renamed to {new_uid}{bcolors.ENDC}\n".encode('ascii'))

                case Action.GROUP_ADD_USER:
                    group: Group = db.get_group(msg['args']['group_uid'])
                    client_uids: List[str] = msg['args']['client_uids']                    
                    for uid in client_uids:
                        try:
                            new_member: Client = db.get_client(uid)
                            if(new_member in group.members):
                                client.socket.send(f"{bcolors.WARNING}User {uid} already in {group.uid}{bcolors.ENDC}\n".encode('ascii')) 
                            else:
                                group.add_member(new_member, client)
                                client.socket.send(f"{bcolors.OKGREEN}User {uid} added to {group.uid}{bcolors.ENDC}\n".encode('ascii')) 
                        except UidNotFoundException as e:
                            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}\n".encode('ascii')) 
                            continue                       
                
                case Action.GROUP_REMOVE_USER:
                    group: Group = db.get_group(msg['args']['group_uid'])
                    client_uids: List[str] = msg['args']['client_uids']                    
                    for uid in client_uids:
                        try:
                            to_remove: Client = db.get_client(uid)
                            if(to_remove not in group.members):
                                client.socket.send(f"{bcolors.WARNING}User {uid} is not in {group.uid}{bcolors.ENDC}\n".encode('ascii')) 
                            else:
                                group.remove_member(to_remove, client)
                                client.socket.send(f"{bcolors.OKGREEN}User {uid} removed from {group.uid}{bcolors.ENDC}\n".encode('ascii')) 
                        except UidNotFoundException as e:
                            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}\n".encode('ascii')) 
                            continue
                
        except ServerException as e:
            client.socket.send(f"{bcolors.FAIL}Error{bcolors.ENDC}: {e}\n".encode('ascii'))        
            
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
            client_socket.send(f'Welcome {uid}!\n'.encode('ascii'))       
        else:
            db.get_client(uid).socket = client_socket
            client_socket.send(f'Welcome back {uid}!\n'.encode('ascii'))  
            buffered_messages: List[str] = db.get_client(uid).buffered_messages
            if len(buffered_messages) > 0:
                for msg in buffered_messages.copy():                   
                    client_socket.send(msg.encode('ascii'))   
                    buffered_messages.remove(msg)


        thread = threading.Thread(target=handle, args=(db.get_client(uid),))
        thread.start()

receive()

