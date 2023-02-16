from enum import Enum
from typing import TypedDict, List

class Action(Enum):
    MESSAGE = "message"
    GROUP_CREATE = "group_create"
    GROUP_DELETE = "group_delete"
    GROUP_ADD_USER = "group_add_user"
    GROUP_REMOVE_USER = "group_remove_user"


class ParsedMsg(TypedDict):
    action: Action
    args: dict

class ParserException(Exception):
    pass

def parse(msg: str) -> ParsedMsg:
    split_msg = msg.split(None, 1)
    if(str(split_msg[0]).startswith("@")):
        recipient_uid = split_msg[0][1:]
        if(len(split_msg)>1):
            content = split_msg[1]
        else:
            content = ""
        return {
            "action": Action.MESSAGE, 
            "args": {'uid': recipient_uid, 'msg': content}
            }
    if(str(split_msg[0]) == "group"):
        split_msg = msg.split(" ")
        if(len(split_msg) <= 2):
            raise ParserException(f"Unkown command {msg}")

        if(split_msg[2] == "create"):
            return {
                "action": Action.GROUP_CREATE,
                "args": {"group_uid": split_msg[1]}
            }
        if(split_msg[2] == "delete"):
            return {
                "action": Action.GROUP_DELETE,
                "args": {"group_uid": split_msg[1]}
            }
        if(split_msg[2] == "add" or split_msg[2] == "remove"):
            if(len(split_msg) <=3):
                raise ParserException(f"Missing user in command {msg}")
            uids = []  
            for user_uid in split_msg[3:]:
                uids.append(user_uid)
            
            if(split_msg[2] == "add"):
                return {
                    "action": Action.GROUP_ADD_USER,
                    "args": {
                        "group_uid": split_msg[1],
                        "user_uids": uids
                    }
                }
            else:
                return {
                    "action": Action.GROUP_REMOVE_USER,
                    "args": {
                        "group_uid": split_msg[1],
                        "user_uids": uids
                    }
                }      

    raise ParserException(f"Unknown command: {msg}")
