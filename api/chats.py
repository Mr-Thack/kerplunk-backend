from common import RES, NYI, SIDValidity 
from user_operations import get_field,datas
from dblib import chatenv,db
from socket import socket, SOL_SOCKET as SS, SO_REUSEADDR as SRA
#indices = chatenv

class ChatRoom():
    def __init__(self,owner:str,name:str,pwd:str,public:bool,temp:bool,port:int=None):
        self.owner = owner
        self.name = name
        self.pwd = pwd or '' 
        # We can't write None to the database
        # So, instead we'll write None
        # I miss the Rust way to do this
        self.public = public
        self.temp = temp
        self.port = port
        self.joiners : [str] = []
        # This is a string of userids or emails or something of each user that joined
chats : [ChatRoom] = [] 

def is_chat_name_taken(name : str):
    return True if name in [chat.name for chat in chats] else False

def GET(D,R):
    return RES(R,{'chats':' '.join(chat.name for chat in chats)}) 

def POST(D,R):
    sid : str = D.get('sid')
    pwd : str = D.get('pwd')
    email : str
    if sid:
        email = SIDValidity(sid,D['ip'])
    else:
        return RES(R,{'error':'Field sid missing'})
    name : str = D.get('name')
    public : bool = D.get('public')
    temp : bool = D.get('temp')
    if not name:
        return RES(R,{'error':'Fields name & public required!'})
    elif is_chat_name_taken(name):
        return RES(R,{'error':'Name Taken!'})
    elif len(chats) <= 100:
        # We want to start assigning public chat ports from port 6000
        # Probably should globalize it as a constant
        port : int = len(chats)+6000 if temp else 0
        new_chat_room = ChatRoom(get_field(email,'uname'),name,pwd,public,temp,port)
        if ( not chats.append(new_chat_room)): 
            # We will have to change this later to also check for failures
            return RES(R,{'error':'','port':new_chat_room.port})
        else:
            return RES(R,{'error':'Failed to Initialize New Chat Room'})
    else:
        return RES(R,{'error':'Too many chat rooms opened! (The total amount from all users)'})


msg = "Chat's name is mispelled"
"""This message will be given when the searched room name is invalid,
doesn't exist, or a "hacker" tries to guess a private room's password
This way the "hacker" doesn't know if the room even exists"""

def PUT(D,R):
    sid : str = D.get('sid')
    name : str = D.get('name')
    pwd : str = D.get('pwd')
    if sid:
        email = SIDValidity(sid,D['ip'])
        if email:
            indx : int = [chat.name for chat in chats].index(name)
            if indx == -1:
                return RES(R,{'error',msg}) #msg is from above this func declaration
            else:
                chat = chats[indx]
                if (pwd or '') == chat.pwd:
                    # Join new user then send data
                    chat.joiners.append(get_field(email,'uname'))
                    return RES(R,{
                        'error':'',
                        'port':chat.port,
                        'owner':chat.owner,
                        'joiners':chat.joiners
                    })
                elif chat.public:
                    return RES(R,{'error','Invalid Password!'})
                else:
                    return RES(R,{'error',msg})
        else:
            return RES(R,{'error':'SID Invalid'})
    else:
        return RES(R,{'error':'SID Missing'})
   

ChatRooms = (GET,POST,PUT,NYI)
