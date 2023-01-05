from dblib import db, BaseSchema
from uuid import uuid1
from fastapi import HTTPException
from dataclasses import dataclass


@dataclass
class UserSchema(BaseSchema):
    email: str
    uname: str
    lname: str | None = None


# Eventually hold email: username, fname+lname, phone#, school, classes
user_data: db = db("UserData", UserSchema)


def is_email_used(email: str):
    # Oh woopsie, this'll be hard to fix
    # return user_data.sget(email)
    return False


def make_user(email: str, username: str) -> str:
    uuid: str = str(uuid1())
    user_data[uuid] = UserSchema(email, username)
    return uuid


def valid_fields(fields: list[str]) -> bool:
    return set(fields) <= set(UserSchema.__annotations__.keys())


def get_field(uuid: str, field: str):
    # We could add some sort of data validation/parsing here
    r = user_data[uuid, field]
    return r


def set_field(uuid: str, field: str, val):
    if field == 'lname' and field.find(' ') != -1:
        raise HTTPException(status_code=401,
                            detail='No space characters allowed!')
    user_data[uuid, field] = val
    return True


def multi_get(uuid: str, fs: list[str]) -> dict:  # Takes fields as "fs"
    r = {}
    for f in fs:
        r[f] = get_field(uuid, f)
    return r


def multi_set(uuid: str, fs: dict) -> str:
    r = []
    for k, v in fs.items():
        set_field(uuid, k, v)
        r.append(k)
    return ' '.join(r)
