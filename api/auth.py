from pydantic import BaseModel
from bcrypt import hashpw
from sid import makeSID
from users import make_user, is_email_used
from dblib import db
from dataclasses import dataclass


@dataclass
class CredsSchema():
    uuid: str
    email: str


creds = db('Credentials', CredsSchema)
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

HASH_SALT = b'$2b$12$lDGmZwBbuqU9DYMFxGRWRe'


# We want a username and a hash of their pwd and email on signup
class SignUpData(BaseModel):
    uname: str
    pwd: str
    email: str


def get_user(ahash: str) -> list[str, str]:
    data = creds[ahash]
    print(creds)
    if data:
        return data


def gen_hash(pwd: str) -> str:
    return hashpw(pwd.encode('utf-8'), HASH_SALT).decode('utf-8')


def login_user(email: str, pwd: str, ip: str):
    ahash: str = gen_hash(email + pwd)
    user: CredsSchema = get_user(ahash)
    if user and user.email == email:
        # This won't work when running behind a proxy
        return makeSID(user.uuid, ip)
        # req.client = (client_ip_addr, client_port)


async def signup_user(data: SignUpData):
    if not is_email_used(data.email):
        # We combine the email and password
        # incase the email or username are the same
        ahash: str = gen_hash(data.email + data.pwd)
        uuid = make_user(data.email, data.uname)
        creds[ahash] = CredsSchema(uuid, data.email)
        return True
