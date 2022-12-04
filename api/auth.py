from common import RES, giveSID, makeUser
import cython
import zxcvbn # To check if the password's good
from dblib import db

userDB : db = db("Credentials")
# Open a file called Credentials to store hash and salt and username
userCreds : cython.char[64] # Type of data, for Cython

# In DB, the credentials are stored username: salt + " " + hash
# thus accessed with creds[0] and creds[1] when split(" ")

def GET(D,R): # D for Data, R for Respond
    rz : bool = False # rezult
    email = D.get('email') # Get username from Data object
    phash = D.get('hash') # Get Hash from Data Object
    if phash and email:
        userCreds = userDB.sget(email) # Ask database for username
        sid = ''
        if userCreds and phash == userCreds.split(' ')[1]:
            sid = giveSID(email,D['ip'])
        # TODO: Give false sid to make hacker think they're smart
        return RES(R,{'rz':rz,'sid':sid})
    elif email: # If only the username was given
        rs = userDB.sget(email) # Get data from username
        # It's stored as 'salt hash', with a space in between
        if not rs == None: # If not nothing found, aka we have result
            return RES(R,{'salt':rs.split(' ')[0]}) # Get the 1st part
        else:
            #TODO: give false salt to trick a hacker into thinking he got someone
            return RES(R,{'rz':rz},'402') # return error
        # TODO: make HTTP errors actually line up with the standard,
        # but it doesn't matter if we don't, bc it won't affect functionality
        # it only affects our adherence to standards
    return RES(R,{'error':'Missing email'},'401')
    # If we're still stuck here, that means we failed, so we return 401

def POST(D,R):
    error = '' # we start with no errors
    email = D.get('email')
    username = D.get('username') # Get username from given Data
    salt = D.get('salt') # Get salt from given data
    phash = D.get('hash') # Get hash from given data
    if not email:
        error='Missing email'
    elif userDB.get(email) or email=='LastTimeChecked':
        #LastTimeChecked is used for the SIDs
        error='Email Already in use'
    elif not salt:
        error='Missing salt'
    elif not phash:
        error='Missing hash'
    elif not username:
        error='Missing username'
    else:
        # If all four (email, username, salt, and hash) and username not registered
        userDB.put(email,salt + ' ' + phash ) # Make a new entry
        makeUser(email)
    return RES(R,{'error':error})

Auth = (GET,POST) # See operations.py for more info on how it's organized
