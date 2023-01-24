from dblib import db
from uuid import uuid1
from dataclasses import dataclass


@dataclass
class UserSchema():
    email: str
    uname: str
    lname: str | None = None


# Eventually hold uuid: email. username, fname+lname, phone#, school, classes
user_data: db = db("UserData", UserSchema)


def is_email_used(email: str):
    for uuid, user in user_data:
        if user.email == email:
            return True
    return False


def make_user(email: str, username: str) -> str:
    uuid: str = str(uuid1())
    user_data[uuid] = UserSchema(email, username)
    return uuid


def print_users():
    for (uuid, user) in user_data:
        print(f'UUID: {uuid} and USER: {user}')


def valid_keys(fields: list[str]) -> bool:
    return set(fields) <= set(UserSchema.__annotations__.keys())


def valid_fields(vals: dict) -> str:
    """Returns empty string on success, str if failure"""
    if valid_keys(vals.keys()):
        return ''


def get_field(uuid: str, field: str):
    return user_data[uuid, field]


def set_field(uuid: str, field: str, val):
    user_data[uuid, field] = val


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
