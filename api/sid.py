from time import time
from secrets import token_urlsafe
from dblib import db
from dataclasses import dataclass


@dataclass
class SessionsSchema():
    ip: str
    time: int
    uuid: str

# This Part is for SIDs


active = db('Sessions', SessionsSchema, tmp=True)  # 1 MB Storage, on RAM


# NOTE: I believe we need to start baasing this off of userids
# And that would require some rewriting of the backend
# So, I guess I'll do that after I'm done making it work properly
# in active DB, sid: ip + " " + timeafterepoch (UTC) + ' ' + email


def SIDValidity(sid: str, ip: str):
    """Check validity of token/SID, returns UUID, None on failure"""
    r = active[sid]
    # To check if the timestamp from the last login is still valid (< hour)
    if r:
        # correct ip, time, uuid
        # Now that we use tokens, we could get rid of the ip check
        # Though it's just an extra layer of security
        if r.ip == ip and (int(time()) - r.time) / 3600 < 60:
            return r.uuid
        else:
            del active[sid]
            # active.delt(sid)


def makeSID(uuid: str, ip: str):
    """Gens and Gives SID"""
    # I don't think we need to check if SID is good or not
    # Because if a user logs on 2 different devices at once
    sid = token_urlsafe(64)  # 64 is probably unnecessary, but more secure
    # We also track the IP Address, so that user can only login from one place;
    # won't work if a user is on mobile or moving between different networks
    # We want to truncate time, a few microseconds innacuracy won't hurt
    active[sid] = SessionsSchema(ip, int(time()), uuid)
    return sid
