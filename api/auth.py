from common import NYI
from common import RES
import cython
import zxcvbn
from dblib import LMDB

userDB : LMDB = LMDB("Credentials")
userCreds : cython.char[64]

# In DB, the credentials are stored (salt,hash)
# thus accessed with creds[0] and creds[1]

def GET(D,R):
    rz : bool = False
    if 'hash' in D and 'username' in D:
        print(D['username'] + ' is trying to log in')
        userCreds = userDB.jget(D['username'])
        if userCreds != None:
            rz = D['hash'].decode() == userCreds[1].decode()
        return RES(R,{'rz':rz})
    elif 'username' in D:
        rs = userDB.jget(D['username'][0])
        if not rs == None:
            return RES(R,{'salt':rs[0]})
        else:
            #TODO: give false hash to trick a hacker into thinking he got someone
            return RES(R,{'rz':rz},'401')
    return RES(R,{'rz':rz},'401')
    # If we're still stuck here, that means we failed, so we return 401

def POST(D,R):
    rz : bool = False
    if 'username' in D and not userDB.get(D['username']):
        userDB.jput(D['username'],( D['salt'], D['hash']) )
        print('Signed up user ' + D['username'])
        rz = True
    return RES(R,{'rz':rz})

Auth = (GET,POST)
