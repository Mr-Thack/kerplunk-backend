from common import RES, makeSID
from users import makeUser, isEmailUsed
import cython
import zxcvbn # To check if the password's good
from dblib import db

creds : db = db("Credentials")
# Open a file called Credentials to store hash and salt and username
userCreds : cython.char[64] # Type of data, for Cython

"""
We use username as key for Credentials
bcz sending email over internet bad idea.
But we keep value of the username key as "email salt hash"
"""

def GET(D,R):
    username = D.get('username')
    thash = D.get('hash')
    #t-hash for test, k-hash for known
    if username:
        (email,salt,khash) = str(creds.get(username),'utf-8').split(' ')
        if thash and creds.get(username): #AutoCaching
            if thash==khash:
                return RES(R,{'sid':makeSID(email,D['ip'])})
        else:
            return RES(R,{'salt':salt}) # Get the 1st part
            # TODO: make HTTP errors actually line up with the standard,
            # TODO: give false salt/hash to hackers
    return RES(R,{'error':'Missing username/hash'})

def POST(D,R):
    error = '' # we start with no errors
    email = D.get('email')
    username = D.get('username')
    salt = D.get('salt')
    phash = D.get('hash')
    if not email:
        error='Missing email'
    elif isEmailUsed(email):
        error='Email Already in use'
    elif not salt:
        error='Missing salt'
    elif not phash:
        error='Missing hash'
    elif not username:
        error='Missing username'
    else:
        # If all four (email, username, salt, and hash) and username not registered
        creds.put(username,email + ' ' + salt + ' ' + phash) # Make a new entry
        makeUser(email) # Set up user data
    return RES(R,{'error':error})

Auth = (GET,POST) # See operations.py for more info on how it's organized
