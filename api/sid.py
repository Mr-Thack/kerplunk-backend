from time import time
from secrets import token_urlsafe
# from dblib import db

# This Part is for SIDs
# active: db = db('Sessions', True)  # 1 MB Storage, on RAM
active = {}


# NOTE: I believe we need to start baasing this off of userids
# And that would require some rewriting of the backend
# So, I guess I'll do that after I'm done making it work properly
# in active DB, sid: ip + " " + timeafterepoch (UTC) + ' ' + email
def SIDValidity(sid: str, ip: str):
    r: str = active.get(sid)
    # To check if the timestamp from the last login is still valid (< hour)
    if r:
        # correct ip, time, email
        (cip, ctime, cemail) = r.split(' ')
        if cip == ip and (int(time()) - int(float(ctime))) / 3600 < 60:
            return cemail
        else:
            del active[sid]
            # active.delt(sid)


def makeSID(email, ip):
    """Gens and Gives SID"""
    # I don't think we need to check if SID is good or not
    # Because if a user logs on 2 different devices at once
    sid = token_urlsafe(64)  # 64 is probably unnecessary, but more secure
    # We also track the IP Address, so that user can only login from one place;
    # won't work if a user is on mobile or moving between different networks
    # We want to truncate time, a few microseconds innacuracy won't hurt
    active[sid] = ip + ' ' + str(int(time())) + ' ' + email
    return sid
