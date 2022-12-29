import ujson as js
from dblib import db
import secrets
import time

### This Part is for SIDs ###
#active : db = db('Sessions',True) # 1 MB Storage, on RAM
active = {}

# NOTE: I believe we need to start baasing this off of userids
# And that would require some rewriting of the backend
# So, I guess I'll do that after I'm done making it work properly
# in active DB, sid: ip + " " + timeafterepoch (UTC) + ' ' + email
def SIDValidity(sid:str, ip:str):
    r : str = active.get(sid)
    # To check if the timestamp from the last login is still valid (Less than an hour)
    if r:
        r : (str,str,str) = r.split(' ')
        if r[0] == ip and (int(time.time()) - int(float(r[1]))) / 3600 < 60:
            return r[2]
        else:
            active.delt(sid)

def makeSID(email,ip):
    """Gens and Gives SID"""
    # I don't think we need to check if SID is good or not
    # Because if a user logs on 2 different devices at once
    sid = secrets.token_urlsafe(32)
    # We also track the IP Address,
    # won't work if a user is on mobile/moving between a bunch of different networks
    # We want to truncate time
    active[sid] = ip + ' ' + str(int(time.time())) + ' ' + email
    return sid

### This Part Is Just For Responding ###
def NYI(_): #NYI: Not Yet Implemented, or also, Doesn't Exist
    # We just return 403 (I think it's the rigth err code)
    R('403', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200'): # A nice wrapper for easy respond
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return [js.dumps(D).encode('utf-8')] # Return this to HTTP Server







