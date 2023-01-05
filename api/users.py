from dblib import db

# Eventually hold email: username, fname+lname, phone#, school, classes
user_data: db = db("UserData")
# UserName, LegalName
# Don't forget to change range to adjust for new length
datanames = ('uname', 'lname')
datas = dict(zip(datanames, range(len(datanames))))
# We don't use an enum because the data is coming from users
# And eval() could be used, but that'scould be a major vulnerability
datanames = set(datanames)  # This will help with performance later


# Split by spaces
def is_email_used(email: str):
    return user_data.get(email)


def make_user(email: str, username: str):
    user_data.put(email, username + ' ')
    # For each field supported, a space, then -1


def valid_fields(fields: list[str]) -> bool:
    return set(fields) <= datanames


def get_field(email: str, field: str):
    r = user_data.sget(email).split(' ')[datas[field]]
    if field == datas['lname']:
        r = r.replace('_', ' ')
    return r


def set_field(email: str, field: str, val):
    fields_all: list[str] = user_data.sget(email).split(' ')
    fields_all[datas[field]] = val  # datas is a dict that we'll use for enums
    # Set up new str
    nf: str = ' '.join(fields_all)
    return user_data.put(email, nf)


def multi_get(email: str, fs: list[str]) -> dict:  # Takes fields as "fs"
    r = {}
    for f in fs:
        r[f] = get_field(email, f)
    return r


def multi_set(email: str, fs: dict) -> str:
    r = []
    for k, v in fs.items():
        set_field(email, k, v)
        r.append(k)
    return ' '.join(r)
