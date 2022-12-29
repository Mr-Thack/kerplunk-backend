from common import RES,SIDValidity,NYI
from user_operations import (set_field, valid_fields, valid_field, multi_get, multi_set)

def GET(D,R):
    #If the first half is altered, alter POST
    error = '' # Start with no error
    rfields = D.get('fields') # Could be 1, could be more
    sid = D.get('sid')
    if not sid:
        error = 'Login! No SID/Retired SID'
    elif rfields:
        fields : [str] = []
        if rfields.find(',') == -1:
            # If only 1 field requested
            if valid_field(rfields):
                fields = [rfields]
            else:
                error = 'Field not supported'
        else:
            if not valid_fields(fields):
                """
                2) Python has a fancy method of checking if a is a subset of b
                We can use <= to check if all key in rfields are a key in datas
                """
                error = 'Not Valid Data Fields'
            else:
                fields = rfields.split(',')
        if fields:
            email = SIDValidity(sid,D['ip'])
            if email:
                re = multi_get(email,fields) # init response
                return RES(R,re)
            else:
                error = 'Email not found'
        # No need for another else statement,
        # bcz the above if elses already dealt with it
    return RES(R,{'error':error})

def POST(D,R):
    #If the first half is altered, alter GET
    #Note that for name, we'd have to do fname,lname
    re = '' # response
    sid = D.get('sid')
    if not sid:
        re = 'No SID'
    else:
        email = SIDValidity(sid,D['ip'])
        if not email:
            re = 'SID Expired'
        d = {} # data to change
        for k,v in D.items():
            if valid_field(k):
                d[k] = v
        if d:
            return RES(R,{'changed':multi_set(email,d.items())})
        else:
            error = 'no field-value specified'
    return RES(R,{'error':re})

Users = (GET,POST,NYI,NYI)
