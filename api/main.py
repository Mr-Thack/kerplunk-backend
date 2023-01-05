from fastapi import FastAPI, Depends, Request, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth import login_user, signup_user
from users import multi_get, multi_set, valid_fields
from chats import (list_chats, create_chatroom, InitChatRoomData,
                   add_user_to_chatroom)
from sid import SIDValidity


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_uuid(req: Request, sid: str = Depends(oauth2_scheme)):
    uuid = SIDValidity(sid, req.client.host)
    if uuid:
        return uuid
    else:
        raise HTTPException(status_code=401, detail='SID/Token Invalid')


@app.post('/signup')
async def signup(success: bool = Depends(signup_user)):
    if success:
        return success
    else:
        raise HTTPException(status_code=400,
                            detail='Dunno, some sort of error')


@app.post('/login')
async def login(token: str = Depends(login_user)):
    return {'access_token': token, 'token_type': 'bearer'}


@app.get('/userme')
async def user_get_field(fields: list[str] = Query(),
                         uuid: str = Depends(get_uuid)):
    if valid_fields(fields):
        return multi_get(uuid, fields)
    raise HTTPException(status_code=400, detail='Invalid Fields')


@app.post('/userme')
async def user_set_field(fields: dict, uuid: str = Depends(get_uuid)):
    if valid_fields(fields.keys()):
        return {'changed': multi_set(uuid, fields)}
    raise HTTPException(status_code=400, detail='Invalid Fields')


@app.get('/chats')
async def ret_list_chats():
    return {'chatrooms': list_chats()}


@app.post('/chats')
async def open_chatroom(room_data: InitChatRoomData,
                        uuid: str = Depends(get_uuid)):
    return {'cid': create_chatroom(room_data, uuid)}


@app.patch('/chats')
async def user_join_chatroom(name: str, pwd: str | None = None,
                             uuid: str = Depends(get_uuid)):
    return add_user_to_chatroom(uuid, name, pwd)
