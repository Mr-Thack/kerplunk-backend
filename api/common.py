import cython
import ujson as js

def NYI(D,R):
    R('403', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200'):
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return js.dumps(D)

def get(D:tuple,s:str): #Look for s in [(s,a),(b,c)] and get a
    for d in D:
        if s == d[0]:
            return d[1]
    return None

