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
    } # ENUM for HTTP Modes
    try:
        op = operations.opFuncs[operations.opNames.index(OPERATION)][switch.get(MODE,5)]
        # op = handlerFunctions[nameOfHanderFuncUserWants][ModeOfUser]
    except:
        resp('402',[('Content-Type','text/plain;charset=utf-8')])
        return '' # Does seem to hurt to leave it like that
    return op(DATA,resp) # run the operation with given data and ability to respond

#TODO, the error codes are wrong, set them to correct HTTP error codes
#environ, respond
def run(mode,operation,data,resp):
    if data != '' or mode == 'GET': # If there's no data or on GET 
        return [send(operation,mode,data,resp).encode()]
        # return array of bytes of response
    else:
        resp('401', [('Content-Type', 'text/plain;charset=utf-8')])
        return [b'']
    # Now we only need to check for operation
    if operation is None:
        resp('400', [('Content-Type','text/plain;charset=utf-8')])
        return [b'']

