import  cython
import ujson as js

def NYI(D,R):
    R('403 Forbidden', [('Content-Type','text/plain;charset=utf-8')])
    return ''

def RES(R,D='',C='200 OK'):
    R(C,[('Content-Type','text/plain;charset=utf-8')])
    return js.dumps(D)
