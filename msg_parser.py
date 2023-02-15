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
        return {
            "action": Action.MESSAGE, 
            "args": {'uid': recipient_uid, 'msg': split_msg[1]}
            }
    if(str(split_msg[0]) == "group"):
        # to be implemented
        raise ParserException(f"Groups feature not implemented yet")
    raise ParserException(f"Unknown command: {split_msg[0]}")
