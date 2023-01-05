from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from bcrypt import hashpw
from sid import makeSID
from users import make_user, is_email_used
from dblib import db

creds: db = db('Credentials')
"""
creds only holds enough information for authentication.
Actual user data is stored elsewhere
Data is stored as:
ahash: uuid1 + ' ' + uname
The ahash is used after the pwd is hashed.
uuid1 is used internally as the user's id
the uname is used so that on login we can check if the uname provided is right
It should be noted that UUID1 has one problem. It uses our MAC address.
This could become a privacy concern if we get hacked. However,
I'm using UUID1 because UUID1 also provides a timestamp, which we can later use
in order to retrieve when the user signed up. So basically, if we're already
storing stuff, why don't we just kill 2 birds with 1 stone?
"""

AUTH_EXCEPTION = HTTPException(status_code=401,
                               detail='Incorrect username or password')
HASH_SALT = b'$2b$12$lDGmZwBbuqU9DYMFxGRWRe'


# We want a username and a hash of their pwd and email on signup
class SignUpData(BaseModel):
    uname: str
    pwd: str
    email: str


def get_user(ahash: str) -> list[str, str]:
    data = creds.sget(ahash)
    if data:
        return data.split(' ')
    raise AUTH_EXCEPTION


def gen_hash(pwd: str) -> str:
    return hashpw(pwd.encode('utf-8'), HASH_SALT).decode('utf-8')


async def login_user(req: Request, fd: OAuth2PasswordRequestForm = Depends()):
    ahash: str = gen_hash(fd.password)
    user = get_user(ahash)
    if user and user[1] == fd.username:
        # This won't work when running behind a proxy
        return makeSID(user[0], req.client.host)
        # req.client = (client_ip_addr, client_port)
    raise AUTH_EXCEPTION


async def signup_user(data: SignUpData):
    if is_email_used(data.email):
        raise HTTPException(status_code=400, detail='Email already in use!')
    ahash: str = gen_hash(data.pwd)
    # Change it so that it uses a userid
    uuid = make_user(data.email, data.uname)
    creds.put(ahash, uuid + ' ' + data.uname)
    return True
