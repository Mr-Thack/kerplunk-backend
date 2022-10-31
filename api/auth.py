from common import NYI
import cython
import zxcvbn
import ujson as js
from dblib import LMDB

userDB : LMDB = LMDB("Credentials")
userCreds : cython.char[64]

def GET(D,R):
    rz : bool = False

    if isinstance(body['hash'],str):
        if isinstance(body['username'],str):
            print(body['username'] + ' is trying to log in')
            userCreds = userDB.get(body['username'])
            if not isinstance(userCreds,None):
                rz = body['hash'].decode() == js.loads(userCreds)['hash'].decode()
        R('200 OK',[('Content-Type','text/plain;character=utf-8')])
        return js.dumps({'rz':rz})
    else:
        return js.dumps({'salt':js.loads(userDB.get(body['username']))['salt']})

def POST(D,R):
    rz : bool = False
    if not userDB.get(D['username']):
        userDB.put(D['username'],js.dumps({ D['salt'] : D['hash'] }))
        print('Signed up user ' + D['username'])
        rz = True
    R('200 OK',[('Content-Type','text/plain;charset=utf-8')])
    return js.dumps({'rz':rz})

Auth = (GET,POST)
