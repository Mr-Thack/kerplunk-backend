from common import RES,SIDValidity
from dblib import db

# Eventually hold email:username,fname+lname,phone#,school,classes
userData : db = db("UserData")
# UserName,LegalName
# Don't forget to change range to adjust for new length
datas = dict(zip(('uname','lname'),range(2)))


# Split by spaces
def isEmailUsed(email):
    return userData.get(email)

def makeUser(email,username):
    userData.put(email,username+' ')
    # For each field supported, a space, then -1

def getField(email,field):
    r = userData.sget(email).split(' ')[field]
    if field==datas['lname']:
        r=r.replace('_',' ')
    return r

def setField(email,field,val):
    fa = userData.sget(email).split(' ')
    fa[field] = val
    nf = ''
    for f in fa:
        nf += ' ' + f
    if field==datas['lname']:
        nf.replace(' ','_')
    return userData.put(email,nf[1:])

# The actual Handlers
def GET(D,R):
    #If the first half is altered, alter POST
    error = '' # Start with no error
    field = D.get('field')
    sid = D.get('sid')
    if not sid:
        error = 'Login! No SID/Retired SID'
    elif not field in datas:
        error = 'Not a valid Data Field'
    else:
        email = SIDValidity(sid,D['ip'])
        if email:
            return RES(R,{'val':getField(email,datas[field])})
        else:
            error = 'Email not found'
    return RES(R,{'error':error})

def POST(D,R):
    #If the first half is altered, alter GET
    #Note that for name, we'd have to do fname,lname
    error = ''
    field = D.get('field')
    sid = D.get('sid')
    val = D.get('val')
    if not sid:
        error = 'No SID'
    elif not field in datas:
        error = 'Not a valid Data Field'
    elif not val:
        error = 'No Value'
    else:
        email = SIDValidity(sid,D['ip'])
        if not email:
            error = 'SID Expired'
        elif not setField(email,datas[field],val):
            error = 'Failed To Write. Debug!'
    return RES(R,{'error':error})

Users = (GET,POST)
