from fastapi import HTTPException
from users import get_field
from pydantic import BaseModel
from secrets import token_urlsafe


class InitChatRoomData(BaseModel):
    name: str
    pwd: str | None = None
    public: bool
    temp: bool


class ChatRoom(InitChatRoomData):
    owner: str
    cid: str
    joiners: list[str] = []


chats: dict[str, ChatRoom] = {}


def is_chat_name_taken(name: str):
    return True if name in [chat.name for chat in chats] else False


def list_chats() -> str:
    return ' '.join(chats.keys())


def create_chatroom(data: InitChatRoomData, owner: str):
    if data.name in chats:
        raise HTTPException(status_code=403, detail='Name already in use')
    new_chatrm = ChatRoom(cid=token_urlsafe(32),
                          owner=get_field(owner, 'uname'), **data.__dict__)
    chats[new_chatrm.name] = new_chatrm  # Works for now, later get use the db
    if True:
        return new_chatrm.cid
    else:
        raise HTTPException(status_code=401, detail='Get assistance!')


def add_user_to_chatroom(email: str, name: str, pwd: str | None):
    chatrm = chats.get(name)
    if not chatrm or (chatrm.pwd and chatrm.pwd != pwd):
        raise HTTPException(status_code=403, detail='Invalid name or pwd')
    chatrm.joiners.append(get_field(email, 'uname'))
    return {
            'cid': chatrm.cid,
            'owner': chatrm.owner,
            'joiners': chatrm.joiners
            }
