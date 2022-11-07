from common import NYI
from common import RES, get
import cython
import zxcvbn
from dblib import LMDB

userDB : LMDB = LMDB("Credentials")
userCreds : cython.char[64]

# In DB, the credentials are stored (salt,hash)
# thus accessed with creds[0] and creds[1]

def GET(D,R):
    rz : bool = False
    username = get(D,'username')
    phash = get(D,'hash')
    if phash and username:
        userCreds = userDB.get(username)
        if userCreds != None:
            rz = bytes(phash,'utf-8') == userCreds[1]
        return RES(R,{'rz':rz})
    elif username:
        rs = userDB.sget(username) #stored as 'salt hash'
        if not rs == None:
            return RES(R,{'salt':rs.split(' ')[0]})
        else:
            #TODO: give false salt to trick a hacker into thinking he got someone
            return RES(R,{'rz':rz},'402')
    return RES(R,{'rz':rz},'401')
    # If we're still stuck here, that means we failed, so we return 401

def POST(D,R):
    rz : bool = False
    username = get(D,'username')
    salt = get(D,'salt')
    phash = get(D,'hash')
    if username and salt and phash and not userDB.get(username):
        userDB.put(username,salt + ' ' + phash )
        rz = True
    return RES(R,{'rz':rz})

Auth = (GET,POST)
