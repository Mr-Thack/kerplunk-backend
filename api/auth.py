from common import NYI
from common import RES, get
import cython
import bcrypt
import zxcvbn # To check if the password's good
from dblib import LMDB

userDB : LMDB = LMDB("Credentials")
# Open a file called Credentials to store hash and salt and username
userCreds : cython.char[64] # Type of data, for Cython

# In DB, the credentials are stored (salt,hash)
# thus accessed with creds[0] and creds[1]

def GET(D,R): # D for Data, R for Respond
    rz : bool = False # rezult
    username = D.get('username') # Get username from Data object
    phash = D.get('hash') # Get Hash from Data Object
    if phash and username:
        userCreds = userDB.get(username) # Ask database for username
        if userCreds != None:
            # 'None' is returned when nothing is found for given index
            rz = bytes(phash,'utf-8') == userCreds.split()[1]
            # Check if the utf8 representation of given hash == stored user hash
        return RES(R,{'rz':rz}) # This is a JSON Object: 
        # {'dataField':'data','nextField':'moreData!'}
    elif username: # If only the username was given
        rs = userDB.sget(username) # Get data from username
        # It's stored as 'salt hash', with a space in between
        if not rs == None: # If not nothing found, aka we have result
            return RES(R,{'salt':rs.split(' ')[0]}) # Get the 1st part
        else:
            #TODO: give false salt to trick a hacker into thinking he got someone
            return RES(R,{'rz':rz},'402') # return error
        # TODO: make HTTP errors actually line up with the standard,
        # but it doesn't matter if we don't, bc it won't affect functionality
        # it only affects our adherence to standards
    return RES(R,{'rz':rz},'401')
    # If we're still stuck here, that means we failed, so we return 401

def POST(D,R):
    error = '' # we start with no errors
    username = D.get('username') # Get username from given Data
    salt = D.get('salt') # Get salt from given data
    phash = D.get('hash') # Get hash from given data
    if not username:
        error='Missing username'
    elif userDB.get(username):
        error='Username Taken'
    elif not salt:
        error='Missing salt'
    elif not phash:
        error='Missing hash'
    else:
        # If all three (username, salt, and hash) and username not registered
        userDB.put(username,salt + ' ' + phash ) # Make a new entry
    return RES(R,{'error':error})

Auth = (GET,POST) # See operations.py for more info on how it's organized
