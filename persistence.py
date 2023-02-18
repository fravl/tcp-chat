import socket
from datetime import datetime
from typing import List
from exceptions import UidNotFoundException, DuplicateUidException, UnauthorizedAccessException

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

__clients = {}
__groups = {}

def create_client(uid: str, client_socket: socket) -> Client:
    if uid in __clients.keys():
        raise DuplicateUidException(f"User name {uid} already exists")
    __clients.update({uid: Client(uid, client_socket)})
    return __clients.get(uid)

def get_client(uid: str) -> Client:
    if uid not in __clients.keys():
        raise UidNotFoundException(f"User {uid} cannot be found")
    return __clients.get(uid)

def has_client(uid: str) -> bool:
    return uid in __clients.keys()

def create_group(uid: str, owner: Client) -> Group:
    if uid in __groups.keys():
        raise DuplicateUidException(f"Group name {uid} already exists")
    __groups.update({uid: Group(uid, owner)})
    return __groups.get(uid)

def get_group(uid: str):
    if uid not in __groups.keys():
        raise UidNotFoundException(f"Group {uid} cannot be found")
    __groups.get(uid)

def delete_group(uid: str, client: Client):
    _group: Group = get_group(uid)
    if(__can_modify(client, _group)):
        __groups.pop(uid)

def has_group(uid: str):
    return uid in __groups.keys()

def update_Group(group: Group, client: Client):
    _group: Group = get_group(group.uid)
    if(__can_modify(client, _group)):
        __groups.update({group.uid: group})

def __can_modify(client: Client, group: Group) -> bool:
    if group.owner.uid is not client.uid:
        raise UnauthorizedAccessException(f"{client.uid} is not owner of group {group.uid}")
    return True



    