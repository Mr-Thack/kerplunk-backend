import ujson as js
from dblib import db
import secrets
import time

### This Part is for SIDs ###
#active : db = db('Sessions',True) # 1 MB Storage, on RAM
active = {}

# in active DB, sid: ip + " " + timeafterepoch (UTC) + ' ' + email
def SIDValidity(sid, ip):
    #r = active.sget(sid)
    r= active.get(sid)
    #active.display()
    # To check if the timestamp from the last login is still valid (Less than an hour)
    if r:
        r=r.split(' ')
        if r[0] == ip and (int(time.time()) - int(float(r[1]))) / 3600 < 60:
            return r[2]
        else:
            #active.delt(sid)
            del active[sid]

def makeSID(email,ip):
    """Gens and Gives SID"""
    # I don't think we need to check if SID is good or not
    # Because if a user logs  on 2 diff devices at once
    sid = secrets.token_urlsafe(32)
    # We also track the IP Address,
    # won't work if a user is on mobile/moving between a bunch of different networks
    #active.put(sid,ip + " " + str(int(time.time())) + " " + email) # We want to truncate time
    active[sid] = ip + ' ' + str(int(time.time())) + ' ' + email
    return sid

### This Part Is Just For Responding ###
def NYI(D,R): #NYI: Not Yet Implemented, or also, Doesn't Exist
    # We just return 403 (I think it's the rigth err code)
    R('403', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200'): # A nice wrapper for easy respond
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return [js.dumps(D).encode('utf-8')] # Return this to HTTP Server
