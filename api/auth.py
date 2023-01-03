from common import RES, makeSID, NYI
from user_operations import make_user, is_email_used
# import zxcvbn  # To check if the password's good
from dblib import db

creds: db = db("Credentials")
# Open a file called Credentials to store hash and salt and username

"""
We use username as key for Credentials
bcz sending email over internet bad idea.
But we keep value of the username key as "email salt hash"
"""


class Auth:
    async def on_get(self, req, res):
        D = req.params
        username = D.get('username')
        thash = D.get('hash')
        error = 'Missing Username'
        # t-hash for test, k-hash for known
        if username:
            data = creds.sget(username)
            if data:
                (email, salt, khash) = data.split(' ')
                if thash == khash:
                    res.media = {'sid': makeSID(email, D['ip'])}
                else:
                    res.media = {'salt': salt}  # Get the 1st part
                    # TODO: make HTTP errors actually line up with the standard
                    # TODO: give false salt/hash to hackers
            else:
                error = 'Sign Up!'
        res.media = {'error': error}

def POST(D,R):
    error = '' # we start with no errors
    email = D.get('email')
    username = D.get('username')
    salt = D.get('salt')
    phash = D.get('hash')
    if not email:
        error='Missing email'
    elif is_email_used(email):
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
        make_user(email,username) # Set up user data
    return RES(R,{'error':error})

# Auth = (GET,POST,NYI,NYI) # See operations.py for more info on how it's organized
