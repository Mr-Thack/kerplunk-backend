import ujson as js
import operations
import cython
import urllib.parse

switch : dict
op : tuple

def send(OPERATION: cython.char[16], MODE: cython.char[8], DATA: str, resp):
    switch = {
        'GET' : 0,
        'POST' : 1,
        'PUT' : 2,
        'DELETE' : 3
    }
    try:
        op = operations.opFuncs[operations.opNames.index(OPERATION)][switch.get(MODE,5)]
    except:
        resp('402',[('Content-Type','text/plain;charset=utf-8')])
        return [b'no']
    return op(DATA,resp)

#TODO, the error codes are wrong, set them to correct HTTP error codes
#environ, respond
def run(mode,operation,addr,data,resp):
    if data != '' or mode == 'GET':
        return [send(operation,mode,data,resp).encode()]
    else:
        resp('401', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b'']
    # Now we only need to check for operation
    if operation is None:
        resp('400', [('Content-Type','text/plain;charset=utf-8')])
        return [b'']

