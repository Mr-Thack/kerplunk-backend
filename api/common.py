import cython
import ujson as js

def NYI(D,R): #NYI: Not Yet Implemented, or also, Doesn't Exist
    # We just return 403 (I think it's the rigth err code)
    R('403', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200'): # A nice wrapper for easy respond
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return js.dumps(D) # Return this to HTTP Server

def get(D,s:str): #Look for s in [(s,a),(b,c)] and get a
    # It's a nice way to parse given data, just call get(dataArray,key)
    for d in D:
        if s == d[0]:
            return d[1]
    return None

