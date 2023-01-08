from users import get_field
from pydantic import BaseModel
from secrets import token_urlsafe
from dblib import db
from socket_manager import SocketManager


class InitChatRoomData(BaseModel):
    name: str
    pwd: str | None = None
    public: bool
    temp: bool


class ChatRoom(InitChatRoomData):
    owner: str  # This is a UUID str
    cid: str
    joiners: list[str] = []


"""
In the chatroom environement, we'll have a subdatabase for each chat.
This one will hold the info on all the chatrooms, but not the actualy texts,
because the info will be accessed constantly, whereas the texts aren't.
So, only when required we'll open up the subdb holding the texts.
For simplicity, we'll just call the subdb for each chat by it's chat id (cid)
"""
chats = db('ChatRoomsInfo', ChatRoom, chat=True)
opened_chats: dict = {}
sm = SocketManager()


def is_chat_name_taken(name: str):
    return True if name in [chat.name for chat in chats] else False


def list_chats() -> str:
    """List all chats by their display name"""
    # Doing "for cid_chat in chats" returns (cid, chat) as a cid_chat: tuple
    return ' '.join([cid_chat[1].name for cid_chat in chats])


def open_chat(cid: str):
    if cid not in opened_chats.keys():
        opened_chats[cid] = db(cid, None, chat=True)
    return opened_chats[cid]


def create_chatroom(data: InitChatRoomData, owner: str):
    # We take owner as a UUID str
    if not is_chat_name_taken(data.name):
        cid = token_urlsafe(32)
        new_chatrm = ChatRoom(cid=cid,
                              owner=owner, **data.__dict__)
        chats[new_chatrm.cid] = new_chatrm  # Write info to the db
        chat_data = open_chat(cid)  # Open a fresh new one
        chat_data[0] = (f"User {get_field(owner, 'uname')}" +
                        f" has created chatroom {new_chatrm.name}!")
        return new_chatrm.cid


def add_user_to_chatroom(uuid: str, name: str, pwd: str | None) -> dict | None:
    chatrm = None
    for cid, chat in chats:
        if chat.name == name:
            chatrm = chat
    if chatrm and (not chatrm.pwd or (pwd and chatrm.pwd == pwd)):
        chatrm.joiners.append(uuid)
        chats[chatrm.cid] = chatrm
        return {
            'cid': chatrm.cid,
            'owner': get_field(chatrm.owner, 'uname'),
            'joiners': [get_field(j, 'uname') for j in chatrm.joiners]
            }


def usr_in_chatroom(uuid: str, cid: str):
    """Check if user is in given chatroom"""
    chat = chats[cid]
    return True if uuid in chat.joiners else False


# We'll take the user's uuid, the msg, and chatroom
def write_msg(cid: str, msg: str):
    # TODO: Check for problems in txt msg or smth
    chat = open_chat(cid)
    chat[len(chat)] = msg
    # Since indices start at 0, len() will return 1 + the last index
    return True


def read_msgs(cid: str, msg_start: int, msg_end: int):
    if not (isinstance(msg_start, int) and isinstance(msg_end, int)):
        raise IndexError
    chat = open_chat(cid)
    if msg_end == -1:
        msg_end = len(chat)
    return [chat[i] for i in range(msg_start, msg_end)]


async def on_user_join_chatroom(cid: str, uuid: str, ws):
    await sm.connect(ws, uuid)
    write_msg(cid, f"User {get_field(uuid, 'uname')} has joined the chat!")
    await sm.dm(uuid, '\x1e'.join(read_msgs(cid, 0, -1)))  # -1 means "end"
    # This weird character is ASCII 30 (Record Seperator)


async def join_chatroom_user_event_loop(uuid: str, cid: str):
    msg = await sm.recv(uuid)
    await sm.dm(uuid, f'You sent "{msg}"')
    write_msg(cid, msg)
    await sm.broadcast(msg)


async def on_user_leave_chatroom(uuid: str, cid: str):
    msg = f"User {get_field(uuid, 'uname')} has left the chat!"
    write_msg(cid, msg)
    sm.disconnect(uuid)  # Remove inactive user
    await sm.broadcast(msg)  # Then send to all that're left
