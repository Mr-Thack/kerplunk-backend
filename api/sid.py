from time import time
from secrets import token_urlsafe
from fastapi import HTTPException
# from dblib import db

# This Part is for SIDs
# active: db = db('Sessions', True)  # 1 MB Storage, on RAM
active = {}


# NOTE: I believe we need to start baasing this off of userids
# And that would require some rewriting of the backend
# So, I guess I'll do that after I'm done making it work properly
# in active DB, sid: ip + " " + timeafterepoch (UTC) + ' ' + email


def SIDValidity(sid: str, ip: str):
    """Check validity of token/SID, returns UUID, HTTPException on failure"""
    r: str = active.get(sid)
    # To check if the timestamp from the last login is still valid (< hour)
    if r:
        # correct ip, time, uuid
        # Now that we use tokens, we could get rid of the ip check
        # Though it's just an extra layer of security
        (cip, ctime, cuuid) = r.split(' ')
        if cip == ip and (int(time()) - int(float(ctime))) / 3600 < 60:
            return cuuid
        else:
            del active[sid]
            # active.delt(sid)
    raise HTTPException(status_code=403, detail='SID Expired/Invalid (Login!)')


def makeSID(uuid: str, ip: str):
    """Gens and Gives SID"""
    # I don't think we need to check if SID is good or not
    # Because if a user logs on 2 different devices at once
    sid = token_urlsafe(64)  # 64 is probably unnecessary, but more secure
    # We also track the IP Address, so that user can only login from one place;
    # won't work if a user is on mobile or moving between different networks
    # We want to truncate time, a few microseconds innacuracy won't hurt
    active[sid] = ip + ' ' + str(int(time())) + ' ' + uuid
    return sid
