from dblib import db

# Eventually hold email:username,fname+lname,phone#,school,classes
user_data : db = db("UserData")
# UserName,LegalName
# Don't forget to change range to adjust for new length
datanames = ('uname','lname')
datas = dict(zip(datanames,range(len(datanames))))
# We don't use an enum because the data is coming from users
# And eval() could be used, but that'scould be a major vulnerability
datanames=set(datanames) # This will help with performance later

# Split by spaces
def is_email_used(email:str):
    return user_data.get(email)

def make_user(email:str,username:str):
    user_data.put(email,username+' ')
    # For each field supported, a space, then -1

def valid_field(f):
    return f in datanames
# I'm thinking of merging these 2 together & then updating users.py
def valid_fields(rf:[str]):
    return set(rf) <= datanames

def get_field(email:str,field:str):
    r = user_data.sget(email).split(' ')[datas[field]]
    if field==datas['lname']:
        r=r.replace('_',' ')
    return r

def set_field(email:str,field:str,val):
    fa = user_data.sget(email).split(' ')
    fa[datas[field]] = val
    # Set up new str
    nf = ' '.join(fa)
    if field==datas['lname']:
        nf.replace(' ','_')
    return user_data.put(email,nf)

def multi_get(email:str,fs:[str]): # Takes fields as "fs"
    r = {}
    for f in fs:
        r[f] = get_field(email,f)
    return r

def multi_set(email:str,fs:dict):
    r = ''
    for k,v in fs:
        set_field(email,k,v)
        r+=' '+k
    return r[1:] # remove first ' ' bcz it's extra

