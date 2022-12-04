import ujson as js
from dblib import db
import secrets
import time

### This Part is for SIDs ###
active : db = db("/tmp/Sessions",10<<20) # 1 MB Storage, on RAM

# in active DB, username: sid + " " + timeafterepoch (UTC)
def SIDValidity(username, ip):
    r = active.sget(username)
    # To check if the timestamp from the last login is still valid (Less than an hour)
    if r:
        r=r.split(' ')
        if r[0] == ip and (int(time.time()) - int(r[1])) / 3600 < 60:
            return True
        else:
            active.delt(username)
    return False

def giveSID(username,ip):
    # I don't think we need to check if SID is good or not
    # Because if a user logs  on 2 diff devices at once
    sid = secrets.token_urlsafe(32)
    # We also track the IP Address,
    # won't work if a user is on mobile/moving between a bunch of different networks
    active.put(username,ip + " " + sid)
    return sid

### This Part is For Users ###
# Eventually hold email:username,fname+lname,phone#,school,classes
userData : db = db("UserData")
(USERNAME,NAME) = range(2)
# Split by spaces

def makeUser(email):
    userData.put(email,' ')
    # For each field supported, a space, then -1

def getField(email,field):
    userData.sget(email,field)

def setField(email,field,val):
    fa = userData.sget(email).split(' ')
    fa[field] = val
    nf:str
    for f in fa:
        nf += ' ' + f
    userData.put(email,nf[1:])

def setUsername(email,username):
    setField(email,USERNAME,username)

def setName(email,fName,lName):
    setField(email,NAME,fName+","+lName)

def getUsername(email):
    getField(email,USERNAME)

def getName(email):
    e = getField(email,NAME)
    if e:
        return e.split(",")
    #This works bcz the default return value is None


### This Part Is Just For Responding ###
def NYI(D,R): #NYI: Not Yet Implemented, or also, Doesn't Exist
    # We just return 403 (I think it's the rigth err code)
    R('403', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200'): # A nice wrapper for easy respond
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return js.dumps(D) # Return this to HTTP Server
