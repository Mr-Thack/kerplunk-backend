from dblib import db
from uuid import uuid1
from fastapi import HTTPException
# Eventually hold email: username, fname+lname, phone#, school, classes
user_data: db = db("UserData")
# UserName, LegalName
# Don't forget to change range to adjust for new length
datanames = ('uname', 'lname', 'email')
datas = dict(zip(datanames, range(len(datanames))))
# We don't use an enum because the data is coming from users
# And eval() could be used, but that'scould be a major vulnerability
datanames = set(datanames)  # This will help with performance later
# because we will be calling datas instead of datanames


# Split by spaces
def is_email_used(email: str):
    # Oh woopsie, this'll be hard to fix
    # return user_data.sget(email)
    return False


def make_user(email: str, username: str) -> str:
    uuid: str = str(uuid1())
    user_data.put(uuid, ' '.join((username, email)))
    return uuid


def valid_fields(fields: list[str]) -> bool:
    return set(fields) <= datanames


def get_field(uuid: str, field: str):
    r = user_data.sget(uuid).split(' ')[datas[field]]
    if field == datas['lname']:
        r = r.replace('_', ' ')
        # Probably should error out instead
    return r


def set_field(uuid: str, field: str, val):
    if field == 'lname' and field.find(' ') != -1:
        raise HTTPException(status_code=401,
                            detail='No space characters allowed!')
    fields_all: list[str] = user_data.sget(uuid).split(' ')
    fields_all[datas[field]] = val  # datas is a dict that we'll use for enums
    # Set up new str
    nf: str = ' '.join(fields_all)
    return user_data.put(uuid, nf)


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
