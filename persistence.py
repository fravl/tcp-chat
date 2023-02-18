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

    def add_member(self, member: Client, client: Client):
        if(client is not self.owner):
            raise UnauthorizedAccessException(f"{client.uid} is not authorized to modify group {self.uid}")
        if(member not in self.members):
            self.members.append(member)
    
    def remove_member(self, member: Client, client: Client):
        if(client is not self.owner):
            raise UnauthorizedAccessException(f"{client.uid} is not authorized to modify group {self.uid}")
        if(member in self.members):
            self.members.remove(member)

class Persistence():
    __clients = {}
    __groups = {}

    def __init__(self) -> None:
        pass

    def create_client(self, uid: str, client_socket: socket) -> Client:
        if uid in self.__clients.keys():
            raise DuplicateUidException(f"User name {uid} already exists")
        self.__clients.update({uid: Client(uid, client_socket)})
        return self.__clients.get(uid)

    def get_client(self, uid: str) -> Client:
        if uid not in self.__clients.keys():
            raise UidNotFoundException(f"User {uid} cannot be found")
        return self.__clients.get(uid)

    def has_client(self, uid: str) -> bool:
        return uid in self.__clients.keys()

    def create_group(self, uid: str, owner: Client) -> Group:
        if uid in self.__groups.keys():
            raise DuplicateUidException(f"Group name {uid} already exists")
        self.__groups.update({uid: Group(uid, owner)})
        return self.__groups.get(uid)

    def get_group(self, uid: str):
        if uid not in self.__groups.keys():
            raise UidNotFoundException(f"Group {uid} cannot be found")
        return self.__groups.get(uid)

    def delete_group(self, uid: str, client: Client):
        _group: Group = self.get_group(uid)
        if(self.__can_modify(client, _group)):
            self.__groups.pop(uid)

    def has_group(self, uid: str):
        return uid in self.__groups.keys()

    def rename_group(self, old_uid: str, new_uid: str, client: Client):
        _group: Group = self.get_group(old_uid)
        if(self.__can_modify(client, _group)):            
            if(new_uid in self.__groups.keys()):
                raise DuplicateUidException(f"Group {new_uid} already exists")
            _group.uid = new_uid            
            self.__groups.update({new_uid: _group})
            self.__groups.pop(old_uid)
            
            

    def __can_modify(self, client: Client, group: Group) -> bool:
        if group.owner.uid is not client.uid:
            raise UnauthorizedAccessException(f"{client.uid} is is not authorized to modify group {group.uid}")
        return True



    